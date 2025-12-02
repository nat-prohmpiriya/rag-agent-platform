"""Middleware package."""

from app.middleware.trace import TraceContextMiddleware

__all__ = ["TraceContextMiddleware"]
