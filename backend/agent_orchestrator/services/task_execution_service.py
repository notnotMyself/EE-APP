"""
任务执行服务 - Task Execution Service

封装对话触发任务的执行逻辑，复用现有的简报生成系统。
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskExecutionService:
    """对话触发任务的执行封装

    核心职责：
    1. 执行Agent分析任务
    2. 评估重要性
    3. 生成简报（如果重要性足够）
    4. 将简报添加到对话中
    """

    def __init__(
        self,
        agent_service,  # AgentSDKService
        briefing_service,  # BriefingService
        importance_evaluator,  # ImportanceEvaluator
        supabase_client,  # Supabase Client
    ):
        """初始化任务执行服务

        Args:
            agent_service: Agent SDK服务实例
            briefing_service: 简报服务实例
            importance_evaluator: 重要性评估器实例
            supabase_client: Supabase客户端
        """
        self.agent_service = agent_service
        self.briefing_service = briefing_service
        self.evaluator = importance_evaluator
        self.supabase = supabase_client
        self.conversation_service = None  # 延迟注入，避免循环依赖

    def set_conversation_service(self, conversation_service):
        """设置conversation服务（解决循环依赖）

        Args:
            conversation_service: ConversationService实例
        """
        self.conversation_service = conversation_service

    async def execute_ad_hoc_task(
        self,
        agent_role: str,
        task_prompt: str,
        user_id: str,
        conversation_id: str,
    ) -> Dict[str, Any]:
        """执行即时任务并生成简报

        Args:
            agent_role: Agent角色ID
            task_prompt: 任务提示词
            user_id: 用户ID
            conversation_id: 对话ID

        Returns:
            执行结果字典，包含analysis_result、importance_score、briefing
        """
        logger.info(
            f"Executing ad-hoc task for user={user_id}, "
            f"agent={agent_role}, conversation={conversation_id}"
        )

        try:
            # 1. 执行Agent分析（流式获取结果）
            logger.info("Step 1: Executing agent analysis...")
            analysis_text = ""
            async for event in self.agent_service.execute_query(
                prompt=task_prompt, agent_role=agent_role
            ):
                if event.get("type") == "text_chunk":
                    analysis_text += event.get("content", "")

            if not analysis_text:
                logger.warning("Agent analysis returned empty result")
                return {
                    "analysis_result": "",
                    "importance_score": 0.0,
                    "briefing": None,
                    "error": "分析结果为空",
                }

            logger.info(
                f"Agent analysis completed, length: {len(analysis_text)} chars"
            )

            # 2. 评估重要性
            logger.info("Step 2: Evaluating importance...")
            score = await self.evaluator.evaluate(analysis_text)
            logger.info(f"Importance score: {score}")

            # 3. 如果重要性足够，创建简报
            briefing = None
            if score >= 0.6:
                logger.info("Step 3: Creating briefing (score >= 0.6)...")
                briefing = await self._create_briefing_from_task(
                    analysis_text=analysis_text,
                    agent_role=agent_role,
                    user_id=user_id,
                    conversation_id=conversation_id,
                )

                if briefing:
                    logger.info(f"Briefing created successfully: {briefing['id']}")
                else:
                    logger.warning("Failed to create briefing")
            else:
                logger.info(
                    f"Skipping briefing creation (score {score} < 0.6 threshold)"
                )

            return {
                "analysis_result": analysis_text,
                "importance_score": score,
                "briefing": briefing,
            }

        except Exception as e:
            logger.error(f"Error executing ad-hoc task: {e}", exc_info=True)
            return {
                "analysis_result": "",
                "importance_score": 0.0,
                "briefing": None,
                "error": str(e),
            }

    async def _create_briefing_from_task(
        self,
        analysis_text: str,
        agent_role: str,
        user_id: str,
        conversation_id: str,
    ) -> Optional[Dict]:
        """从任务结果创建简报

        复用 BriefingService.create_briefing() 逻辑。

        Args:
            analysis_text: Agent分析结果
            agent_role: Agent角色ID
            user_id: 用户ID
            conversation_id: 对话ID

        Returns:
            创建的简报对象，如果失败返回None
        """
        try:
            # 构建context_data，标识来源为conversation
            context_data = {
                "trigger_source": "conversation",
                "conversation_id": conversation_id,
                "created_at": datetime.utcnow().isoformat(),
            }

            # 调用 BriefingService 创建简报
            briefing = await self.briefing_service.create_briefing(
                agent_id=agent_role,
                user_id=user_id,
                analysis_result=analysis_text,
                context_data=context_data,
            )

            if not briefing:
                logger.warning("BriefingService.create_briefing returned None")
                return None

            logger.info(f"Briefing created: {briefing['id']}")

            # 将简报添加到对话
            if self.conversation_service:
                try:
                    await self.conversation_service.add_briefing_to_conversation(
                        briefing_id=briefing["id"],
                        user_id=user_id,
                        agent_id=agent_role,
                    )
                    logger.info(
                        f"Briefing {briefing['id']} added to conversation {conversation_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to add briefing to conversation: {e}", exc_info=True
                    )
                    # 不影响简报创建结果
            else:
                logger.warning(
                    "conversation_service not set, skipping add to conversation"
                )

            return briefing

        except Exception as e:
            logger.error(f"Error creating briefing from task: {e}", exc_info=True)
            return None

    async def create_user_scheduled_job(
        self,
        agent_id: str,
        user_id: str,
        schedule_config: Dict[str, Any],
        task_prompt: str,
        conversation_id: str,
    ) -> Dict[str, Any]:
        """创建用户自定义定时任务

        Args:
            agent_id: Agent角色ID
            user_id: 用户ID
            schedule_config: 调度配置（频率、时间等）
            task_prompt: 任务提示词
            conversation_id: 对话ID

        Returns:
            创建的任务记录
        """
        import time

        logger.info(
            f"Creating user scheduled job for user={user_id}, agent={agent_id}"
        )

        try:
            # 生成cron表达式
            cron_expression = self._generate_cron_expression(schedule_config)

            # 构建任务数据
            job_data = {
                "agent_id": agent_id,
                "job_name": f"user_task_{user_id}_{int(time.time())}",
                "job_type": "user_scheduled",
                "schedule_type": "cron",
                "cron_expression": cron_expression,
                "task_prompt": task_prompt,
                "target_user_ids": [user_id],
                "metadata": {
                    "created_from": "conversation",
                    "conversation_id": conversation_id,
                    "schedule_config": schedule_config,
                },
                "enabled": True,
            }

            # 插入数据库
            result = self.supabase.table("scheduled_jobs").insert(job_data).execute()

            if result.data and len(result.data) > 0:
                logger.info(f"Scheduled job created: {result.data[0]['id']}")
                return result.data[0]
            else:
                logger.error("Failed to create scheduled job: no data returned")
                return None

        except Exception as e:
            logger.error(f"Error creating scheduled job: {e}", exc_info=True)
            raise

    def _generate_cron_expression(self, schedule_config: Dict[str, Any]) -> str:
        """生成cron表达式

        Args:
            schedule_config: 调度配置

        Returns:
            cron表达式字符串
        """
        frequency = schedule_config.get("frequency", "daily")
        time_str = schedule_config.get("time", "09:00")

        # 解析时间
        hour, minute = map(int, time_str.split(":"))

        if frequency == "daily":
            # 每天
            return f"{minute} {hour} * * *"

        elif frequency == "weekly":
            # 每周
            weekday = schedule_config.get("weekday", 1)  # 默认周一
            return f"{minute} {hour} * * {weekday}"

        elif frequency == "monthly":
            # 每月
            day_of_month = schedule_config.get("day_of_month", 1)  # 默认1号
            return f"{minute} {hour} {day_of_month} * *"

        else:
            # 默认每天
            logger.warning(f"Unknown frequency: {frequency}, using daily")
            return f"{minute} {hour} * * *"
