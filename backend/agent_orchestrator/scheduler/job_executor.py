"""
任务执行器 - 执行Agent分析任务并生成简报
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    from agent_sdk import AgentSDKService
    from services.briefing_service import BriefingService

logger = logging.getLogger(__name__)


class JobExecutor:
    """定时任务执行器"""

    def __init__(
        self,
        agent_service: "AgentSDKService",
        briefing_service: "BriefingService",
        supabase_client: Any = None,
    ):
        self.agent_service = agent_service
        self.briefing_service = briefing_service
        self.supabase = supabase_client

    async def execute(
        self,
        job_id: str,
        agent_id: str,
        task_prompt: str,
        briefing_config: Dict[str, Any],
        target_user_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """执行定时任务"""
        start_time = datetime.utcnow()
        logger.info(f"Executing job {job_id}")

        result = {
            "job_id": job_id,
            "status": "success",
            "start_time": start_time.isoformat(),
            "briefings_created": 0,
        }

        try:
            # 1. 获取Agent角色
            agent_role = await self._get_agent_role(agent_id)
            if not agent_role:
                raise ValueError(f"Agent not found: {agent_id}")

            # 2. 执行Agent分析
            analysis_result = await self._run_agent_analysis(
                agent_role=agent_role, task_prompt=task_prompt
            )

            result["analysis_completed"] = True

            # 3. 评估是否需要生成简报
            if briefing_config.get("enabled", True):
                briefings_count = await self._process_briefing(
                    job_id=job_id,
                    agent_id=agent_id,
                    analysis_result=analysis_result,
                    briefing_config=briefing_config,
                    target_user_ids=target_user_ids,
                )
                result["briefings_created"] = briefings_count

            # 4. 更新任务执行记录
            await self._update_job_status(
                job_id=job_id, status="success", result=result
            )

            logger.info(
                f"Job {job_id} completed successfully, "
                f"created {result['briefings_created']} briefings"
            )

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}", exc_info=True)
            result["status"] = "failed"
            result["error"] = str(e)
            await self._update_job_status(job_id=job_id, status="failed", error=str(e))

        result["end_time"] = datetime.utcnow().isoformat()
        return result

    async def _get_agent_role(self, agent_id: str) -> Optional[str]:
        """根据agent_id获取角色名"""
        if not self.supabase:
            # 如果没有数据库，假设agent_id就是role
            return agent_id

        try:
            result = (
                self.supabase.table("agents")
                .select("role")
                .eq("id", agent_id)
                .single()
                .execute()
            )
            return result.data.get("role") if result.data else None
        except Exception:
            # 回退：直接使用agent_id作为role
            return agent_id

    async def _run_agent_analysis(
        self, agent_role: str, task_prompt: str
    ) -> Dict[str, Any]:
        """运行Agent分析任务"""
        result_chunks = []

        async for event in self.agent_service.execute_query(
            prompt=task_prompt,
            agent_role=agent_role,
        ):
            if event["type"] == "text_chunk":
                result_chunks.append(event["content"])

        full_response = "".join(result_chunks)

        return {"response": full_response, "timestamp": datetime.utcnow().isoformat()}

    async def _process_briefing(
        self,
        job_id: str,
        agent_id: str,
        analysis_result: Dict[str, Any],
        briefing_config: Dict[str, Any],
        target_user_ids: Optional[List[str]],
    ) -> int:
        """处理简报生成，返回创建的简报数量"""
        # 1. 评估重要性分数
        importance_score = await self.briefing_service.evaluate_importance(
            analysis_result
        )

        min_score = briefing_config.get("min_importance_score", 0.6)

        # 2. 检查是否达到推送阈值
        if importance_score < min_score:
            logger.info(
                f"Skipping briefing: importance {importance_score:.2f} < {min_score}"
            )
            return 0

        # 3. 检查今日简报数量限制
        max_daily = briefing_config.get("max_daily_briefings", 3)
        today_count = await self.briefing_service.get_today_briefing_count(
            agent_id=agent_id
        )

        if today_count >= max_daily:
            logger.info(
                f"Skipping briefing: daily limit reached ({today_count}/{max_daily})"
            )
            return 0

        # 4. 获取目标用户
        users = await self._get_target_users(agent_id, target_user_ids)

        if not users:
            logger.warning("No target users found for briefing")
            return 0

        # 5. 获取Agent角色用于查找reports目录
        agent_role = await self._get_agent_role(agent_id)

        # 6. 为每个用户生成简报（包含artifact）
        created_count = 0
        for user_id in users:
            try:
                # 创建artifact存储完整报告
                artifact_id = await self._create_artifact(
                    agent_id=agent_id,
                    user_id=user_id,
                    agent_role=agent_role,
                    analysis_result=analysis_result,
                )

                # 创建briefing并关联artifact
                await self.briefing_service.create_briefing(
                    agent_id=agent_id,
                    user_id=user_id,
                    analysis_result=analysis_result,
                    importance_score=importance_score,
                    job_id=job_id,
                    report_artifact_id=artifact_id,
                )
                created_count += 1
            except Exception as e:
                logger.error(f"Failed to create briefing for user {user_id}: {e}")

        return created_count

    async def _create_artifact(
        self,
        agent_id: str,
        user_id: str,
        agent_role: str,
        analysis_result: Dict[str, Any],
    ) -> Optional[str]:
        """
        创建报告artifact，返回artifact_id

        优先检查Agent工作目录下的reports/目录是否有新生成的md文件，
        如果没有，则使用analysis_result.response作为报告内容。
        """
        if not self.supabase:
            logger.warning("Supabase not configured, artifact not created")
            return None

        report_content = analysis_result.get("response", "")
        report_title = "分析报告"

        # 尝试从Agent工作目录读取最新的报告文件
        if agent_role:
            reports_dir = self._get_agent_reports_dir(agent_role)
            if reports_dir and reports_dir.exists():
                latest_report = self._find_latest_report(reports_dir)
                if latest_report:
                    try:
                        report_content = latest_report.read_text(encoding="utf-8")
                        report_title = latest_report.stem.replace("_", " ").title()
                        logger.info(f"Using report file: {latest_report}")
                    except Exception as e:
                        logger.warning(f"Failed to read report file: {e}")

        # 从响应中提取标题
        if report_content:
            lines = report_content.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("#"):
                    report_title = line.lstrip("#").strip()[:100]
                    break

        artifact_id = str(uuid4())
        artifact = {
            "id": artifact_id,
            "user_id": user_id,
            "type": "report",
            "title": report_title,
            "content": report_content,
            "format": "markdown",
            "metadata": {
                "agent_id": agent_id,
                "generated_at": datetime.utcnow().isoformat(),
            },
            "created_at": datetime.utcnow().isoformat(),
        }

        try:
            self.supabase.table("artifacts").insert(artifact).execute()
            logger.info(f"Created artifact {artifact_id} for user {user_id}")
            return artifact_id
        except Exception as e:
            logger.error(f"Failed to create artifact: {e}")
            return None

    def _get_agent_reports_dir(self, agent_role: str) -> Optional[Path]:
        """获取Agent的reports目录路径"""
        # 基于当前文件位置推断agents目录
        current_dir = Path(__file__).parent.parent.parent  # backend/
        agents_dir = current_dir / "agents" / agent_role / "reports"
        return agents_dir if agents_dir.exists() else None

    def _find_latest_report(self, reports_dir: Path) -> Optional[Path]:
        """查找最新的报告文件（最近1小时内修改的）"""
        md_files = list(reports_dir.glob("*.md"))
        if not md_files:
            return None

        # 按修改时间排序，取最新的
        md_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        latest = md_files[0]

        # 检查是否是最近1小时内生成的
        mtime = datetime.fromtimestamp(latest.stat().st_mtime)
        if (datetime.now() - mtime).total_seconds() < 3600:
            return latest

        return None

    async def _get_target_users(
        self, agent_id: str, target_user_ids: Optional[List[str]]
    ) -> List[str]:
        """获取目标用户列表"""
        if target_user_ids:
            return target_user_ids

        if not self.supabase:
            return []

        # 获取订阅该Agent的所有用户
        try:
            result = (
                self.supabase.table("user_agents")
                .select("user_id")
                .eq("agent_id", agent_id)
                .eq("is_subscribed", True)
                .execute()
            )
            return [row["user_id"] for row in result.data]
        except Exception as e:
            logger.error(f"Failed to get target users: {e}")
            return []

    async def _update_job_status(
        self,
        job_id: str,
        status: str,
        result: Dict[str, Any] = None,
        error: str = None,
    ):
        """更新任务执行状态"""
        if not self.supabase:
            return

        try:
            update_data = {
                "last_run_at": datetime.utcnow().isoformat(),
                "last_result": {"status": status, "result": result, "error": error},
            }

            # 更新计数器
            if status == "success":
                # 使用原生SQL增加计数
                self.supabase.rpc(
                    "increment_job_counter",
                    {"job_id": job_id, "counter_name": "success_count"},
                ).execute()
            else:
                self.supabase.rpc(
                    "increment_job_counter",
                    {"job_id": job_id, "counter_name": "failure_count"},
                ).execute()

            self.supabase.table("scheduled_jobs").update(update_data).eq(
                "id", job_id
            ).execute()

        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
