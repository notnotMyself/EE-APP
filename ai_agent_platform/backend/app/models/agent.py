"""
Agent SQLAlchemy model.
"""
from sqlalchemy import Boolean, Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base


class Agent(Base):
    """AI Agent model."""
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    description = Column(String, nullable=True)
    role = Column(String(100), nullable=False)
    avatar_url = Column(String, nullable=True)

    # Configuration stored as JSON
    data_sources = Column(JSON, nullable=True)
    trigger_conditions = Column(JSON, nullable=True)
    capabilities = Column(JSON, nullable=True)

    # System fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_builtin = Column(Boolean, default=False, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Metadata (renamed to avoid SQLAlchemy reserved word)
    extra_metadata = Column("metadata", JSON, default={}, nullable=False)
