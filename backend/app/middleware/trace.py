"""Trace context middleware for request-scoped context."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.context import RequestContext, reset_context, set_context


class TraceContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that creates RequestContext for each request.

    This middleware:
    1. Creates a new RequestContext at the start of each request
    2. Makes it available via get_context() throughout the request
    3. Adds X-Trace-Id header to the response
    4. Resets context after request completes
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Create new context for this request
        ctx = RequestContext()
        set_context(ctx)

        try:
            # Process the request
            response = await call_next(request)

            # Add trace_id to response header
            response.headers["X-Trace-Id"] = ctx.trace_id

            return response
        finally:
            # Reset context after request
            reset_context()
