"""
Message data model - 消息数据模型

支持多态消息内容：
- text: 普通文本消息（用户/助手）
- briefing_card: 简报卡片消息（系统）
"""

import logging
import json
from typing import Any, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class MessageModel:
    """消息数据模型

    核心功能：
    - create_text_message: 创建文本消息
    - create_briefing_card: 创建简报卡片消息
    - list_by_conversation: 获取对话的所有消息
    """

    def __init__(self, supabase_client: Any):
        """初始化消息模型

        Args:
            supabase_client: Supabase客户端实例
        """
        self.supabase = supabase_client

    async def create_text_message(
        self, conversation_id: str, role: str, content: str
    ) -> Dict[str, Any]:
        """创建文本消息

        Args:
            conversation_id: 对话UUID
            role: 消息角色 ('user', 'assistant', 'system')
            content: 消息内容文本

        Returns:
            创建的消息记录

        Raises:
            ValueError: 参数无效时
            Exception: 数据库操作失败时
        """
        if role not in ["user", "assistant", "system"]:
            raise ValueError(f"Invalid role: {role}. Must be user/assistant/system")

        if not content or not content.strip():
            raise ValueError("Content cannot be empty")

        try:
            message_data = {
                "conversation_id": conversation_id,
                "role": role,
                "content_type": "text",
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
            }

            result = (
                self.supabase.table("messages").insert(message_data).execute()
            )

            if not result.data or len(result.data) == 0:
                raise Exception("Failed to create text message: no data returned")

            message = result.data[0]
            logger.debug(
                f"Created text message: {message['id']} "
                f"in conversation {conversation_id}, role={role}"
            )
            return message

        except Exception as e:
            logger.error(
                f"Error creating text message in conversation {conversation_id}: {e}"
            )
            raise

    async def create_briefing_card(
        self, conversation_id: str, briefing_id: str, briefing_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建简报卡片消息（核心方法）

        将简报作为特殊消息插入对话流。简报卡片包含结构化数据：
        - title: 简报标题
        - summary: 简报摘要
        - priority: 优先级 (P0/P1/P2)
        - created_at: 简报创建时间

        Args:
            conversation_id: 对话UUID
            briefing_id: 简报UUID
            briefing_data: 简报数据字典，包含 title, summary, priority, created_at

        Returns:
            创建的消息记录

        Raises:
            ValueError: 简报数据缺少必需字段时
            Exception: 数据库操作失败时
        """
        # 验证必需字段
        required_fields = ["title", "summary", "priority"]
        missing_fields = [f for f in required_fields if f not in briefing_data]
        if missing_fields:
            raise ValueError(
                f"Briefing data missing required fields: {missing_fields}"
            )

        try:
            # 构建简报卡片内容（结构化JSON）
            card_content = {
                "title": briefing_data["title"],
                "summary": briefing_data["summary"],
                "priority": briefing_data["priority"],
                "created_at": briefing_data.get(
                    "created_at", datetime.utcnow().isoformat()
                ),
                "briefing_type": briefing_data.get("briefing_type", "insight"),
                "impact": briefing_data.get("impact", ""),
            }

            message_data = {
                "conversation_id": conversation_id,
                "role": "system",
                "content_type": "briefing_card",
                "briefing_id": briefing_id,
                "content": json.dumps(card_content, ensure_ascii=False),
                "created_at": datetime.utcnow().isoformat(),
            }

            result = (
                self.supabase.table("messages").insert(message_data).execute()
            )

            if not result.data or len(result.data) == 0:
                raise Exception("Failed to create briefing card: no data returned")

            message = result.data[0]
            logger.info(
                f"Created briefing card: message_id={message['id']}, "
                f"briefing_id={briefing_id}, conversation_id={conversation_id}"
            )
            return message

        except Exception as e:
            logger.error(
                f"Error creating briefing card in conversation {conversation_id}: {e}"
            )
            raise

    async def list_by_conversation(
        self, conversation_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """获取对话的所有消息（按时间顺序）

        返回包含文本消息和简报卡片的完整消息历史。

        Args:
            conversation_id: 对话UUID
            limit: 返回数量限制（默认50条）
            offset: 偏移量（用于分页）

        Returns:
            消息列表，按created_at升序排列（时间线顺序）

        Note:
            对于briefing_card类型消息，content字段包含JSON字符串，
            需要在使用时解析为字典。
        """
        try:
            result = (
                self.supabase.table("messages")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=False)  # 时间线顺序
                .range(offset, offset + limit - 1)
                .execute()
            )

            messages = result.data or []

            logger.debug(
                f"Retrieved {len(messages)} messages "
                f"from conversation {conversation_id}"
            )

            return messages

        except Exception as e:
            logger.error(
                f"Error listing messages for conversation {conversation_id}: {e}"
            )
            return []

    async def get_recent_messages(
        self, conversation_id: str, count: int = 20
    ) -> List[Dict[str, Any]]:
        """获取对话的最近N条消息

        用于构建AI上下文，避免加载过多历史消息。

        Args:
            conversation_id: 对话UUID
            count: 消息数量（默认20条）

        Returns:
            最近N条消息，按created_at升序排列
        """
        try:
            result = (
                self.supabase.table("messages")
                .select("*")
                .eq("conversation_id", conversation_id)
                .order("created_at", desc=True)  # 先降序获取最新的
                .limit(count)
                .execute()
            )

            messages = result.data or []

            # 反转顺序，变成时间线顺序（升序）
            messages.reverse()

            logger.debug(
                f"Retrieved {len(messages)} recent messages "
                f"from conversation {conversation_id}"
            )

            return messages

        except Exception as e:
            logger.error(
                f"Error getting recent messages for conversation {conversation_id}: {e}"
            )
            return []

    async def delete_message(self, message_id: str) -> bool:
        """删除消息（软删除或硬删除）

        注意：当前实现为硬删除。未来可以改为软删除（标记deleted=true）。

        Args:
            message_id: 消息UUID

        Returns:
            删除成功返回True，失败返回False
        """
        try:
            result = (
                self.supabase.table("messages")
                .delete()
                .eq("id", message_id)
                .execute()
            )

            logger.info(f"Deleted message: {message_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting message {message_id}: {e}")
            return False
