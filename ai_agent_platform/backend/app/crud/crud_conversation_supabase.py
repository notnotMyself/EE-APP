"""
CRUD operations for Conversation and Message using Supabase Client.
"""
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from supabase import Client
from postgrest.exceptions import APIError

from app.core.config import settings
from supabase import create_client


def get_supabase_client() -> Client:
    """Get Supabase client with service role key."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )


class CRUDConversationSupabase:
    """CRUD operations for conversations using Supabase Client."""

    def __init__(self):
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def get(self, conversation_id: UUID) -> Optional[Dict[str, Any]]:
        """Get conversation by ID."""
        result = self.client.table("conversations").select("*").eq(
            "id", str(conversation_id)
        ).execute()
        return result.data[0] if result.data else None

    async def get_by_user_agent(
        self,
        *,
        user_id: Union[UUID, str],
        agent_id: Union[UUID, str],
    ) -> Optional[Dict[str, Any]]:
        """Get conversation by (user_id, agent_id) unique key."""
        result = (
            self.client.table("conversations")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("agent_id", str(agent_id))
            .order("last_message_at", desc=True)
            .limit(1)
            .execute()
        )
        return result.data[0] if result.data else None

    async def get_user_conversations(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get user's conversations."""
        query = self.client.table("conversations").select(
            "*, agents(name, role, avatar_url)"
        ).eq("user_id", str(user_id))

        if status:
            query = query.eq("status", status)

        query = query.order("last_message_at", desc=True).range(skip, skip + limit - 1)
        result = query.execute()

        # Flatten agent info
        conversations = []
        for conv in result.data:
            agent_info = conv.pop("agents", {}) or {}
            conversations.append({
                **conv,
                "agent_name": agent_info.get("name"),
                "agent_role": agent_info.get("role"),
                "agent_avatar_url": agent_info.get("avatar_url")
            })
        return conversations

    async def create(
        self,
        user_id: Union[UUID, str],
        *,
        obj_in: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new conversation.

        NOTE: conversations table may enforce a unique constraint on (user_id, agent_id).
        In that case, this method becomes idempotent and returns the existing conversation.
        """
        data = {
            "user_id": str(user_id),
            "agent_id": str(obj_in.get("agent_id")),
            "title": obj_in.get("title", "New Conversation"),
            "context": obj_in.get("context", {}),
            "status": "active",
            "last_message_at": datetime.utcnow().isoformat()
        }
        try:
            result = self.client.table("conversations").insert(data).execute()
            return result.data[0] if result.data else None
        except APIError as e:
            payload = e.args[0] if e.args else {}
            if isinstance(payload, dict) and payload.get("code") == "23505":
                existing = await self.get_by_user_agent(
                    user_id=data["user_id"],
                    agent_id=data["agent_id"],
                )
                if existing:
                    return existing
            raise

    async def update(
        self,
        *,
        conversation_id: UUID,
        obj_in: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a conversation."""
        result = self.client.table("conversations").update(
            obj_in
        ).eq("id", str(conversation_id)).execute()
        return result.data[0] if result.data else None

    async def update_last_message_time(self, conversation_id: UUID) -> None:
        """Update last_message_at timestamp."""
        self.client.table("conversations").update({
            "last_message_at": datetime.utcnow().isoformat()
        }).eq("id", str(conversation_id)).execute()

    async def close(self, conversation_id: UUID) -> Optional[Dict[str, Any]]:
        """Close a conversation."""
        result = self.client.table("conversations").update({
            "status": "closed",
            "closed_at": datetime.utcnow().isoformat()
        }).eq("id", str(conversation_id)).execute()
        return result.data[0] if result.data else None


class CRUDMessageSupabase:
    """CRUD operations for messages using Supabase Client."""

    def __init__(self):
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def get(self, message_id: UUID) -> Optional[Dict[str, Any]]:
        """Get message by ID."""
        result = self.client.table("messages").select("*").eq(
            "id", str(message_id)
        ).execute()
        return result.data[0] if result.data else None

    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get messages in a conversation."""
        result = self.client.table("messages").select("*").eq(
            "conversation_id", str(conversation_id)
        ).order("created_at").range(skip, skip + limit - 1).execute()
        return result.data

    async def get_recent_messages(
        self,
        conversation_id: UUID,
        *,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get recent messages for context building."""
        result = self.client.table("messages").select("*").eq(
            "conversation_id", str(conversation_id)
        ).order("created_at", desc=True).limit(limit).execute()
        # Return in chronological order
        return list(reversed(result.data))

    async def create(
        self,
        conversation_id: UUID,
        *,
        obj_in: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new message."""
        data = {
            "conversation_id": str(conversation_id),
            "role": obj_in.get("role"),
            "content": obj_in.get("content"),
            "metadata": obj_in.get("metadata", {})
        }
        result = self.client.table("messages").insert(data).execute()
        return result.data[0] if result.data else None


# Singleton instances
conversation_supabase = CRUDConversationSupabase()
message_supabase = CRUDMessageSupabase()

