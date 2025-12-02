"""Base response schemas with trace_id support."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper with trace_id.

    All API endpoints should return this format:
    {
        "trace_id": "abc123...",
        "data": { ... }
    }
    """

    trace_id: str
    data: T


class ErrorResponse(BaseModel):
    """
    Standard error response with trace_id.

    Format:
    {
        "trace_id": "abc123...",
        "error": "Error type",
        "detail": "Detailed message"
    }
    """

    trace_id: str
    error: str
    detail: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str

    model_config = ConfigDict(from_attributes=True)
