"""
CRUD operations for Subscription using Supabase Client.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from supabase import Client

from app.core.config import settings
from supabase import create_client


def get_supabase_client() -> Client:
    """Get Supabase client with service role key."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )


class CRUDSubscriptionSupabase:
    """CRUD operations for subscriptions using Supabase Client."""

    def __init__(self):
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def get(self, subscription_id: UUID) -> Optional[Dict[str, Any]]:
        """Get subscription by ID."""
        result = self.client.table("user_agent_subscriptions").select("*").eq(
            "id", str(subscription_id)
        ).execute()
        return result.data[0] if result.data else None

    async def get_user_subscriptions(
        self,
        user_id: UUID,
        *,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get user's subscriptions."""
        query = self.client.table("user_agent_subscriptions").select(
            "*, agents(name, role, avatar_url, description)"
        ).eq("user_id", str(user_id))

        if active_only:
            query = query.eq("is_active", True)

        result = query.order("subscribed_at", desc=True).execute()
        
        # Flatten agent info
        subscriptions = []
        for sub in result.data:
            agent_info = sub.pop("agents", {}) or {}
            subscriptions.append({
                **sub,
                "agent_name": agent_info.get("name"),
                "agent_role": agent_info.get("role"),
                "agent_avatar_url": agent_info.get("avatar_url"),
                "agent_description": agent_info.get("description")
            })
        return subscriptions

    async def get_user_subscription(
        self,
        user_id: UUID,
        agent_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get user's subscription for specific agent."""
        result = self.client.table("user_agent_subscriptions").select("*").eq(
            "user_id", str(user_id)
        ).eq("agent_id", str(agent_id)).eq("is_active", True).execute()
        return result.data[0] if result.data else None

    async def create(
        self,
        user_id: UUID,
        *,
        obj_in: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new subscription."""
        data = {
            "user_id": str(user_id),
            "agent_id": str(obj_in.get("agent_id")),
            "config": obj_in.get("config", {}),
            "notify_on_alert": obj_in.get("notify_on_alert", True),
            "notify_via_push": obj_in.get("notify_via_push", True),
            "notify_via_email": obj_in.get("notify_via_email", False),
            "is_active": True,
            "subscribed_at": datetime.utcnow().isoformat()
        }
        result = self.client.table("user_agent_subscriptions").insert(data).execute()
        return result.data[0] if result.data else None

    async def update(
        self,
        *,
        subscription_id: UUID,
        obj_in: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a subscription."""
        result = self.client.table("user_agent_subscriptions").update(
            obj_in
        ).eq("id", str(subscription_id)).execute()
        return result.data[0] if result.data else None

    async def resubscribe(
        self,
        user_id: UUID,
        agent_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Reactivate an inactive subscription."""
        result = self.client.table("user_agent_subscriptions").update({
            "is_active": True,
            "subscribed_at": datetime.utcnow().isoformat()
        }).eq("user_id", str(user_id)).eq(
            "agent_id", str(agent_id)
        ).eq("is_active", False).execute()
        return result.data[0] if result.data else None

    async def unsubscribe(
        self,
        user_id: UUID,
        agent_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Deactivate a subscription."""
        result = self.client.table("user_agent_subscriptions").update({
            "is_active": False,
            "unsubscribed_at": datetime.utcnow().isoformat()
        }).eq("user_id", str(user_id)).eq(
            "agent_id", str(agent_id)
        ).eq("is_active", True).execute()
        return result.data[0] if result.data else None

    async def count_agent_subscribers(self, agent_id: UUID) -> int:
        """Count active subscribers for an agent."""
        result = self.client.table("user_agent_subscriptions").select(
            "id", count="exact"
        ).eq("agent_id", str(agent_id)).eq("is_active", True).execute()
        return result.count or 0


# Singleton instance
subscription_supabase = CRUDSubscriptionSupabase()

