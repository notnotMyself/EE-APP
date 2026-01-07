"""
Agent Pydantic schemas for request/response validation.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# Base schema with common fields
class AgentBase(BaseModel):
    """Base agent schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    role: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    data_sources: Optional[Dict[str, Any]] = Field(default_factory=dict)
    trigger_conditions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    capabilities: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


# Schema for creating a new agent
class AgentCreate(AgentBase):
    """Schema for creating a new agent."""
    pass


# Schema for updating an agent
class AgentUpdate(BaseModel):
    """Schema for updating an agent (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    role: Optional[str] = Field(None, min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    data_sources: Optional[Dict[str, Any]] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


# Schema for agent in database (includes all fields)
class Agent(AgentBase):
    """Complete agent schema from database."""
    id: UUID
    is_active: bool
    is_builtin: bool
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema for agent list response (minimal fields)
class AgentListItem(BaseModel):
    """Minimal agent info for list views."""
    id: UUID
    name: str
    role: str
    description: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_builtin: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Schema for agent statistics
class AgentStats(BaseModel):
    """Statistics for an agent."""
    total_subscribers: int = 0
    total_alerts_generated: int = 0
    total_conversations: int = 0
    total_tasks_completed: int = 0
