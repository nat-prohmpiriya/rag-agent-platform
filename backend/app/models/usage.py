"""Usage tracking models for request-based billing."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class RequestType(str, enum.Enum):
    """Type of LLM request."""

    CHAT = "chat"
    RAG = "rag"
    AGENT = "agent"
    EMBEDDING = "embedding"
    IMAGE = "image"
    TOOL = "tool"


class UsageRecord(Base, TimestampMixin):
    """Individual usage record for each LLM request.

    Tracks every request made to LLM providers for billing and analytics.
    """

    __tablename__ = "usage_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # User reference
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Request details
    request_type: Mapped[RequestType] = mapped_column(
        Enum(RequestType),
        default=RequestType.CHAT,
        nullable=False,
    )
    model: Mapped[str] = mapped_column(String(100), nullable=False)

    # Token usage
    tokens_input: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Cost tracking (from LiteLLM)
    cost: Mapped[float] = mapped_column(Numeric(12, 6), default=0.0, nullable=False)

    # Credit system
    credits_used: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Performance metrics
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Reference IDs for tracing
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    # LiteLLM reference
    litellm_call_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Additional metadata
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="usage_records")

    __table_args__ = (
        Index("ix_usage_records_user_created", "user_id", "created_at"),
        Index("ix_usage_records_model", "model"),
        Index("ix_usage_records_request_type", "request_type"),
    )

    def __repr__(self) -> str:
        return f"<UsageRecord(id={self.id}, user_id={self.user_id}, model={self.model})>"


class UsageSummary(Base, TimestampMixin):
    """Aggregated usage summary per user per period.

    Pre-computed summary for fast quota checks and billing.
    Updated incrementally with each request.
    """

    __tablename__ = "usage_summaries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # User reference
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Period (format: YYYY-MM for monthly billing)
    period: Mapped[str] = mapped_column(String(7), nullable=False)  # e.g., "2024-01"

    # Aggregated counts
    total_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_credits: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Cost tracking
    total_cost: Mapped[float] = mapped_column(Numeric(12, 4), default=0.0, nullable=False)

    # Breakdown by request type
    chat_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rag_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    agent_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    embedding_requests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Sync status with LiteLLM
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="usage_summaries")

    __table_args__ = (
        UniqueConstraint("user_id", "period", name="uq_usage_summary_user_period"),
        Index("ix_usage_summaries_period", "period"),
    )

    def __repr__(self) -> str:
        return f"<UsageSummary(user_id={self.user_id}, period={self.period}, requests={self.total_requests})>"


# Import at the end to avoid circular imports
from app.models.user import User  # noqa: E402, F401
