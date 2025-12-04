from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_current_user, get_db
from app.core.exceptions import ConflictError
from app.models.agent import Agent
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.message import Message
from app.models.user import User
from app.schemas.base import BaseResponse, MessageResponse
from app.schemas.stats import UsageQuota, UserStatsResponse, UserUsageResponse
from app.schemas.user import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    UserProfileResponse,
    UserUpdate,
)
from app.services.auth import change_password, delete_account

# Token limits by tier
TIER_LIMITS: dict[str, int | None] = {
    "free": 50000,
    "basic": 200000,
    "pro": 1000000,
    "enterprise": None,  # unlimited
}

# Average cost per million tokens (simplified)
COST_PER_1M_TOKENS = 0.50

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
async def get_profile(
    current_user: User = Depends(get_current_user),
) -> BaseResponse[UserProfileResponse]:
    """Get current user's profile."""
    ctx = get_context()
    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserProfileResponse.model_validate(current_user),
    )


@router.put("")
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[UserProfileResponse]:
    """Update current user's profile."""
    ctx = get_context()

    # Check username uniqueness if provided
    if data.username and data.username != current_user.username:
        result = await db.execute(
            select(User).where(User.username == data.username)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise ConflictError("Username already taken")

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserProfileResponse.model_validate(current_user),
    )


@router.post("/change-password")
async def change_user_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[MessageResponse]:
    """Change current user's password."""
    ctx = get_context()

    await change_password(
        db=db,
        user=current_user,
        current_password=data.current_password,
        new_password=data.new_password,
    )

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=MessageResponse(message="Password changed successfully"),
    )


@router.post("/delete-account")
async def delete_user_account(
    data: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[MessageResponse]:
    """Delete current user's account (soft delete)."""
    ctx = get_context()

    await delete_account(
        db=db,
        user=current_user,
        password=data.password,
    )

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=MessageResponse(message="Account deleted successfully"),
    )


@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[UserStatsResponse]:
    """Get current user's usage statistics."""
    ctx = get_context()

    # Count conversations
    conv_result = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.user_id == current_user.id
        )
    )
    conversations_count = conv_result.scalar() or 0

    # Count documents
    doc_result = await db.execute(
        select(func.count(Document.id)).where(Document.user_id == current_user.id)
    )
    documents_count = doc_result.scalar() or 0

    # Count agents (user-created only)
    agent_result = await db.execute(
        select(func.count(Agent.id)).where(Agent.user_id == current_user.id)
    )
    agents_count = agent_result.scalar() or 0

    # Count total messages (via conversations)
    msg_result = await db.execute(
        select(func.count(Message.id))
        .join(Conversation, Message.conversation_id == Conversation.id)
        .where(Conversation.user_id == current_user.id)
    )
    total_messages = msg_result.scalar() or 0

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserStatsResponse(
            conversations_count=conversations_count,
            documents_count=documents_count,
            agents_count=agents_count,
            total_messages=total_messages,
        ),
    )


@router.get("/usage")
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[UserUsageResponse]:
    """Get user's token usage statistics."""
    ctx = get_context()

    # Get current month start
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)

    # Get user's conversation IDs
    conv_stmt = select(Conversation.id).where(Conversation.user_id == current_user.id)
    conv_result = await db.execute(conv_stmt)
    conv_ids = [row[0] for row in conv_result.all()]

    if not conv_ids:
        # No conversations, return zeros
        return BaseResponse(
            trace_id=ctx.trace_id,
            data=UserUsageResponse(
                total_tokens=0,
                total_messages=0,
                tokens_this_month=0,
                messages_this_month=0,
                estimated_cost=0.0,
                cost_this_month=0.0,
                quota=None,
            ),
        )

    # Total tokens and messages (all time)
    total_stmt = select(
        func.coalesce(func.sum(Message.tokens_used), 0).label("total_tokens"),
        func.count(Message.id).label("total_messages"),
    ).where(Message.conversation_id.in_(conv_ids))

    total_result = await db.execute(total_stmt)
    total_row = total_result.one()
    total_tokens = int(total_row.total_tokens)
    total_messages = int(total_row.total_messages)

    # This month tokens and messages
    month_stmt = select(
        func.coalesce(func.sum(Message.tokens_used), 0).label("tokens"),
        func.count(Message.id).label("messages"),
    ).where(
        and_(
            Message.conversation_id.in_(conv_ids),
            Message.created_at >= month_start,
        )
    )

    month_result = await db.execute(month_stmt)
    month_row = month_result.one()
    tokens_this_month = int(month_row.tokens)
    messages_this_month = int(month_row.messages)

    # Calculate costs
    estimated_cost = (total_tokens / 1_000_000) * COST_PER_1M_TOKENS
    cost_this_month = (tokens_this_month / 1_000_000) * COST_PER_1M_TOKENS

    # Get quota based on tier
    quota = None
    tier_limit = TIER_LIMITS.get(current_user.tier)
    if tier_limit:
        percentage = min(100, int((tokens_this_month / tier_limit) * 100))
        quota = UsageQuota(
            tokens_limit=tier_limit,
            tokens_used=tokens_this_month,
            percentage=percentage,
        )

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserUsageResponse(
            total_tokens=total_tokens,
            total_messages=total_messages,
            tokens_this_month=tokens_this_month,
            messages_this_month=messages_this_month,
            estimated_cost=round(estimated_cost, 2),
            cost_this_month=round(cost_this_month, 2),
            quota=quota,
        ),
    )
