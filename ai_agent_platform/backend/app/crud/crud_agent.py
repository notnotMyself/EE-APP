"""
CRUD operations for Agent model.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


class CRUDAgent:
    """CRUD operations for agents."""

    async def get(self, db: AsyncSession, agent_id: UUID) -> Optional[Agent]:
        """Get agent by ID."""
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        return result.scalar_one_or_none()

    async def get_by_role(self, db: AsyncSession, role: str) -> Optional[Agent]:
        """Get agent by role."""
        result = await db.execute(
            select(Agent).where(Agent.role == role)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Agent]:
        """Get multiple agents."""
        query = select(Agent)

        if active_only:
            query = query.where(Agent.is_active == True)

        query = query.offset(skip).limit(limit).order_by(Agent.created_at.desc())

        result = await db.execute(query)
        return result.scalars().all()

    async def get_builtin_agents(self, db: AsyncSession) -> List[Agent]:
        """Get all built-in system agents."""
        result = await db.execute(
            select(Agent).where(
                and_(Agent.is_builtin == True, Agent.is_active == True)
            ).order_by(Agent.created_at)
        )
        return result.scalars().all()

    async def get_user_created_agents(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> List[Agent]:
        """Get agents created by a specific user."""
        result = await db.execute(
            select(Agent).where(
                and_(Agent.created_by == user_id, Agent.is_active == True)
            ).order_by(Agent.created_at.desc())
        )
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: AgentCreate,
        created_by: Optional[UUID] = None,
        is_builtin: bool = False
    ) -> Agent:
        """Create a new agent."""
        db_obj = Agent(
            name=obj_in.name,
            description=obj_in.description,
            role=obj_in.role,
            avatar_url=obj_in.avatar_url,
            data_sources=obj_in.data_sources,
            trigger_conditions=obj_in.trigger_conditions,
            capabilities=obj_in.capabilities,
            metadata=obj_in.metadata,
            is_builtin=is_builtin,
            created_by=created_by,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Agent,
        obj_in: AgentUpdate
    ) -> Agent:
        """Update an agent."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, agent_id: UUID) -> Agent:
        """Soft delete an agent by setting is_active to False."""
        agent = await self.get(db, agent_id)
        if agent:
            agent.is_active = False
            db.add(agent)
            await db.commit()
            await db.refresh(agent)
        return agent

    async def count(self, db: AsyncSession, active_only: bool = True) -> int:
        """Count total agents."""
        query = select(func.count(Agent.id))

        if active_only:
            query = query.where(Agent.is_active == True)

        result = await db.execute(query)
        return result.scalar()


# Create a singleton instance
agent = CRUDAgent()
