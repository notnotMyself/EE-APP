"""
User-Agent Subscription Pydantic schemas.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# Base subscription schema
class SubscriptionBase(BaseModel):
    """Base subscription schema."""
    agent_id: UUID
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    notify_on_alert: bool = True
    notify_via_push: bool = True
    notify_via_email: bool = False


# Schema for creating a subscription
class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a new subscription."""
    pass


# Schema for updating a subscription
class SubscriptionUpdate(BaseModel):
    """Schema for updating a subscription."""
    config: Optional[Dict[str, Any]] = None
    notify_on_alert: Optional[bool] = None
    notify_via_push: Optional[bool] = None
    notify_via_email: Optional[bool] = None
    is_active: Optional[bool] = None


# Complete subscription from database
class Subscription(SubscriptionBase):
    """Complete subscription schema from database."""
    id: UUID
    user_id: UUID
    is_active: bool
    subscribed_at: datetime
    unsubscribed_at: Optional[datetime]

    class Config:
        from_attributes = True


# Subscription with agent details
class SubscriptionWithAgent(Subscription):
    """Subscription with agent information."""
    agent_name: str
    agent_role: str
    agent_description: Optional[str]
    agent_avatar_url: Optional[str]

    class Config:
        from_attributes = True
