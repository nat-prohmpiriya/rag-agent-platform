"""Admin Plan API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_db, require_admin
from app.models.audit_log import AuditAction
from app.models.user import User
from app.schemas.base import BaseResponse, MessageResponse
from app.schemas.plan import (
    PlanCreate,
    PlanListResponse,
    PlanResponse,
    PlanUpdate,
    PlanWithSubscriberCountResponse,
)
from app.services import audit_log as audit_service
from app.services import plan as plan_service

router = APIRouter(prefix="/plans", tags=["admin-plans"])


@router.get("")
async def list_plans(
    page: int = 1,
    per_page: int = 20,
    include_inactive: bool = True,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[PlanListResponse]:
    """List all plans with subscriber counts (admin only)."""
    ctx = get_context()

    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    plans_with_counts, total = await plan_service.get_plans_with_subscriber_counts(
        db=db,
        page=page,
        per_page=per_page,
        include_inactive=include_inactive,
    )

    pages = plan_service.calculate_pages(total, per_page)

    items = [
        PlanWithSubscriberCountResponse(
            **PlanResponse.model_validate(plan).model_dump(),
            subscriber_count=count,
        )
        for plan, count in plans_with_counts
    ]

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=PlanListResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )


@router.post("", status_code=201)
async def create_plan(
    data: PlanCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> BaseResponse[PlanResponse]:
    """Create a new plan (admin only)."""
    ctx = get_context()

    # Check if plan name already exists
    existing = await plan_service.get_plan_by_name(db, data.name)
    if existing:
        raise HTTPException(status_code=409, detail="Plan name already exists")

    plan = await plan_service.create_plan(db=db, data=data)

    # Audit log
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    await audit_service.create_audit_log(
        db=db,
        admin_id=admin.id,
        action=AuditAction.PLAN_CREATE.value,
        description=f"Created plan {data.name}",
        target_type="plan",
        target_id=plan.id,
        details={"plan_name": data.name, "price_monthly": data.price_monthly},
        ip_address=ip_address,
        user_agent=user_agent,
    )

    await db.commit()
    await db.refresh(plan)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=PlanResponse.model_validate(plan),
    )


@router.get("/{plan_id}")
async def get_plan(
    plan_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[PlanWithSubscriberCountResponse]:
    """Get a plan by ID with subscriber count (admin only)."""
    ctx = get_context()

    plan = await plan_service.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    subscriber_count = await plan_service.get_subscriber_count(db, plan_id)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=PlanWithSubscriberCountResponse(
            **PlanResponse.model_validate(plan).model_dump(),
            subscriber_count=subscriber_count,
        ),
    )


@router.put("/{plan_id}")
async def update_plan(
    plan_id: uuid.UUID,
    data: PlanUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> BaseResponse[PlanResponse]:
    """Update a plan (admin only)."""
    ctx = get_context()

    # Check if new name conflicts with existing plan
    if data.name:
        existing = await plan_service.get_plan_by_name(db, data.name)
        if existing and existing.id != plan_id:
            raise HTTPException(status_code=409, detail="Plan name already exists")

    plan = await plan_service.update_plan(db=db, plan_id=plan_id, data=data)

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Audit log
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    await audit_service.create_audit_log(
        db=db,
        admin_id=admin.id,
        action=AuditAction.PLAN_UPDATE.value,
        description=f"Updated plan {plan.name}",
        target_type="plan",
        target_id=plan_id,
        details=data.model_dump(exclude_unset=True),
        ip_address=ip_address,
        user_agent=user_agent,
    )

    await db.commit()
    await db.refresh(plan)

    # TODO: Sync LiteLLM keys when plan limits change
    # If tokens_per_month, requests_per_minute, requests_per_day, or allowed_models changed,
    # we need to update the LiteLLM keys for all active subscribers

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=PlanResponse.model_validate(plan),
    )


@router.delete("/{plan_id}")
async def delete_plan(
    plan_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> BaseResponse[MessageResponse]:
    """Delete a plan (admin only). Cannot delete plans with active subscribers."""
    ctx = get_context()

    # Get plan info before deletion for audit log
    plan = await plan_service.get_plan(db, plan_id)
    plan_name = plan.name if plan else "unknown"

    try:
        deleted = await plan_service.delete_plan(db=db, plan_id=plan_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if not deleted:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Audit log
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    await audit_service.create_audit_log(
        db=db,
        admin_id=admin.id,
        action=AuditAction.PLAN_DELETE.value,
        description=f"Deleted plan {plan_name}",
        target_type="plan",
        target_id=plan_id,
        details={"deleted_plan_name": plan_name},
        ip_address=ip_address,
        user_agent=user_agent,
    )

    await db.commit()

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=MessageResponse(message="Plan deleted successfully"),
    )
