"""Request context management using ContextVar."""

from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any

from app.config import settings


@dataclass
class RequestContext:
    """
    Request-scoped context available throughout the request lifecycle.

    Attributes:
        user_id: Authenticated user ID (set after auth middleware)
    """

    user_id: int | None = None
    _extra: dict[str, Any] = field(default_factory=dict)

    @property
    def trace_id(self) -> str:
        """Get trace_id from current OTEL span."""
        if not settings.otel_enabled:
            return "otel-disabled"

        try:
            from opentelemetry import trace

            span = trace.get_current_span()
            span_context = span.get_span_context()
            if span_context.is_valid:
                return format(span_context.trace_id, "032x")
            return "no-active-span"
        except Exception:
            return "trace-error"

    @property
    def span(self):
        """Get current active OTEL span."""
        if not settings.otel_enabled:
            return None

        try:
            from opentelemetry import trace

            return trace.get_current_span()
        except Exception:
            return None

    def set_data(self, data: dict[str, Any]) -> None:
        """Set span data with user context."""
        from app.core.telemetry import span_set_data

        if self.span:
            span_set_data(self.span, {"user_id": self.user_id, **data})

    def set(self, key: str, value: Any) -> None:
        """Set extra context data."""
        self._extra[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get extra context data."""
        return self._extra.get(key, default)


# Global context variable for request-scoped data
_request_context: ContextVar[RequestContext] = ContextVar(
    "request_context", default=RequestContext()
)


def get_context() -> RequestContext:
    """Get current request context."""
    return _request_context.get()


def set_context(ctx: RequestContext) -> None:
    """Set current request context."""
    _request_context.set(ctx)


def reset_context() -> None:
    """Reset context to default (for testing or cleanup)."""
    _request_context.set(RequestContext())
