"""
Conversation Service - 对话服务

核心职责：
1. 管理持久化对话（每用户-Agent对一个对话）
2. 将简报添加为对话中的卡片消息
3. 处理用户消息并流式返回AI响应
4. 构建包含简报卡片的对话上下文
"""

import logging
import json
from typing import Any, AsyncGenerator, Dict, List, Optional
from datetime import datetime

from models import ConversationModel, MessageModel

logger = logging.getLogger(__name__)


class ConversationService:
    """对话服务 - 支持共享对话模式"""

    def __init__(
        self,
        supabase_client: Any,
        agent_manager: Any,
        briefing_service: Optional[Any] = None,
    ):
        """初始化对话服务

        Args:
            supabase_client: Supabase客户端实例
            agent_manager: AgentManager实例（用于调用Claude Agent SDK）
            briefing_service: BriefingService实例（可选，用于获取简报详情）
        """
        self.conversation_model = ConversationModel(supabase_client)
        self.message_model = MessageModel(supabase_client)
        self.agent_manager = agent_manager
        self.briefing_service = briefing_service
        self.supabase = supabase_client

    def set_briefing_service(self, briefing_service: Any) -> None:
        """设置BriefingService（解决循环依赖）

        Args:
            briefing_service: BriefingService实例
        """
        self.briefing_service = briefing_service

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
        """发送消息并流式返回AI回复

        工作流程：
        1. 保存用户消息
        2. 获取对话上下文（包括简报卡片）
        3. 构建AI prompt
        4. 流式调用Agent SDK
        5. 保存AI回复
        6. 更新对话时间戳

        Args:
            conversation_id: 对话UUID
            user_message: 用户消息内容
            user_id: 用户UUID（用于权限检查）

        Yields:
            AI响应的文本块（流式）

        Raises:
            ValueError: 对话不存在或用户无权访问时
            Exception: AI调用失败或数据库操作失败时
        """
        try:
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

            # 2. 获取对话上下文（最近20条消息）
            messages = await self.message_model.get_recent_messages(
                conversation_id, count=20
            )

            # 3. 构建包含简报的上下文提示词
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
            agent_role = conversation["agent_id"]

            # Agent SDK Service 使用 execute_query 方法
            async for event in self.agent_manager.execute_query(
                prompt=full_prompt,
                agent_role=agent_role,
            ):
                # 只处理 text_chunk 类型的事件
                if event.get("type") == "text_chunk":
                    chunk = event.get("content", "")
                    assistant_content += chunk
                    yield chunk

            # 5. 保存AI回复
            await self.message_model.create_text_message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_content,
            )

            # 6. 更新对话时间戳
            await self.conversation_model.update_last_message_time(conversation_id)

            logger.info(
                f"Completed message exchange in conversation {conversation_id}, "
                f"assistant response length: {len(assistant_content)}"
            )

        except Exception as e:
            logger.error(
                f"Error in send_message for conversation {conversation_id}: {e}"
            )
            raise

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
