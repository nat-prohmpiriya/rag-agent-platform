"""Message model for individual chat messages."""

import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class MessageRole(str, enum.Enum):
    """Role of the message sender."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(Base, TimestampMixin):
    """Message model for storing individual chat messages."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(MessageRole),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    tokens_used: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    # Full-text search vector (auto-updated by trigger)
    search_vector: Mapped[str | None] = mapped_column(
        TSVECTOR,
        nullable=True,
    )

    # GIN index for full-text search
    __table_args__ = (
        Index(
            'ix_messages_search_vector',
            'search_vector',
            postgresql_using='gin'
        ),
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role})>"


# Import at the end to avoid circular imports
from app.models.conversation import Conversation  # noqa: E402, F401
