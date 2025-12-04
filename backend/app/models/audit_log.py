"""Audit Log model for tracking admin actions."""

import uuid
from enum import Enum

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class AuditAction(str, Enum):
    """Enumeration of audit log actions."""

    # User actions
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_SUSPEND = "user_suspend"
    USER_ACTIVATE = "user_activate"
    USER_BAN = "user_ban"

    # Plan actions
    PLAN_CREATE = "plan_create"
    PLAN_UPDATE = "plan_update"
    PLAN_DELETE = "plan_delete"

    # Subscription actions
    SUBSCRIPTION_CREATE = "subscription_create"
    SUBSCRIPTION_UPGRADE = "subscription_upgrade"
    SUBSCRIPTION_DOWNGRADE = "subscription_downgrade"
    SUBSCRIPTION_CANCEL = "subscription_cancel"

    # Billing actions
    REFUND_ISSUE = "refund_issue"
    INVOICE_VOID = "invoice_void"

    # System actions
    SETTINGS_UPDATE = "settings_update"
    SYSTEM_CONFIG = "system_config"


class AuditLog(Base, TimestampMixin):
    """Audit log model for tracking admin actions."""

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Admin who performed the action
    admin_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Action details
    action: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Target entity
    target_type: Mapped[str | None] = mapped_column(
        String(50), index=True, nullable=True
    )  # user, plan, subscription, etc.
    target_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=True
    )

    # Additional details
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Request metadata
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6 max length
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    admin: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[admin_id],
        lazy="joined",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("ix_audit_logs_admin_created", "admin_id", "created_at"),
        Index("ix_audit_logs_action_created", "action", "created_at"),
        Index("ix_audit_logs_target", "target_type", "target_id"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, admin_id={self.admin_id})>"


# Import at the end to avoid circular imports
from app.models.user import User  # noqa: E402, F401
