"""Statistics schemas."""

from pydantic import BaseModel


class UserStatsResponse(BaseModel):
    """Schema for user usage statistics."""

    conversations_count: int
    documents_count: int
    agents_count: int
    total_messages: int


class UsageQuota(BaseModel):
    """Token quota information."""

    tokens_limit: int
    tokens_used: int
    percentage: int


class UserUsageResponse(BaseModel):
    """Schema for user token usage statistics."""

    total_tokens: int
    total_messages: int
    tokens_this_month: int
    messages_this_month: int
    estimated_cost: float
    cost_this_month: float
    quota: UsageQuota | None = None


class QuotaStatusResponse(BaseModel):
    """Single quota status."""

    limit: int
    used: int
    remaining: int
    percentage: float
    is_exceeded: bool
    is_warning: bool
    is_unlimited: bool = False


class UserQuotaResponse(BaseModel):
    """Complete quota information for user."""

    user_id: str
    plan_name: str
    plan_type: str
    has_active_subscription: bool
    tokens: QuotaStatusResponse
    documents: QuotaStatusResponse
    projects: QuotaStatusResponse
