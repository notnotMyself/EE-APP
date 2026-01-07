"""
CRUD operations for Briefing using Supabase Client.
This is an alternative to SQLAlchemy-based crud_briefing.py
that uses Supabase Client for database operations.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from supabase import create_client, Client

from app.core.config import settings


def get_supabase_client() -> Client:
    """Get Supabase client with service role key for full access."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )


class CRUDBriefingSupabase:
    """CRUD operations for briefings using Supabase Client."""

    def __init__(self):
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def get(self, briefing_id: UUID) -> Optional[Dict[str, Any]]:
        """Get briefing by ID."""
        result = self.client.table("briefings").select("*").eq(
            "id", str(briefing_id)
        ).execute()
        if not result.data:
            return None
        briefing = result.data[0]
        # 确保 importance_score 是浮点数而非字符串
        if "importance_score" in briefing and briefing["importance_score"] is not None:
            briefing["importance_score"] = float(briefing["importance_score"])
        return briefing

    async def get_with_agent(self, briefing_id: UUID) -> Optional[Dict[str, Any]]:
        """Get briefing with agent info."""
        result = self.client.table("briefings").select(
            "*, agents(name, avatar_url, role)"
        ).eq("id", str(briefing_id)).execute()

        if not result.data:
            return None

        briefing = result.data[0]
        agent_info = briefing.pop("agents", {}) or {}
        # 确保 importance_score 是浮点数而非字符串
        if "importance_score" in briefing and briefing["importance_score"] is not None:
            briefing["importance_score"] = float(briefing["importance_score"])
        return {
            **briefing,
            "agent_name": agent_info.get("name"),
            "agent_avatar_url": agent_info.get("avatar_url"),
            "agent_role": agent_info.get("role")
        }

    async def get_user_briefings(
        self,
        user_id: UUID,
        *,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's briefings with agent info."""
        query = self.client.table("briefings").select(
            "*, agents(name, avatar_url, role)"
        ).eq("user_id", str(user_id))

        if status:
            query = query.eq("status", status)

        query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
        result = query.execute()

        briefings = []
        for briefing in result.data:
            agent_info = briefing.pop("agents", {}) or {}
            # 确保 importance_score 是浮点数而非字符串
            if "importance_score" in briefing and briefing["importance_score"] is not None:
                briefing["importance_score"] = float(briefing["importance_score"])
            briefings.append({
                **briefing,
                "agent_name": agent_info.get("name"),
                "agent_avatar_url": agent_info.get("avatar_url"),
                "agent_role": agent_info.get("role")
            })

        return briefings

    async def count_user_briefings(
        self,
        user_id: UUID,
        *,
        status: Optional[str] = None
    ) -> int:
        """Count user's briefings."""
        query = self.client.table("briefings").select(
            "id", count="exact"
        ).eq("user_id", str(user_id))

        if status:
            query = query.eq("status", status)

        result = query.execute()
        return result.count or 0

    async def get_unread_count(self, user_id: UUID) -> Dict[str, Any]:
        """Get unread briefing count by priority."""
        # 获取所有未读的简报
        result = self.client.table("briefings").select(
            "priority"
        ).eq("user_id", str(user_id)).eq("status", "new").execute()

        total = len(result.data)
        by_priority = {}
        for item in result.data:
            priority = item.get("priority", "normal")
            by_priority[priority] = by_priority.get(priority, 0) + 1

        return {
            "count": total,
            "by_priority": by_priority
        }

    async def mark_as_read(self, briefing_id: UUID) -> Optional[Dict[str, Any]]:
        """Mark briefing as read."""
        result = self.client.table("briefings").update({
            "status": "read",
            "read_at": datetime.utcnow().isoformat()
        }).eq("id", str(briefing_id)).eq("status", "new").execute()

        if not result.data:
            return None
        briefing = result.data[0]
        # 确保 importance_score 是浮点数而非字符串
        if "importance_score" in briefing and briefing["importance_score"] is not None:
            briefing["importance_score"] = float(briefing["importance_score"])
        return briefing

    async def mark_as_actioned(
        self,
        briefing_id: UUID,
        conversation_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Mark briefing as actioned."""
        update_data = {
            "status": "actioned",
            "actioned_at": datetime.utcnow().isoformat()
        }
        if conversation_id:
            update_data["conversation_id"] = str(conversation_id)

        result = self.client.table("briefings").update(
            update_data
        ).eq("id", str(briefing_id)).execute()

        if not result.data:
            return None
        briefing = result.data[0]
        # 确保 importance_score 是浮点数而非字符串
        if "importance_score" in briefing and briefing["importance_score"] is not None:
            briefing["importance_score"] = float(briefing["importance_score"])
        return briefing

    async def dismiss(self, briefing_id: UUID) -> Optional[Dict[str, Any]]:
        """Dismiss a briefing."""
        result = self.client.table("briefings").update({
            "status": "dismissed"
        }).eq("id", str(briefing_id)).execute()

        if not result.data:
            return None
        briefing = result.data[0]
        # 确保 importance_score 是浮点数而非字符串
        if "importance_score" in briefing and briefing["importance_score"] is not None:
            briefing["importance_score"] = float(briefing["importance_score"])
        return briefing


# Singleton instance
briefing_supabase = CRUDBriefingSupabase()

