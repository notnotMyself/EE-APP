"""
Scheduler Service - 定时任务调度服务

使用 APScheduler 实现定时触发 Agent 分析任务
"""
import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from croniter import croniter

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.briefing_service import briefing_service
from app.crud.crud_briefing import scheduled_job as scheduled_job_crud
from app.db.supabase import get_supabase_admin_client

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务调度服务"""

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self._is_running = False

    async def start(self):
        """启动调度器"""
        if self._is_running:
            logger.warning("Scheduler is already running")
            return

        # 配置 Job Store
        jobstores = {
            'default': MemoryJobStore()
        }

        # 配置调度器
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            job_defaults={
                'coalesce': True,  # 合并错过的任务
                'max_instances': 1,  # 同一任务最多1个实例
                'misfire_grace_time': 3600  # 1小时内可补执行
            },
            timezone='Asia/Shanghai'
        )

        # 从数据库加载活跃的定时任务
        await self._load_jobs_from_db()

        self.scheduler.start()
        self._is_running = True
        logger.info("✅ Scheduler service started")

    async def stop(self):
        """停止调度器"""
        if self.scheduler and self._is_running:
            self.scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("⏹️ Scheduler service stopped")

    async def _load_jobs_from_db(self):
        """从数据库加载定时任务配置"""
        try:
            supabase = get_supabase_admin_client()

            result = supabase.table('scheduled_jobs').select('*').eq(
                'is_active', True
            ).execute()

            if not result.data:
                logger.info("No active scheduled jobs found")
                return

            for job_config in result.data:
                await self.add_job_from_config(job_config)

            logger.info(f"Loaded {len(result.data)} scheduled jobs")

        except Exception as e:
            logger.error(f"Failed to load jobs from DB: {e}", exc_info=True)

    async def add_job_from_config(self, job_config: dict):
        """从配置添加定时任务"""
        job_id = job_config['id']

        try:
            # 创建触发器
            if job_config.get('schedule_type') == 'cron':
                cron_expr = job_config.get('cron_expression', '0 9 * * *')
                trigger = CronTrigger.from_crontab(
                    cron_expr,
                    timezone=job_config.get('timezone', 'Asia/Shanghai')
                )
            else:
                interval = job_config.get('interval_seconds', 3600)
                trigger = IntervalTrigger(seconds=int(interval))

            # 添加任务
            self.scheduler.add_job(
                func=self._execute_scheduled_job,
                trigger=trigger,
                id=str(job_id),
                replace_existing=True,
                kwargs={
                    'job_id': str(job_id),
                    'agent_id': job_config['agent_id'],
                    'task_prompt': job_config['task_prompt'],
                    'briefing_config': job_config.get('briefing_config', {}),
                    'target_user_ids': job_config.get('target_user_ids')
                }
            )

            # 计算并更新下次运行时间
            next_run = self._calculate_next_run(job_config)
            if next_run:
                supabase = get_supabase_admin_client()
                supabase.table('scheduled_jobs').update({
                    'next_run_at': next_run.isoformat()
                }).eq('id', job_id).execute()

            logger.info(f"Added scheduled job: {job_config.get('job_name')} ({job_id})")

        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {e}", exc_info=True)

    def _calculate_next_run(self, job_config: dict) -> Optional[datetime]:
        """计算下次运行时间"""
        try:
            if job_config.get('schedule_type') == 'cron':
                cron_expr = job_config.get('cron_expression', '0 9 * * *')
                cron = croniter(cron_expr, datetime.now())
                return cron.get_next(datetime)
            else:
                interval = job_config.get('interval_seconds', 3600)
                return datetime.now() + timedelta(seconds=int(interval))
        except Exception:
            return None

    async def _execute_scheduled_job(
        self,
        job_id: str,
        agent_id: str,
        task_prompt: str,
        briefing_config: dict,
        target_user_ids: Optional[list] = None
    ):
        """
        执行定时分析任务

        这是定时任务的核心执行函数
        """
        logger.info(f"🔄 Executing scheduled job: {job_id}")
        start_time = datetime.utcnow()

        try:
            # 创建数据库会话
            async with AsyncSessionLocal() as db:
                # 转换用户ID列表
                user_ids = None
                if target_user_ids:
                    user_ids = [UUID(uid) for uid in target_user_ids]

                # 调用简报生成服务
                result = await briefing_service.execute_and_generate_briefing(
                    db=db,
                    agent_id=UUID(agent_id),
                    task_prompt=task_prompt,
                    briefing_config=briefing_config,
                    target_user_ids=user_ids
                )

                # 更新任务执行记录
                await self._update_job_status(
                    job_id=job_id,
                    success=result.get('analysis_completed', False),
                    result=result
                )

                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info(
                    f"✅ Job {job_id} completed in {duration:.2f}s, "
                    f"briefings generated: {result.get('briefing_count', 0)}"
                )

        except Exception as e:
            logger.error(f"❌ Failed to execute job {job_id}: {e}", exc_info=True)
            await self._update_job_status(
                job_id=job_id,
                success=False,
                result={'error': str(e)}
            )

    async def _update_job_status(
        self,
        job_id: str,
        success: bool,
        result: Dict[str, Any]
    ):
        """更新任务执行状态"""
        try:
            supabase = get_supabase_admin_client()

            # 获取当前计数
            job_data = supabase.table('scheduled_jobs').select(
                'run_count, success_count, failure_count'
            ).eq('id', job_id).single().execute()

            current = job_data.data if job_data.data else {}
            run_count = int(current.get('run_count', 0)) + 1
            success_count = int(current.get('success_count', 0)) + (1 if success else 0)
            failure_count = int(current.get('failure_count', 0)) + (0 if success else 1)

            # 更新记录
            supabase.table('scheduled_jobs').update({
                'last_run_at': datetime.utcnow().isoformat(),
                'last_result': result,
                'run_count': run_count,
                'success_count': success_count,
                'failure_count': failure_count
            }).eq('id', job_id).execute()

        except Exception as e:
            logger.error(f"Failed to update job status: {e}")

    async def trigger_job_manually(
        self,
        job_id: UUID,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        手动触发任务执行

        Args:
            job_id: 任务ID
            dry_run: 是否为试运行（不实际生成简报）

        Returns:
            执行结果
        """
        try:
            supabase = get_supabase_admin_client()

            # 获取任务配置
            result = supabase.table('scheduled_jobs').select('*').eq(
                'id', str(job_id)
            ).single().execute()

            if not result.data:
                return {"error": f"Job not found: {job_id}"}

            job_config = result.data

            if dry_run:
                return {
                    "status": "dry_run",
                    "message": f"Would execute job: {job_config.get('job_name')}",
                    "config": {
                        "agent_id": job_config.get('agent_id'),
                        "task_prompt": job_config.get('task_prompt')[:200] + "...",
                        "briefing_config": job_config.get('briefing_config')
                    }
                }

            # 执行任务
            async with AsyncSessionLocal() as db:
                target_user_ids = job_config.get('target_user_ids')
                user_ids = [UUID(uid) for uid in target_user_ids] if target_user_ids else None

                exec_result = await briefing_service.execute_and_generate_briefing(
                    db=db,
                    agent_id=UUID(job_config['agent_id']),
                    task_prompt=job_config['task_prompt'],
                    briefing_config=job_config.get('briefing_config', {}),
                    target_user_ids=user_ids
                )

                # 更新执行状态
                await self._update_job_status(
                    job_id=str(job_id),
                    success=exec_result.get('analysis_completed', False),
                    result=exec_result
                )

                return {
                    "status": "executed",
                    "message": f"Job executed: {job_config.get('job_name')}",
                    "result": exec_result
                }

        except Exception as e:
            logger.error(f"Failed to trigger job manually: {e}", exc_info=True)
            return {"error": str(e)}

    def get_job_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        if not self.scheduler:
            return {"status": "not_initialized"}

        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })

        return {
            "status": "running" if self._is_running else "stopped",
            "jobs_count": len(jobs),
            "jobs": jobs
        }

    async def reload_jobs(self):
        """重新加载所有任务"""
        if self.scheduler:
            # 移除所有现有任务
            self.scheduler.remove_all_jobs()
            # 重新加载
            await self._load_jobs_from_db()
            logger.info("Jobs reloaded")


# 需要导入的额外模块
from datetime import timedelta

# 单例实例
scheduler_service = SchedulerService()
