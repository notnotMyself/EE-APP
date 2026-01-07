"""
User-Agent Subscription SQLAlchemy model.
"""
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base


class UserAgentSubscription(Base):
    """User-Agent subscription model."""
    __tablename__ = "user_agent_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)

    # Configuration
    config = Column(JSON, default={}, nullable=False)

    # Notification preferences
    notify_on_alert = Column(Boolean, default=True, nullable=False)
    notify_via_push = Column(Boolean, default=True, nullable=False)
    notify_via_email = Column(Boolean, default=False, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)

    # Ensure unique active subscription per user-agent pair
    __table_args__ = (
        UniqueConstraint('user_id', 'agent_id', 'is_active', name='uq_user_agent_active'),
    )
