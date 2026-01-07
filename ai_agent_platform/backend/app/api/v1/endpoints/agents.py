"""
Agent API endpoints.
使用 Supabase Client 替代 SQLAlchemy 直连。
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_active_user
from app.crud.crud_agent_supabase import agent_supabase as crud_agent
from app.schemas.agent import (
    Agent,
    AgentCreate,
    AgentUpdate,
    AgentListItem,
)
from app.schemas.user import CurrentUser

router = APIRouter()


@router.get("/", response_model=List[AgentListItem])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Get list of all agents.

    - **skip**: Number of items to skip (pagination)
    - **limit**: Maximum number of items to return
    - **active_only**: Only return active agents
    """
    agents = await crud_agent.get_multi(
        skip=skip, limit=limit, active_only=active_only
    )
    return agents


@router.get("/builtin", response_model=List[Agent])
async def list_builtin_agents(
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Get all built-in system agents.
    """
    agents = await crud_agent.get_builtin_agents()
    return agents


@router.get("/my-agents", response_model=List[Agent])
async def list_my_agents(
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Get agents created by current user.
    """
    agents = await crud_agent.get_user_created_agents(current_user.id)
    return agents


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Get agent details by ID.
    """
    agent = await crud_agent.get(agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent


@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_in: AgentCreate,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Create a new agent.

    Only authenticated users can create agents.
    Created agents are not built-in by default.
    """
    # Check if role already exists
    existing = await crud_agent.get_by_role(role=agent_in.role)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent with role '{agent_in.role}' already exists"
        )

    agent = await crud_agent.create(
        obj_in=agent_in.model_dump(),
        created_by=current_user.id,
        is_builtin=False
    )
    return agent


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: UUID,
    agent_in: AgentUpdate,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Update an agent.

    Users can only update agents they created.
    Superusers can update any agent.
    Built-in agents can only be updated by superusers.
    """
    agent = await crud_agent.get(agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Permission check
    if agent.get("is_builtin") and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update built-in agents"
        )

    if str(agent.get("created_by")) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this agent"
        )

    updated = await crud_agent.update(
        agent_id=agent_id,
        obj_in=agent_in.model_dump(exclude_unset=True)
    )
    return updated


@router.delete("/{agent_id}", response_model=Agent)
async def delete_agent(
    agent_id: UUID,
    current_user: CurrentUser = Depends(get_current_active_user),
):
    """
    Delete (deactivate) an agent.

    Users can only delete agents they created.
    Superusers can delete any agent.
    Built-in agents cannot be deleted.
    """
    agent = await crud_agent.get(agent_id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )

    # Permission check
    if agent.get("is_builtin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete built-in agents"
        )

    if str(agent.get("created_by")) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this agent"
        )

    deleted = await crud_agent.delete(agent_id=agent_id)
    return deleted
