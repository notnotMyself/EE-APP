"""
Conversation and Message Pydantic schemas.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# Message schemas
class MessageBase(BaseModel):
    """Base message schema."""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    attachments: Optional[List[Dict[str, Any]]] = None


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    pass


class Message(MessageBase):
    """Complete message schema from database."""
    id: UUID
    conversation_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Conversation schemas
class ConversationBase(BaseModel):
    """Base conversation schema."""
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ConversationCreate(BaseModel):
    """Schema for creating a conversation."""
    agent_id: UUID
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    source_alert_id: Optional[UUID] = None


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(active|archived|closed)$")


class Conversation(ConversationBase):
    """Complete conversation schema from database."""
    id: UUID
    user_id: UUID
    agent_id: UUID
    status: str
    source_alert_id: Optional[UUID]
    started_at: datetime
    last_message_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ConversationWithMessages(Conversation):
    """Conversation with recent messages."""
    messages: List[Message] = []


class ConversationWithAgent(Conversation):
    """Conversation with agent details."""
    agent_name: str
    agent_role: str
    agent_avatar_url: Optional[str]


# Chat request/response schemas
class ChatRequest(BaseModel):
    """Request to send a message in a conversation."""
    message: str = Field(..., min_length=1, max_length=10000)
    stream: bool = Field(default=True, description="Use SSE streaming")


class ChatResponse(BaseModel):
    """Response for non-streaming chat."""
    message_id: UUID
    content: str
    conversation_id: UUID
