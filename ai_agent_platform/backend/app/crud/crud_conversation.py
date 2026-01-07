"""
CRUD operations for Conversation and Message models.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from datetime import datetime

from app.models.conversation import Conversation, Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate, MessageCreate


class CRUDConversation:
    """CRUD operations for conversations."""

    async def get(self, db: AsyncSession, conversation_id: UUID) -> Optional[Conversation]:
        """Get conversation by ID."""
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        return result.scalar_one_or_none()

    async def get_user_conversations(
        self,
        db: AsyncSession,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[Conversation]:
        """Get user's conversations."""
        query = select(Conversation).where(Conversation.user_id == user_id)

        if status:
            query = query.where(Conversation.status == status)

        query = query.order_by(Conversation.last_message_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_agent_conversations(
        self,
        db: AsyncSession,
        agent_id: UUID,
        *,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Get conversations for a specific agent."""
        result = await db.execute(
            select(Conversation)
            .where(Conversation.agent_id == agent_id)
            .order_by(Conversation.last_message_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(
        self,
        db: AsyncSession,
        *,
        user_id: UUID,
        obj_in: ConversationCreate
    ) -> Conversation:
        """Create a new conversation."""
        db_obj = Conversation(
            user_id=user_id,
            agent_id=obj_in.agent_id,
            title=obj_in.title,
            context=obj_in.context,
            source_alert_id=obj_in.source_alert_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Conversation,
        obj_in: ConversationUpdate
    ) -> Conversation:
        """Update a conversation."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update_last_message_time(
        self,
        db: AsyncSession,
        conversation_id: UUID
    ) -> None:
        """Update last_message_at timestamp."""
        await db.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(last_message_at=datetime.utcnow())
        )
        await db.commit()

    async def close(
        self,
        db: AsyncSession,
        conversation_id: UUID
    ) -> Optional[Conversation]:
        """Close a conversation."""
        conversation = await self.get(db, conversation_id)
        if conversation:
            conversation.status = "closed"
            conversation.closed_at = datetime.utcnow()
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
        return conversation


class CRUDMessage:
    """CRUD operations for messages."""

    async def get(self, db: AsyncSession, message_id: UUID) -> Optional[Message]:
        """Get message by ID."""
        result = await db.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_conversation_messages(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        *,
        limit: Optional[int] = None
    ) -> List[Message]:
        """Get messages for a conversation."""
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc())

        if limit:
            query = query.limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_recent_messages(
        self,
        db: AsyncSession,
        conversation_id: UUID,
        limit: int = 10
    ) -> List[Message]:
        """Get recent messages for context."""
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order

    async def create(
        self,
        db: AsyncSession,
        *,
        conversation_id: UUID,
        obj_in: MessageCreate
    ) -> Message:
        """Create a new message."""
        db_obj = Message(
            conversation_id=conversation_id,
            role=obj_in.role,
            content=obj_in.content,
            metadata=obj_in.metadata,
            attachments=obj_in.attachments,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def count_conversation_messages(
        self,
        db: AsyncSession,
        conversation_id: UUID
    ) -> int:
        """Count messages in a conversation."""
        result = await db.execute(
            select(func.count(Message.id)).where(
                Message.conversation_id == conversation_id
            )
        )
        return result.scalar()


# Create singleton instances
conversation = CRUDConversation()
message = CRUDMessage()
