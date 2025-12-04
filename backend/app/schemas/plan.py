"""Plan schemas for API request/response."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.plan import PlanType


class PlanCreate(BaseModel):
    """Schema for creating a new plan."""

    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    plan_type: PlanType = PlanType.FREE

    # Pricing
    price_monthly: float = Field(0.0, ge=0)
    price_yearly: float | None = Field(None, ge=0)
    currency: str = Field("USD", max_length=3)

    # Limits
    tokens_per_month: int = Field(100000, ge=0)
    requests_per_month: int = Field(100, ge=0)
    credits_per_month: int = Field(100, ge=0)
    requests_per_minute: int = Field(10, ge=1)
    requests_per_day: int = Field(1000, ge=1)
    max_documents: int = Field(10, ge=0)
    max_projects: int = Field(3, ge=0)
    max_agents: int = Field(1, ge=0)

    # Model access
    allowed_models: list[str] = Field(default_factory=list)

    # Features
    features: dict | None = None

    # Status
    is_active: bool = True
    is_public: bool = True

    # Stripe
    stripe_price_id_monthly: str | None = None
    stripe_price_id_yearly: str | None = None
    stripe_product_id: str | None = None


class PlanUpdate(BaseModel):
    """Schema for updating a plan."""

    name: str | None = Field(None, min_length=1, max_length=100)
    display_name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    plan_type: PlanType | None = None

    # Pricing
    price_monthly: float | None = Field(None, ge=0)
    price_yearly: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=3)

    # Limits
    tokens_per_month: int | None = Field(None, ge=0)
    requests_per_month: int | None = Field(None, ge=0)
    credits_per_month: int | None = Field(None, ge=0)
    requests_per_minute: int | None = Field(None, ge=1)
    requests_per_day: int | None = Field(None, ge=1)
    max_documents: int | None = Field(None, ge=0)
    max_projects: int | None = Field(None, ge=0)
    max_agents: int | None = Field(None, ge=0)

    # Model access
    allowed_models: list[str] | None = None

    # Features
    features: dict | None = None

    # Status
    is_active: bool | None = None
    is_public: bool | None = None

    # Stripe
    stripe_price_id_monthly: str | None = None
    stripe_price_id_yearly: str | None = None
    stripe_product_id: str | None = None


class PlanResponse(BaseModel):
    """Schema for plan response."""

    id: uuid.UUID
    name: str
    display_name: str
    description: str | None
    plan_type: PlanType

    # Pricing
    price_monthly: float
    price_yearly: float | None
    currency: str

    # Limits
    tokens_per_month: int
    requests_per_month: int
    credits_per_month: int
    requests_per_minute: int
    requests_per_day: int
    max_documents: int
    max_projects: int
    max_agents: int

    # Model access
    allowed_models: list[str]

    # Features
    features: dict | None

    # Status
    is_active: bool
    is_public: bool

    # Stripe
    stripe_price_id_monthly: str | None
    stripe_price_id_yearly: str | None
    stripe_product_id: str | None

    # Timestamps
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlanWithSubscriberCountResponse(PlanResponse):
    """Schema for plan response with subscriber count."""

    subscriber_count: int = 0


class PlanListResponse(BaseModel):
    """Schema for paginated plan list response."""

    items: list[PlanWithSubscriberCountResponse]
    total: int
    page: int
    per_page: int
    pages: int
