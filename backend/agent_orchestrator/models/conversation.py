"""
Conversation data model - 对话数据模型

实现"每用户-Agent对一个对话"的持久化模式
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationModel:
    """对话数据模型

    核心功能：
    - get_or_create: 获取或创建对话（幂等操作）
    - 确保每个(user_id, agent_id)对只有一个对话
    """

    def __init__(self, supabase_client: Any):
        """初始化对话模型

        Args:
            supabase_client: Supabase客户端实例
        """
        self.supabase = supabase_client

    async def get_or_create(
        self, user_id: str, agent_id: str
    ) -> Dict[str, Any]:
        """获取或创建对话（核心方法）

        实现get-or-create模式：
        1. 先查询是否存在 (user_id, agent_id) 对应的对话
        2. 如果存在，直接返回
        3. 如果不存在，创建新对话并返回

        Args:
            user_id: 用户UUID
            agent_id: Agent UUID

        Returns:
            对话记录字典，包含: id, user_id, agent_id, title, started_at, etc.

        Raises:
            Exception: 数据库操作失败时
        """
        try:
            # 1. 查找现有对话
            result = (
                self.supabase.table("conversations")
                .select("*")
                .eq("user_id", user_id)
                .eq("agent_id", agent_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                # 已有对话，直接返回
                conversation = result.data[0]
                logger.info(
                    f"Reusing existing conversation: {conversation['id']} "
                    f"for user={user_id}, agent={agent_id}"
                )
                return conversation

            # 2. 创建新对话
            # 获取agent名称用于生成标题
            agent_result = (
                self.supabase.table("agents")
                .select("name")
                .eq("id", agent_id)
                .execute()
            )
            agent_name = (
                agent_result.data[0]["name"] if agent_result.data else "AI员工"
            )

            conversation_data = {
                "user_id": user_id,
                "agent_id": agent_id,
                "title": f"与 {agent_name} 的对话",
                "status": "active",
                "started_at": datetime.utcnow().isoformat(),
                "last_message_at": datetime.utcnow().isoformat(),
            }

            result = (
                self.supabase.table("conversations")
                .insert(conversation_data)
                .execute()
            )

            if not result.data or len(result.data) == 0:
                raise Exception("Failed to create conversation: no data returned")

            conversation = result.data[0]
            logger.info(
                f"Created new conversation: {conversation['id']} "
                f"for user={user_id}, agent={agent_id}"
            )
            return conversation

        except Exception as e:
            logger.error(
                f"Error in get_or_create conversation "
                f"(user={user_id}, agent={agent_id}): {e}"
            )
            raise

    async def get_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取对话

        Args:
            conversation_id: 对话UUID

        Returns:
            对话记录字典，如果不存在返回None
        """
        try:
            result = (
                self.supabase.table("conversations")
                .select("*")
                .eq("id", conversation_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {e}")
            return None

    async def update_last_message_time(self, conversation_id: str) -> None:
        """更新对话的最后消息时间戳

        Args:
            conversation_id: 对话UUID
        """
        try:
            self.supabase.table("conversations").update(
                {"last_message_at": datetime.utcnow().isoformat()}
            ).eq("id", conversation_id).execute()

            logger.debug(f"Updated last_message_at for conversation {conversation_id}")

        except Exception as e:
            logger.error(
                f"Error updating last_message_at for conversation {conversation_id}: {e}"
            )
            # Non-critical error, don't raise

    async def list_by_user(
        self, user_id: str, limit: int = 20
    ) -> list[Dict[str, Any]]:
        """获取用户的所有对话

        Args:
            user_id: 用户UUID
            limit: 返回数量限制

        Returns:
            对话列表，按last_message_at降序排列
        """
        try:
            result = (
                self.supabase.table("conversations")
                .select("*")
                .eq("user_id", user_id)
                .order("last_message_at", desc=True)
                .limit(limit)
                .execute()
            )

            return result.data or []

        except Exception as e:
            logger.error(f"Error listing conversations for user {user_id}: {e}")
            return []

    async def create_conversation(
        self, user_id: str, agent_id: str, title: Optional[str] = None
    ) -> str:
        """创建新会话（多会话模式）

        不检查 UNIQUE(user_id, agent_id) 约束，直接创建新会话

        Args:
            user_id: 用户UUID
            agent_id: Agent UUID
            title: 会话标题（可选，默认生成）

        Returns:
            新创建的会话ID

        Raises:
            Exception: 数据库操作失败时
        """
        try:
            # 获取agent名称用于生成默认标题
            if not title:
                agent_result = (
                    self.supabase.table("agents")
                    .select("name")
                    .eq("id", agent_id)
                    .execute()
                )
                agent_name = (
                    agent_result.data[0]["name"] if agent_result.data else "AI员工"
                )
                title = f"与 {agent_name} 的对话"

            conversation_data = {
                "user_id": user_id,
                "agent_id": agent_id,
                "title": title,
                "status": "active",
                "started_at": datetime.utcnow().isoformat(),
                "last_message_at": datetime.utcnow().isoformat(),
            }

            result = (
                self.supabase.table("conversations")
                .insert(conversation_data)
                .execute()
            )

            if not result.data or len(result.data) == 0:
                raise Exception("Failed to create conversation: no data returned")

            conversation = result.data[0]
            logger.info(
                f"Created new conversation (multi-conversation mode): {conversation['id']} "
                f"for user={user_id}, agent={agent_id}, title='{title}'"
            )
            return conversation["id"]

        except Exception as e:
            logger.error(
                f"Error creating conversation (user={user_id}, agent={agent_id}): {e}"
            )
            raise

    async def list_agent_conversations(
        self, user_id: str, agent_id: str, limit: int = 20, status: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """获取用户与特定Agent的所有会话（多会话模式）

        Args:
            user_id: 用户UUID
            agent_id: Agent UUID
            limit: 返回数量限制
            status: 状态过滤（可选）

        Returns:
            会话列表，按last_message_at降序排列
        """
        try:
            query = (
                self.supabase.table("conversations")
                .select("*")
                .eq("user_id", user_id)
                .eq("agent_id", agent_id)
            )

            if status:
                query = query.eq("status", status)

            result = query.order("last_message_at", desc=True).limit(limit).execute()

            logger.info(
                f"Found {len(result.data or [])} conversations for user={user_id}, agent={agent_id}"
            )
            return result.data or []

        except Exception as e:
            logger.error(
                f"Error listing agent conversations for user {user_id}, agent {agent_id}: {e}"
            )
            return []

    async def update_title(
        self, conversation_id: str, title: str
    ) -> Optional[Dict[str, Any]]:
        """更新会话标题

        Args:
            conversation_id: 会话UUID
            title: 新标题

        Returns:
            更新后的会话记录，如果失败返回None
        """
        try:
            result = (
                self.supabase.table("conversations")
                .update({"title": title})
                .eq("id", conversation_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                logger.info(f"Updated title for conversation {conversation_id}: '{title}'")
                return result.data[0]

            return None

        except Exception as e:
            logger.error(f"Error updating title for conversation {conversation_id}: {e}")
            return None

