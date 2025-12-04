"""Billing routes for checkout and customer portal."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_context
from app.core.dependencies import get_current_user, get_db
from app.models.plan import Plan
from app.models.user import User
from app.schemas.base import BaseResponse
from app.services import stripe_service

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutRequest(BaseModel):
    """Request to create a checkout session."""

    plan_id: uuid.UUID
    billing_interval: str = "monthly"  # "monthly" or "yearly"
    success_url: str | None = None
    cancel_url: str | None = None


class CheckoutResponse(BaseModel):
    """Response with checkout session URL."""

    session_id: str
    url: str


class PortalRequest(BaseModel):
    """Request to create a customer portal session."""

    return_url: str | None = None


class PortalResponse(BaseModel):
    """Response with portal session URL."""

    url: str


@router.post("/checkout")
async def create_checkout(
    request: CheckoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[CheckoutResponse]:
    """
    Create a Stripe checkout session for subscribing to a plan.

    The user will be redirected to Stripe's hosted checkout page.
    """
    ctx = get_context()

    # Get the plan
    result = await db.execute(select(Plan).where(Plan.id == request.plan_id))
    plan = result.scalar_one_or_none()

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if not plan.is_active:
        raise HTTPException(status_code=400, detail="Plan is not available")

    # Validate billing interval
    if request.billing_interval not in ("monthly", "yearly"):
        raise HTTPException(status_code=400, detail="Invalid billing interval")

    try:
        session = await stripe_service.create_checkout_session(
            user=user,
            plan=plan,
            billing_interval=request.billing_interval,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )

        return BaseResponse(
            trace_id=ctx.trace_id,
            data=CheckoutResponse(
                session_id=session["session_id"],
                url=session["url"],
            ),
        )
    except stripe_service.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/portal")
async def create_portal_session(
    request: PortalRequest,
    user: User = Depends(get_current_user),
) -> BaseResponse[PortalResponse]:
    """
    Create a Stripe customer portal session.

    The user will be redirected to Stripe's customer portal where they can:
    - View and manage their subscription
    - Update payment methods
    - View invoice history
    - Cancel subscription
    """
    ctx = get_context()

    try:
        session = await stripe_service.create_customer_portal_session(
            user=user,
            return_url=request.return_url,
        )

        return BaseResponse(
            trace_id=ctx.trace_id,
            data=PortalResponse(url=session["url"]),
        )
    except stripe_service.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/plans")
async def get_available_plans(
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[list[dict]]:
    """
    Get all available billing plans.

    Returns active, public plans with pricing information.
    """
    ctx = get_context()

    result = await db.execute(
        select(Plan).where(Plan.is_active == True, Plan.is_public == True)  # noqa: E712
    )
    plans = result.scalars().all()

    plan_list = [
        {
            "id": str(plan.id),
            "name": plan.name,
            "display_name": plan.display_name,
            "description": plan.description,
            "plan_type": plan.plan_type.value,
            "price_monthly": float(plan.price_monthly),
            "price_yearly": float(plan.price_yearly) if plan.price_yearly else None,
            "currency": plan.currency,
            "tokens_per_month": plan.tokens_per_month,
            "requests_per_minute": plan.requests_per_minute,
            "requests_per_day": plan.requests_per_day,
            "max_documents": plan.max_documents,
            "max_projects": plan.max_projects,
            "max_agents": plan.max_agents,
            "allowed_models": plan.allowed_models,
            "features": plan.features,
        }
        for plan in plans
    ]

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=plan_list,
    )
