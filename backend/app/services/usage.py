"""Usage tracking service.

Provides functions to record and query usage for request-based billing.
"""

import logging
import uuid
from datetime import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.telemetry import traced
from app.models.usage import RequestType, UsageRecord, UsageSummary
from app.schemas.usage import (
    UsageRecordCreate,
    UsageStatsResponse,
    get_credits_for_model,
)

logger = logging.getLogger(__name__)


def get_current_period() -> str:
    """Get current billing period in YYYY-MM format."""
    return datetime.utcnow().strftime("%Y-%m")


@traced()
async def record_usage(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: UsageRecordCreate,
) -> UsageRecord:
    """
    Record a single usage event.

    This function:
    1. Creates a UsageRecord entry
    2. Updates the UsageSummary for the current period

    Args:
        db: Database session
        user_id: User ID
        data: Usage record data

    Returns:
        Created UsageRecord
    """
    # Calculate credits if not provided
    credits = data.credits_used
    if credits == 1:  # Default value, calculate based on model
        credits = get_credits_for_model(data.model)

    # Create usage record
    record = UsageRecord(
        user_id=user_id,
        request_type=data.request_type,
        model=data.model,
        tokens_input=data.tokens_input,
        tokens_output=data.tokens_output,
        tokens_total=data.tokens_total,
        cost=data.cost,
        credits_used=credits,
        latency_ms=data.latency_ms,
        conversation_id=data.conversation_id,
        message_id=data.message_id,
        agent_id=data.agent_id,
        litellm_call_id=data.litellm_call_id,
        extra_data=data.extra_data,
    )
    db.add(record)

    # Update usage summary (upsert)
    period = get_current_period()
    await update_usage_summary(
        db=db,
        user_id=user_id,
        period=period,
        request_type=data.request_type,
        tokens=data.tokens_total,
        credits=credits,
        cost=data.cost,
    )

    await db.commit()
    await db.refresh(record)

    logger.info(
        f"Recorded usage for user {user_id}: "
        f"model={data.model}, tokens={data.tokens_total}, credits={credits}"
    )

    return record


@traced()
async def update_usage_summary(
    db: AsyncSession,
    user_id: uuid.UUID,
    period: str,
    request_type: RequestType,
    tokens: int,
    credits: int,
    cost: float,
) -> None:
    """
    Update usage summary with incremental values.

    Uses PostgreSQL UPSERT for atomic operation.
    """
    # Map request type to column
    type_column_map = {
        RequestType.CHAT: "chat_requests",
        RequestType.RAG: "rag_requests",
        RequestType.AGENT: "agent_requests",
        RequestType.EMBEDDING: "embedding_requests",
    }
    type_column = type_column_map.get(request_type, "chat_requests")

    # Build upsert statement
    stmt = insert(UsageSummary).values(
        user_id=user_id,
        period=period,
        total_requests=1,
        total_tokens=tokens,
        total_credits=credits,
        total_cost=cost,
        chat_requests=1 if request_type == RequestType.CHAT else 0,
        rag_requests=1 if request_type == RequestType.RAG else 0,
        agent_requests=1 if request_type == RequestType.AGENT else 0,
        embedding_requests=1 if request_type == RequestType.EMBEDDING else 0,
        is_synced=False,
    )

    # On conflict, increment values
    stmt = stmt.on_conflict_do_update(
        constraint="uq_usage_summary_user_period",
        set_={
            "total_requests": UsageSummary.total_requests + 1,
            "total_tokens": UsageSummary.total_tokens + tokens,
            "total_credits": UsageSummary.total_credits + credits,
            "total_cost": UsageSummary.total_cost + cost,
            type_column: getattr(UsageSummary, type_column) + 1,
            "is_synced": False,
            "updated_at": func.now(),
        },
    )

    await db.execute(stmt)


@traced()
async def get_usage_summary(
    db: AsyncSession,
    user_id: uuid.UUID,
    period: str | None = None,
) -> UsageSummary | None:
    """
    Get usage summary for a user and period.

    Args:
        db: Database session
        user_id: User ID
        period: Billing period (YYYY-MM), defaults to current

    Returns:
        UsageSummary or None if not found
    """
    if period is None:
        period = get_current_period()

    stmt = select(UsageSummary).where(
        and_(
            UsageSummary.user_id == user_id,
            UsageSummary.period == period,
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


@traced()
async def get_or_create_usage_summary(
    db: AsyncSession,
    user_id: uuid.UUID,
    period: str | None = None,
) -> UsageSummary:
    """
    Get or create usage summary for a user and period.

    Args:
        db: Database session
        user_id: User ID
        period: Billing period (YYYY-MM), defaults to current

    Returns:
        UsageSummary
    """
    if period is None:
        period = get_current_period()

    summary = await get_usage_summary(db, user_id, period)

    if summary is None:
        summary = UsageSummary(
            user_id=user_id,
            period=period,
            total_requests=0,
            total_tokens=0,
            total_credits=0,
            total_cost=0.0,
            chat_requests=0,
            rag_requests=0,
            agent_requests=0,
            embedding_requests=0,
            is_synced=True,
        )
        db.add(summary)
        await db.commit()
        await db.refresh(summary)

    return summary


@traced()
async def get_usage_records(
    db: AsyncSession,
    user_id: uuid.UUID,
    period: str | None = None,
    request_type: RequestType | None = None,
    model: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[UsageRecord]:
    """
    Get usage records for a user with optional filters.

    Args:
        db: Database session
        user_id: User ID
        period: Filter by period (YYYY-MM)
        request_type: Filter by request type
        model: Filter by model
        limit: Maximum records to return
        offset: Offset for pagination

    Returns:
        List of UsageRecord
    """
    conditions = [UsageRecord.user_id == user_id]

    if period:
        # Filter by month
        year, month = period.split("-")
        start_date = datetime(int(year), int(month), 1)
        if int(month) == 12:
            end_date = datetime(int(year) + 1, 1, 1)
        else:
            end_date = datetime(int(year), int(month) + 1, 1)
        conditions.append(UsageRecord.created_at >= start_date)
        conditions.append(UsageRecord.created_at < end_date)

    if request_type:
        conditions.append(UsageRecord.request_type == request_type)

    if model:
        conditions.append(UsageRecord.model == model)

    stmt = (
        select(UsageRecord)
        .where(and_(*conditions))
        .order_by(UsageRecord.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


@traced()
async def get_usage_by_model(
    db: AsyncSession,
    user_id: uuid.UUID,
    period: str | None = None,
) -> dict[str, int]:
    """
    Get usage breakdown by model.

    Args:
        db: Database session
        user_id: User ID
        period: Billing period (YYYY-MM), defaults to current

    Returns:
        Dict mapping model name to request count
    """
    if period is None:
        period = get_current_period()

    # Filter by month
    year, month = period.split("-")
    start_date = datetime(int(year), int(month), 1)
    if int(month) == 12:
        end_date = datetime(int(year) + 1, 1, 1)
    else:
        end_date = datetime(int(year), int(month) + 1, 1)

    stmt = (
        select(UsageRecord.model, func.count(UsageRecord.id))
        .where(
            and_(
                UsageRecord.user_id == user_id,
                UsageRecord.created_at >= start_date,
                UsageRecord.created_at < end_date,
            )
        )
        .group_by(UsageRecord.model)
    )

    result = await db.execute(stmt)
    return {row[0]: row[1] for row in result.all()}


@traced()
async def get_usage_by_request_type(
    db: AsyncSession,
    user_id: uuid.UUID,
    period: str | None = None,
) -> dict[str, int]:
    """
    Get usage breakdown by request type.

    Args:
        db: Database session
        user_id: User ID
        period: Billing period (YYYY-MM), defaults to current

    Returns:
        Dict mapping request type to request count
    """
    summary = await get_usage_summary(db, user_id, period)

    if summary is None:
        return {
            "chat": 0,
            "rag": 0,
            "agent": 0,
            "embedding": 0,
        }

    return {
        "chat": summary.chat_requests,
        "rag": summary.rag_requests,
        "agent": summary.agent_requests,
        "embedding": summary.embedding_requests,
    }


@traced()
async def get_usage_stats(
    db: AsyncSession,
    user_id: uuid.UUID,
    requests_limit: int,
    credits_limit: int,
    tokens_limit: int,
) -> UsageStatsResponse:
    """
    Get comprehensive usage statistics for a user.

    Args:
        db: Database session
        user_id: User ID
        requests_limit: User's request limit from plan
        credits_limit: User's credit limit from plan
        tokens_limit: User's token limit from plan

    Returns:
        UsageStatsResponse with current usage and limits
    """
    period = get_current_period()
    summary = await get_or_create_usage_summary(db, user_id, period)

    # Calculate remaining and percentages
    requests_remaining = max(0, requests_limit - summary.total_requests)
    credits_remaining = max(0, credits_limit - summary.total_credits)
    tokens_remaining = max(0, tokens_limit - summary.total_tokens)

    requests_pct = (summary.total_requests / requests_limit * 100) if requests_limit > 0 else 0
    credits_pct = (summary.total_credits / credits_limit * 100) if credits_limit > 0 else 0
    tokens_pct = (summary.total_tokens / tokens_limit * 100) if tokens_limit > 0 else 0

    # Get breakdowns
    by_model = await get_usage_by_model(db, user_id, period)
    by_type = await get_usage_by_request_type(db, user_id, period)

    # Check if exceeded or warning
    is_requests_exceeded = summary.total_requests >= requests_limit
    is_credits_exceeded = summary.total_credits >= credits_limit
    is_tokens_exceeded = summary.total_tokens >= tokens_limit
    is_warning = (
        requests_pct >= 80 or credits_pct >= 80 or tokens_pct >= 80
    ) and not (is_requests_exceeded or is_credits_exceeded or is_tokens_exceeded)

    return UsageStatsResponse(
        period=period,
        requests_used=summary.total_requests,
        requests_limit=requests_limit,
        requests_remaining=requests_remaining,
        requests_percentage=round(requests_pct, 1),
        credits_used=summary.total_credits,
        credits_limit=credits_limit,
        credits_remaining=credits_remaining,
        credits_percentage=round(credits_pct, 1),
        tokens_used=summary.total_tokens,
        tokens_limit=tokens_limit,
        tokens_remaining=tokens_remaining,
        tokens_percentage=round(tokens_pct, 1),
        total_cost=float(summary.total_cost),
        by_request_type=by_type,
        by_model=by_model,
        is_requests_exceeded=is_requests_exceeded,
        is_credits_exceeded=is_credits_exceeded,
        is_tokens_exceeded=is_tokens_exceeded,
        is_warning=is_warning,
    )
