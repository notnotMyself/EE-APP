"""
CRUD operations for Agent using Supabase Client.
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from supabase import Client

from app.core.config import settings
from supabase import create_client


def get_supabase_client() -> Client:
    """Get Supabase client with service role key."""
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )


class CRUDAgentSupabase:
    """CRUD operations for agents using Supabase Client."""

    def __init__(self):
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = get_supabase_client()
        return self._client

    async def get(self, agent_id: UUID) -> Optional[Dict[str, Any]]:
        """Get agent by ID."""
        result = self.client.table("agents").select("*").eq(
            "id", str(agent_id)
        ).execute()
        return result.data[0] if result.data else None

    async def get_by_role(self, role: str) -> Optional[Dict[str, Any]]:
        """Get agent by role."""
        result = self.client.table("agents").select("*").eq(
            "role", role
        ).execute()
        return result.data[0] if result.data else None

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get multiple agents."""
        query = self.client.table("agents").select("*")

        if active_only:
            query = query.eq("is_active", True)

        query = query.order("created_at", desc=True).range(skip, skip + limit - 1)
        result = query.execute()
        return result.data

    async def get_builtin_agents(self) -> List[Dict[str, Any]]:
        """Get all built-in agents."""
        result = self.client.table("agents").select("*").eq(
            "is_builtin", True
        ).eq("is_active", True).order("created_at").execute()
        return result.data

    async def get_user_created_agents(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get agents created by user."""
        result = self.client.table("agents").select("*").eq(
            "created_by", str(user_id)
        ).order("created_at", desc=True).execute()
        return result.data

    async def create(
        self,
        *,
        obj_in: Dict[str, Any],
        created_by: UUID,
        is_builtin: bool = False
    ) -> Dict[str, Any]:
        """Create a new agent."""
        data = {
            **obj_in,
            "created_by": str(created_by),
            "is_builtin": is_builtin,
            "is_active": True
        }
        result = self.client.table("agents").insert(data).execute()
        return result.data[0] if result.data else None

    async def update(
        self,
        *,
        agent_id: UUID,
        obj_in: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an agent."""
        result = self.client.table("agents").update(
            obj_in
        ).eq("id", str(agent_id)).execute()
        return result.data[0] if result.data else None

    async def delete(self, agent_id: UUID) -> Optional[Dict[str, Any]]:
        """Soft delete an agent (deactivate)."""
        result = self.client.table("agents").update({
            "is_active": False
        }).eq("id", str(agent_id)).execute()
        return result.data[0] if result.data else None


# Singleton instance
agent_supabase = CRUDAgentSupabase()

