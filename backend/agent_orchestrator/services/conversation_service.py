"""
Conversation Service - 对话服务

核心职责：
1. 管理持久化对话（每用户-Agent对一个对话）
2. 将简报添加为对话中的卡片消息
3. 处理用户消息并流式返回AI响应
4. 构建包含简报卡片的对话上下文

优化（v2）：
- Agent role 缓存减少数据库查询
- 并行化 IO 操作减少 TTFT
- 增强超时控制
"""

import asyncio
import logging
import json
from typing import Any, AsyncGenerator, Dict, List, Optional
from datetime import datetime

from models import ConversationModel, MessageModel
from services.task_intent_recognizer import TaskIntentRecognizer
from agent_registry import get_global_registry

logger = logging.getLogger(__name__)


class ConversationService:
    """对话服务 - 支持共享对话模式（优化版）"""

    # 配置常量
    CONVERSATION_TIMEOUT = 180  # 对话总超时 3 分钟
    API_CALL_TIMEOUT = 120      # 单次 API 调用 2 分钟
    MAX_CONTEXT_MESSAGES = 20   # 上下文消息数量

    def __init__(
        self,
        supabase_client: Any,
        agent_service: Any,
        briefing_service: Optional[Any] = None,
    ):
        """初始化对话服务

        Args:
            supabase_client: Supabase客户端实例
            agent_service: AgentSDKService实例（用于调用Claude Agent SDK）
            briefing_service: BriefingService实例（可选，用于获取简报详情）
        """
        self.conversation_model = ConversationModel(supabase_client)
        self.message_model = MessageModel(supabase_client)
        self.agent_service = agent_service
        self.briefing_service = briefing_service
        self.supabase = supabase_client

        # 任务相关组件（Phase 1新增）
        self.task_recognizer = TaskIntentRecognizer()
        self.task_executor = None  # 从main.py延迟注入，避免循环依赖

        # 优化：Agent role 缓存（减少数据库查询）
        self._agent_role_cache: Dict[str, str] = {}

    def set_briefing_service(self, briefing_service: Any) -> None:
        """设置BriefingService（解决循环依赖）

        Args:
            briefing_service: BriefingService实例
        """
        self.briefing_service = briefing_service

    def set_task_executor(self, task_executor: Any) -> None:
        """设置TaskExecutionService（解决循环依赖）

        Args:
            task_executor: TaskExecutionService实例
        """
        self.task_executor = task_executor

    def _get_agent_role(self, agent_id: str) -> str:
        """获取 Agent 的 role string（带缓存优化）

        优化：三级缓存策略
        1. 实例级缓存（内存）
        2. AgentRegistry（内存）
        3. 数据库查询（缓存结果）

        Args:
            agent_id: Agent 的 UUID 或 role string

        Returns:
            Agent 的 role string

        Raises:
            ValueError: 如果 agent 不存在
        """
        # 1. 检查实例缓存
        if agent_id in self._agent_role_cache:
            return self._agent_role_cache[agent_id]

        # 使用 agent_registry 的动态映射
        registry = get_global_registry()

        # 2. 尝试通过 UUID 获取 role
        role = registry.get_agent_id(agent_id)
        if role:
            self._agent_role_cache[agent_id] = role
            return role

        # 如果 agent_id 已经是 role，检查是否存在
        if registry.exists(agent_id):
            self._agent_role_cache[agent_id] = agent_id
            return agent_id

        # 3. Fallback: 从数据库查询 agent 的 role（并缓存结果）
        try:
            result = (
                self.supabase.table("agents")
                .select("role")
                .eq("id", agent_id)
                .execute()
            )
            if result.data and len(result.data) > 0:
                db_role = result.data[0].get("role")
                if db_role and registry.exists(db_role):
                    logger.info(
                        f"Found agent role '{db_role}' from database for UUID '{agent_id}'"
                    )
                    self._agent_role_cache[agent_id] = db_role
                    return db_role
        except Exception as e:
            logger.warning(f"Failed to query agent from database: {e}")

        # 未找到 agent
        logger.error(
            f"Agent '{agent_id}' not found in registry or database. "
            f"Available agents: {registry.get_all_ids()}"
        )
        raise ValueError(f"Agent '{agent_id}' not found")

    async def get_or_create_conversation(
        self, user_id: str, agent_id: str
    ) -> str:
        """获取或创建对话（核心方法）

        实现"一个用户-Agent对一个对话"模式。

        Args:
            user_id: 用户UUID
            agent_id: Agent UUID

        Returns:
            对话UUID (conversation_id)

        Raises:
            Exception: 数据库操作失败时
        """
        conversation = await self.conversation_model.get_or_create(
            user_id, agent_id
        )
        return conversation["id"]

    async def add_briefing_to_conversation(
        self, briefing_id: str, user_id: str, agent_id: str
    ) -> str:
        """将简报添加到对话中（核心新增功能）

        工作流程：
        1. 获取或创建对话
        2. 获取简报详情
        3. 在对话中插入简报卡片消息
        4. 更新对话时间戳

        Args:
            briefing_id: 简报UUID
            user_id: 用户UUID
            agent_id: Agent UUID

        Returns:
            对话UUID (conversation_id)

        Raises:
            ValueError: 简报不存在或数据无效时
            Exception: 数据库操作失败时
        """
        try:
            # 1. 获取或创建对话
            conversation_id = await self.get_or_create_conversation(
                user_id, agent_id
            )

            # 2. 获取简报详情
            if self.briefing_service:
                briefing = await self.briefing_service.get_briefing(briefing_id)
            else:
                # Fallback: 直接从数据库查询
                result = (
                    self.supabase.table("briefings")
                    .select("*")
                    .eq("id", briefing_id)
                    .execute()
                )
                if not result.data or len(result.data) == 0:
                    raise ValueError(f"Briefing not found: {briefing_id}")
                briefing = result.data[0]

            if not briefing:
                raise ValueError(f"Briefing not found: {briefing_id}")

            # 3. 在对话中插入简报卡片
            await self.message_model.create_briefing_card(
                conversation_id=conversation_id,
                briefing_id=briefing_id,
                briefing_data={
                    "title": briefing["title"],
                    "summary": briefing["summary"],
                    "priority": briefing["priority"],
                    "briefing_type": briefing.get("briefing_type", "insight"),
                    "impact": briefing.get("impact", ""),
                    "created_at": briefing.get(
                        "created_at", datetime.utcnow().isoformat()
                    ),
                },
            )

            # 4. 更新对话时间戳
            await self.conversation_model.update_last_message_time(conversation_id)

            logger.info(
                f"Added briefing {briefing_id} to conversation {conversation_id} "
                f"(user={user_id}, agent={agent_id})"
            )

            return conversation_id

        except Exception as e:
            logger.error(
                f"Error adding briefing {briefing_id} to conversation: {e}"
            )
            raise

    async def send_message(
        self, conversation_id: str, user_message: str, user_id: str
    ) -> AsyncGenerator[str, None]:
        """发送消息并流式返回AI回复（增强支持任务执行）

        优化：
        - 增加分层超时控制
        - 友好的错误提示

        工作流程：
        1. 保存用户消息
        2. 任务意图识别
        3a. 如果是任务：执行任务→生成简报→AI总结
        3b. 如果不是任务：获取上下文→AI回复
        4. 保存AI回复
        5. 更新对话时间戳

        Args:
            conversation_id: 对话UUID
            user_message: 用户消息内容
            user_id: 用户UUID（用于权限检查）

        Yields:
            AI响应的文本块（流式）或任务事件（JSON）

        Raises:
            ValueError: 对话不存在或用户无权访问时
            Exception: AI调用失败或数据库操作失败时
        """
        try:
            # 增强超时控制
            async with asyncio.timeout(self.CONVERSATION_TIMEOUT):
                # 0. 验证对话存在且用户有权访问
                conversation = await self.conversation_model.get_by_id(conversation_id)
                if not conversation:
                    raise ValueError(f"Conversation not found: {conversation_id}")

                if conversation["user_id"] != user_id:
                    raise ValueError(
                        f"User {user_id} does not have access to conversation {conversation_id}"
                    )

                # 1. 保存用户消息
                await self.message_model.create_text_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=user_message,
                )

                # 2. 任务意图识别（Phase 1 新增）
                task_intent = None
                if self.task_recognizer:
                    task_intent = await self.task_recognizer.recognize(
                        user_message, conversation_context={"agent_id": conversation["agent_id"]}
                    )

                # 3. 根据是否为任务选择执行流程
                if task_intent and self.task_executor:
                    # 3a. 执行任务并流式输出
                    logger.info(f"Task recognized: {task_intent.task_type}")
                    async for event in self._execute_task_and_generate_briefing(
                        conversation=conversation,
                        task_intent=task_intent,
                        user_id=user_id,
                    ):
                        yield event
                else:
                    # 3b. 原有对话流程
                    async for chunk in self._normal_chat_flow(
                        conversation=conversation, user_message=user_message
                    ):
                        yield chunk

        except asyncio.TimeoutError:
            logger.error(f"Conversation timeout after {self.CONVERSATION_TIMEOUT}s")
            yield json.dumps({
                "type": "error",
                "error": f"对话处理超时（{self.CONVERSATION_TIMEOUT}秒），请稍后重试"
            })
        except Exception as e:
            logger.error(f"Error in send_message: {e}", exc_info=True)
            # 返回错误给用户
            yield json.dumps({
                "type": "error",
                "error": "消息处理失败，请稍后重试"
            })

    async def _execute_task_and_generate_briefing(
        self, conversation: Dict, task_intent: Any, user_id: str
    ) -> AsyncGenerator[str, None]:
        """执行任务并生成简报（Phase 1 新增方法）

        Args:
            conversation: 对话记录
            task_intent: 任务意图对象
            user_id: 用户ID

        Yields:
            任务执行事件（JSON格式）和AI总结
        """
        # 🔧 获取 Agent Role (从 UUID 转换)
        agent_role = self._get_agent_role(conversation["agent_id"])

        # 1. 任务开始事件
        yield json.dumps({
            "type": "task_start",
            "task_type": task_intent.task_type,
            "status": "executing"
        })

        # 2. 执行任务
        try:
            result = await self.task_executor.execute_ad_hoc_task(
                agent_role=agent_role,  # 使用 role string
                task_prompt=task_intent.task_prompt,
                user_id=user_id,
                conversation_id=conversation["id"],
            )

            # 3. 简报创建事件
            if result.get("briefing"):
                yield json.dumps({
                    "type": "briefing_created",
                    "briefing_id": result["briefing"]["id"],
                    "title": result["briefing"]["title"],
                    "priority": result["briefing"].get("priority", "P2")
                })
                briefing_title = result["briefing"]["title"]
            else:
                # 没有生成简报（重要性不足）
                yield json.dumps({
                    "type": "task_complete",
                    "briefing_created": False,
                    "reason": "importance_too_low"
                })
                briefing_title = None

            # 4. AI总结回复
            if briefing_title:
                summary_prompt = f"""
任务已完成。简报标题：{briefing_title}

请给用户一个友好的总结（1-2句话），告诉他们分析结果已经生成。
"""
            else:
                summary_prompt = """
任务已完成，分析结果显示一切正常，暂无需要特别关注的问题。

请给用户一个友好的回复（1-2句话）。
"""

            assistant_content = ""
            async for event in self.agent_service.execute_query(
                prompt=summary_prompt,
                agent_role=agent_role,  # 使用 role string
            ):
                if event.get("type") == "text_chunk":
                    chunk = event.get("content", "")
                    assistant_content += chunk
                    yield json.dumps({
                        "type": "text_chunk",
                        "content": chunk
                    })

            # 5. 保存AI回复
            await self.message_model.create_text_message(
                conversation_id=conversation["id"],
                role="assistant",
                content=assistant_content,
            )

            # 6. 更新对话时间戳
            await self.conversation_model.update_last_message_time(conversation["id"])

        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            yield json.dumps({
                "type": "task_error",
                "error": "任务执行失败，请稍后重试"
            })

    async def _normal_chat_flow(
        self, conversation: Dict, user_message: str
    ) -> AsyncGenerator[str, None]:
        """原有对话流程（Phase 1 提取为独立方法）

        优化：并行化 IO 操作减少 TTFT

        Args:
            conversation: 对话记录
            user_message: 用户消息

        Yields:
            AI响应的文本块
        """
        # 优化：并行执行多个 IO 操作
        # 1. Agent role 查询（已缓存）
        # 2. 历史消息查询
        agent_role_task = asyncio.create_task(
            asyncio.to_thread(self._get_agent_role, conversation["agent_id"])
        )
        messages_task = asyncio.create_task(
            self.message_model.get_recent_messages(
                conversation["id"], count=self.MAX_CONTEXT_MESSAGES
            )
        )

        # 等待所有任务完成
        agent_role, messages = await asyncio.gather(agent_role_task, messages_task)

        # 3. 构建包含简报的上下文提示词（CPU 密集型，保持同步）
        context_prompt = self._build_context_with_briefings(
            conversation, messages
        )

        # 组合用户消息
        full_prompt = (
            f"{context_prompt}\n\n"
            f"用户最新消息: {user_message}\n\n"
            f"请根据对话历史和简报信息回答用户的问题。"
        )

        # 4. 流式生成回复（使用Agent SDK Service）
        assistant_content = ""

        # Agent SDK Service 使用 execute_query 方法
        async for event in self.agent_service.execute_query(
            prompt=full_prompt,
            agent_role=agent_role,  # 使用 role string
        ):
            # 只处理 text_chunk 类型的事件
            if event.get("type") == "text_chunk":
                chunk = event.get("content", "")
                assistant_content += chunk
                yield chunk

        # 5. 保存AI回复
        await self.message_model.create_text_message(
            conversation_id=conversation["id"],
            role="assistant",
            content=assistant_content,
        )

        # 6. 更新对话时间戳
        await self.conversation_model.update_last_message_time(conversation["id"])

        logger.info(
            f"Completed message exchange in conversation {conversation['id']}, "
            f"assistant response length: {len(assistant_content)}"
        )

    def _build_context_with_briefings(
        self, conversation: Dict[str, Any], messages: List[Dict[str, Any]]
    ) -> str:
        """构建包含简报的上下文（核心改进）

        将简报卡片和文本消息组合成结构化提示词，供AI理解对话背景。

        Args:
            conversation: 对话记录
            messages: 消息列表（按时间顺序）

        Returns:
            格式化的上下文提示词
        """
        prompt = "你是一个AI助手，正在与用户进行长期对话。\n\n"
        prompt += "**对话历史**（包含简报和讨论）：\n\n"

        for msg in messages:
            if msg["content_type"] == "briefing_card":
                # 简报卡片展示为结构化信息
                try:
                    briefing = json.loads(msg["content"])
                    prompt += f"[简报 {briefing.get('created_at', 'N/A')}]\n"
                    prompt += f"标题：{briefing.get('title', 'N/A')}\n"
                    prompt += f"摘要：{briefing.get('summary', 'N/A')}\n"
                    prompt += f"优先级：{briefing.get('priority', 'N/A')}\n"
                    if briefing.get("impact"):
                        prompt += f"影响：{briefing['impact']}\n"
                    prompt += "\n"
                except json.JSONDecodeError:
                    # 如果JSON解析失败，跳过这条简报
                    logger.warning(
                        f"Failed to parse briefing_card content: {msg['content']}"
                    )
                    continue

            elif msg["content_type"] == "text":
                # 普通对话
                role_label = {"user": "用户", "assistant": "助手", "system": "系统"}.get(
                    msg["role"], msg["role"]
                )
                prompt += f"{role_label}: {msg['content']}\n\n"

        return prompt

    async def get_conversation_by_agent(
        self, user_id: str, agent_id: str
    ) -> Optional[Dict[str, Any]]:
        """根据user_id和agent_id获取对话

        Args:
            user_id: 用户UUID
            agent_id: Agent UUID

        Returns:
            对话记录，如果不存在返回None
        """
        try:
            result = (
                self.supabase.table("conversations")
                .select("*")
                .eq("user_id", user_id)
                .eq("agent_id", agent_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]
            return None

        except Exception as e:
            logger.error(
                f"Error getting conversation for user={user_id}, agent={agent_id}: {e}"
            )
            return None

    async def list_user_conversations(
        self, user_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取用户的所有对话

        Args:
            user_id: 用户UUID
            limit: 返回数量限制

        Returns:
            对话列表
        """
        return await self.conversation_model.list_by_user(user_id, limit)
