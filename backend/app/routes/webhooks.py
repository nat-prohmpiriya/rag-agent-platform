"""Webhook handlers for external services."""

import json
import logging

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.context import get_context
from app.core.dependencies import get_db
from app.schemas.base import BaseResponse, MessageResponse
from app.services import stripe_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[MessageResponse]:
    """
    Handle Stripe webhook events.

    Supported events:
    - customer.subscription.created -> Create subscription, create LiteLLM key
    - customer.subscription.updated -> Update subscription, update key
    - customer.subscription.deleted -> Cancel subscription, disable key
    - invoice.paid -> Record invoice, reset budget
    - invoice.payment_failed -> Mark subscription as past_due
    """
    ctx = get_context()

    if not settings.stripe_secret_key:
        logger.warning("Stripe not configured, ignoring webhook")
        return BaseResponse(
            trace_id=ctx.trace_id,
            data=MessageResponse(message="Stripe not configured"),
        )

    # Get raw body for signature verification
    payload = await request.body()

    try:
        import stripe

        stripe.api_key = settings.stripe_secret_key

        # Verify webhook signature
        if settings.stripe_webhook_secret and stripe_signature:
            event = await stripe_service.verify_webhook_signature(
                payload=payload,
                signature=stripe_signature,
            )
        else:
            # No webhook secret configured, parse without verification (dev mode)
            logger.warning("Processing webhook without signature verification (dev mode)")
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)

        logger.info(f"Processing Stripe webhook: {event.type}")

        # Process the event using stripe_service
        result = await stripe_service.process_webhook_event(
            db_session=db,
            event=event,
        )

        if result:
            logger.info(f"Successfully processed {event.type}")
        else:
            logger.debug(f"No action taken for {event.type}")

        return BaseResponse(
            trace_id=ctx.trace_id,
            data=MessageResponse(message=f"Processed {event.type}"),
        )

    except stripe_service.StripeError as e:
        logger.error(f"Stripe service error: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ImportError:
        logger.error("Stripe library not installed")
        return BaseResponse(
            trace_id=ctx.trace_id,
            data=MessageResponse(message="Stripe library not installed"),
        )
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed") from e
