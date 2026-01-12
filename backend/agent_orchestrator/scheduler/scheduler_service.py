"""
调度器服务 - APScheduler初始化和任务管理
"""

import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

if TYPE_CHECKING:
    from .job_executor import JobExecutor

logger = logging.getLogger(__name__)


class SchedulerService:
    """定时任务调度服务"""

    def __init__(self, supabase_client: Any = None):
        self.supabase = supabase_client
        self.scheduler: Optional[AsyncIOScheduler] = None
        self._job_executor: Optional["JobExecutor"] = None

    def initialize(self, job_executor: "JobExecutor"):
        """初始化调度器"""
        self._job_executor = job_executor

        # 配置调度器
        jobstores = {"default": MemoryJobStore()}

        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores, timezone="Asia/Shanghai"
        )

        # 将 scheduler 实例传给 job_executor，用于安排重试任务
        self._job_executor.scheduler = self.scheduler

        logger.info("Scheduler initialized")

    async def start(self):
        """启动调度器并加载任务"""
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized")

        # 从数据库加载定时任务配置
        await self._load_jobs_from_db()

        # 启动调度器
        self.scheduler.start()
        logger.info("Scheduler started")

    async def shutdown(self):
        """关闭调度器"""
        if self.scheduler:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler shutdown")

    async def _load_jobs_from_db(self):
        """从scheduled_jobs表加载任务配置"""
        if not self.supabase:
            logger.warning("Supabase not configured, skipping job loading")
            return

        try:
            result = (
                self.supabase.table("scheduled_jobs")
                .select("*")
                .eq("is_active", True)
                .execute()
            )

            for job_config in result.data:
                await self._add_job(job_config)

            logger.info(f"Loaded {len(result.data)} scheduled jobs from database")
        except Exception as e:
            logger.error(f"Failed to load scheduled jobs: {e}")

    async def _add_job(self, job_config: Dict[str, Any]):
        """添加单个定时任务"""
        job_id = str(job_config["id"])

        # 构建触发器
        if job_config["schedule_type"] == "cron":
            trigger = CronTrigger.from_crontab(
                job_config["cron_expression"],
                timezone=job_config.get("timezone", "Asia/Shanghai"),
            )
        else:
            trigger = IntervalTrigger(seconds=job_config["interval_seconds"])

        # 添加任务
        self.scheduler.add_job(
            func=self._job_executor.execute,
            trigger=trigger,
            id=job_id,
            name=job_config["job_name"],
            kwargs={
                "job_id": job_id,
                "agent_id": str(job_config["agent_id"]),
                "task_prompt": job_config["task_prompt"],
                "briefing_config": job_config.get("briefing_config", {}),
                "target_user_ids": job_config.get("target_user_ids"),
            },
            replace_existing=True,
        )

        logger.info(f"Added job: {job_config['job_name']} ({job_id})")

    async def run_job_now(self, job_id: str) -> Dict[str, Any]:
        """立即执行一次任务（用于测试）"""
        if not self.supabase:
            raise RuntimeError("Supabase not configured")

        # 从数据库获取任务配置
        result = (
            self.supabase.table("scheduled_jobs")
            .select("*")
            .eq("id", job_id)
            .single()
            .execute()
        )

        if not result.data:
            raise ValueError(f"Job not found: {job_id}")

        job_config = result.data

        # 立即执行
        return await self._job_executor.execute(
            job_id=job_id,
            agent_id=str(job_config["agent_id"]),
            task_prompt=job_config["task_prompt"],
            briefing_config=job_config.get("briefing_config", {}),
            target_user_ids=job_config.get("target_user_ids"),
        )

    def get_jobs(self):
        """获取所有调度中的任务"""
        if not self.scheduler:
            return []

        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": (
                    job.next_run_time.isoformat() if job.next_run_time else None
                ),
            }
            for job in self.scheduler.get_jobs()
        ]
