"""Quota enforcement service.

Provides functions to check and enforce usage limits based on user's subscription plan.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.telemetry import traced
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.message import Message
from app.models.plan import Plan, PlanType
from app.models.project import Project
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User

logger = logging.getLogger(__name__)


# Default limits for users without active subscription (free tier fallback)
DEFAULT_LIMITS = {
    "tokens_per_month": 10000,
    "requests_per_minute": 5,
    "requests_per_day": 100,
    "max_documents": 5,
    "max_projects": 2,
    "max_agents": 1,
}


@dataclass
class QuotaStatus:
    """Quota status for a specific resource."""

    limit: int
    used: int
    remaining: int
    percentage: float
    is_exceeded: bool
    is_warning: bool  # 80% threshold

    @property
    def is_unlimited(self) -> bool:
        return self.limit == -1


@dataclass
class UserQuota:
    """Complete quota information for a user."""

    user_id: uuid.UUID
    plan_name: str
    plan_type: str
    tokens: QuotaStatus
    documents: QuotaStatus
    projects: QuotaStatus
    has_active_subscription: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "user_id": str(self.user_id),
            "plan_name": self.plan_name,
            "plan_type": self.plan_type,
            "has_active_subscription": self.has_active_subscription,
            "tokens": {
                "limit": self.tokens.limit,
                "used": self.tokens.used,
                "remaining": self.tokens.remaining,
                "percentage": self.tokens.percentage,
                "is_exceeded": self.tokens.is_exceeded,
                "is_warning": self.tokens.is_warning,
                "is_unlimited": self.tokens.is_unlimited,
            },
            "documents": {
                "limit": self.documents.limit,
                "used": self.documents.used,
                "remaining": self.documents.remaining,
                "percentage": self.documents.percentage,
                "is_exceeded": self.documents.is_exceeded,
                "is_warning": self.documents.is_warning,
            },
            "projects": {
                "limit": self.projects.limit,
                "used": self.projects.used,
                "remaining": self.projects.remaining,
                "percentage": self.projects.percentage,
                "is_exceeded": self.projects.is_exceeded,
                "is_warning": self.projects.is_warning,
            },
        }


def _calculate_quota_status(limit: int, used: int) -> QuotaStatus:
    """Calculate quota status from limit and usage."""
    # Handle unlimited (-1)
    if limit == -1:
        return QuotaStatus(
            limit=-1,
            used=used,
            remaining=-1,
            percentage=0.0,
            is_exceeded=False,
            is_warning=False,
        )

    remaining = max(0, limit - used)
    percentage = (used / limit * 100) if limit > 0 else 0.0

    return QuotaStatus(
        limit=limit,
        used=used,
        remaining=remaining,
        percentage=round(percentage, 1),
        is_exceeded=used >= limit,
        is_warning=percentage >= 80 and not (used >= limit),
    )


@traced()
async def get_user_plan(db: AsyncSession, user_id: uuid.UUID) -> Plan | None:
    """Get the active plan for a user."""
    query = (
        select(Plan)
        .join(Subscription, Subscription.plan_id == Plan.id)
        .where(
            and_(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE,
            )
        )
        .limit(1)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


@traced()
async def get_user_with_subscription(
    db: AsyncSession, user_id: uuid.UUID
) -> tuple[User | None, Subscription | None, Plan | None]:
    """Get user with their active subscription and plan."""
    query = (
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.subscriptions).selectinload(Subscription.plan)
        )
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None, None, None

    # Find active subscription
    active_sub = next(
        (s for s in user.subscriptions if s.status == SubscriptionStatus.ACTIVE),
        None,
    )

    plan = active_sub.plan if active_sub else None

    return user, active_sub, plan


@traced()
async def get_tokens_used_this_month(
    db: AsyncSession, user_id: uuid.UUID
) -> int:
    """Get total tokens used this month by user."""
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)

    # Get user's conversation IDs
    conv_stmt = select(Conversation.id).where(Conversation.user_id == user_id)
    conv_result = await db.execute(conv_stmt)
    conv_ids = [row[0] for row in conv_result.all()]

    if not conv_ids:
        return 0

    # Sum tokens from messages this month
    token_stmt = select(func.coalesce(func.sum(Message.tokens_used), 0)).where(
        and_(
            Message.conversation_id.in_(conv_ids),
            Message.created_at >= month_start,
        )
    )
    result = await db.execute(token_stmt)
    return int(result.scalar() or 0)


@traced()
async def get_document_count(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Get total document count for user."""
    stmt = select(func.count(Document.id)).where(Document.user_id == user_id)
    result = await db.execute(stmt)
    return int(result.scalar() or 0)


@traced()
async def get_project_count(db: AsyncSession, user_id: uuid.UUID) -> int:
    """Get total project count for user."""
    stmt = select(func.count(Project.id)).where(Project.user_id == user_id)
    result = await db.execute(stmt)
    return int(result.scalar() or 0)


@traced()
async def get_user_quota(db: AsyncSession, user_id: uuid.UUID) -> UserQuota:
    """
    Get complete quota information for a user.

    Returns quota status for tokens, documents, and projects.
    """
    user, subscription, plan = await get_user_with_subscription(db, user_id)

    if not user:
        raise ValueError(f"User {user_id} not found")

    # Determine limits from plan or use defaults
    if plan:
        tokens_limit = plan.tokens_per_month
        documents_limit = plan.max_documents
        projects_limit = plan.max_projects
        plan_name = plan.display_name
        plan_type = plan.plan_type.value

        # Enterprise has unlimited (-1)
        if plan.plan_type == PlanType.ENTERPRISE:
            tokens_limit = -1
    else:
        # Fallback to default limits
        tokens_limit = DEFAULT_LIMITS["tokens_per_month"]
        documents_limit = DEFAULT_LIMITS["max_documents"]
        projects_limit = DEFAULT_LIMITS["max_projects"]
        plan_name = "Free"
        plan_type = "free"

    # Get current usage
    tokens_used = await get_tokens_used_this_month(db, user_id)
    documents_used = await get_document_count(db, user_id)
    projects_used = await get_project_count(db, user_id)

    return UserQuota(
        user_id=user_id,
        plan_name=plan_name,
        plan_type=plan_type,
        has_active_subscription=subscription is not None,
        tokens=_calculate_quota_status(tokens_limit, tokens_used),
        documents=_calculate_quota_status(documents_limit, documents_used),
        projects=_calculate_quota_status(projects_limit, projects_used),
    )


@traced()
async def check_token_quota(
    db: AsyncSession, user_id: uuid.UUID
) -> tuple[bool, str | None]:
    """
    Check if user can use more tokens.

    Returns:
        Tuple of (is_allowed, error_message)
    """
    quota = await get_user_quota(db, user_id)

    if quota.tokens.is_unlimited:
        return True, None

    if quota.tokens.is_exceeded:
        return False, (
            f"Token quota exceeded. Used {quota.tokens.used:,} of "
            f"{quota.tokens.limit:,} tokens this month. "
            "Please upgrade your plan or wait until next month."
        )

    return True, None


@traced()
async def check_document_quota(
    db: AsyncSession, user_id: uuid.UUID
) -> tuple[bool, str | None]:
    """
    Check if user can upload more documents.

    Returns:
        Tuple of (is_allowed, error_message)
    """
    quota = await get_user_quota(db, user_id)

    if quota.documents.is_exceeded:
        return False, (
            f"Document limit reached. You have {quota.documents.used} of "
            f"{quota.documents.limit} documents allowed on your plan. "
            "Please delete some documents or upgrade your plan."
        )

    return True, None


@traced()
async def check_project_quota(
    db: AsyncSession, user_id: uuid.UUID
) -> tuple[bool, str | None]:
    """
    Check if user can create more projects.

    Returns:
        Tuple of (is_allowed, error_message)
    """
    quota = await get_user_quota(db, user_id)

    if quota.projects.is_exceeded:
        return False, (
            f"Project limit reached. You have {quota.projects.used} of "
            f"{quota.projects.limit} projects allowed on your plan. "
            "Please delete some projects or upgrade your plan."
        )

    return True, None


class QuotaExceededError(Exception):
    """Exception raised when quota is exceeded."""

    def __init__(self, message: str, quota_type: str):
        self.message = message
        self.quota_type = quota_type
        super().__init__(message)
