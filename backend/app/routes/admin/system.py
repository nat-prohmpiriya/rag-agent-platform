"""Admin System Health API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.admin import SystemHealthResponse, SystemMetrics
from app.schemas.base import BaseResponse
from app.services import system_health

router = APIRouter(prefix="/system", tags=["admin-system"])


@router.get("/health")
async def get_system_health_status(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[SystemHealthResponse]:
    """Get system health status (admin only)."""
    ctx = get_context()

    health = await system_health.get_system_health(db)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=health,
    )


@router.get("/metrics")
async def get_system_metrics_data(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> BaseResponse[SystemMetrics]:
    """Get system performance metrics (admin only)."""
    ctx = get_context()

    metrics = await system_health.get_system_metrics(db)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=metrics,
    )
