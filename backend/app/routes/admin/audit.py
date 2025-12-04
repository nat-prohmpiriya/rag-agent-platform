"""Admin Audit Log API endpoints."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.admin import (
    AuditLogListResponse,
    AuditLogResponse,
)
from app.schemas.base import BaseResponse
from app.services import audit_log as audit_service

router = APIRouter(prefix="/audit", tags=["admin-audit"])


@router.get("")
async def list_audit_logs(
    page: int = 1,
    per_page: int = 20,
    action: str | None = None,
    admin_id: uuid.UUID | None = None,
    target_type: str | None = None,
    target_id: uuid.UUID | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[AuditLogListResponse]:
    """
    List audit logs with optional filters (admin only).

    Filters:
    - action: Filter by action type (e.g., user_suspend, plan_update)
    - admin_id: Filter by admin who performed the action
    - target_type: Filter by target entity type (user, plan, subscription)
    - target_id: Filter by specific target entity ID
    - start_date: Filter logs from this date
    - end_date: Filter logs until this date
    - search: Search in description
    """
    ctx = get_context()

    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    logs, total = await audit_service.get_audit_logs(
        db=db,
        page=page,
        per_page=per_page,
        action=action,
        admin_id=admin_id,
        target_type=target_type,
        target_id=target_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
    )

    pages = audit_service.calculate_pages(total, per_page)

    items = [AuditLogResponse(**log) for log in logs]

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=AuditLogListResponse(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
        ),
    )


@router.get("/actions")
async def get_action_types(
    _admin: User = Depends(require_admin),
) -> BaseResponse[list[dict]]:
    """Get all available audit action types for filter dropdown (admin only)."""
    ctx = get_context()

    action_types = await audit_service.get_action_types()

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=action_types,
    )


@router.get("/target-types")
async def get_target_types(
    _admin: User = Depends(require_admin),
) -> BaseResponse[list[str]]:
    """Get all available target types for filter dropdown (admin only)."""
    ctx = get_context()

    target_types = await audit_service.get_target_types()

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=target_types,
    )


@router.get("/admins")
async def get_admins(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[list[dict]]:
    """Get all admins for filter dropdown (admin only)."""
    ctx = get_context()

    admins = await audit_service.get_admins_for_filter(db)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=admins,
    )


@router.get("/{log_id}")
async def get_audit_log(
    log_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[AuditLogResponse]:
    """Get a single audit log entry by ID (admin only)."""
    ctx = get_context()

    log = await audit_service.get_audit_log_by_id(db=db, log_id=log_id)

    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=AuditLogResponse(**log),
    )
