"""OpenTelemetry setup and utilities."""

import json
import logging
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

from app.config import settings

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def setup_telemetry() -> None:
    """Initialize OpenTelemetry tracing."""
    if not settings.otel_enabled:
        logger.info("OpenTelemetry is disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.sdk.resources import SERVICE_NAME, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Create resource with service info
        resource = Resource(
            attributes={
                SERVICE_NAME: settings.otel_service_name,
                "service.version": "0.1.0",
                "deployment.environment": settings.app_env,
            }
        )

        # Setup tracer provider
        provider = TracerProvider(resource=resource)

        # Configure OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=settings.otel_exporter_endpoint,
            insecure=True,  # Use False in production with TLS
        )

        # Add span processor
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        logger.info(
            f"OpenTelemetry initialized: service={settings.otel_service_name}, "
            f"endpoint={settings.otel_exporter_endpoint}"
        )
    except ImportError:
        logger.warning("OpenTelemetry packages not installed, tracing disabled")
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}")


def instrument_app(app) -> None:
    """Instrument FastAPI app with OpenTelemetry."""
    if not settings.otel_enabled:
        return

    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        # FastAPI auto-instrumentation
        FastAPIInstrumentor.instrument_app(app)

        # HTTPX (for LiteLLM calls)
        HTTPXClientInstrumentor().instrument()

        logger.info("FastAPI and HTTPX instrumented with OpenTelemetry")
    except ImportError:
        logger.warning("OpenTelemetry instrumentation packages not installed")
    except Exception as e:
        logger.error(f"Failed to instrument app: {e}")


def instrument_database(engine) -> None:
    """Instrument SQLAlchemy engine with OpenTelemetry."""
    if not settings.otel_enabled:
        return

    try:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
        logger.info("SQLAlchemy instrumented with OpenTelemetry")
    except ImportError:
        logger.warning("SQLAlchemy instrumentation package not installed")
    except Exception as e:
        logger.error(f"Failed to instrument database: {e}")


def get_tracer(name: str = __name__):
    """Get a tracer instance for creating spans."""
    if not settings.otel_enabled:
        return None

    try:
        from opentelemetry import trace

        return trace.get_tracer(name)
    except ImportError:
        return None


def span_set_data(span, data: dict[str, Any]) -> None:
    """
    Set span attribute with JSON data.

    Args:
        span: OTEL span instance
        data: Dictionary to store as JSON string
    """
    if span is None:
        return

    try:
        span.set_attribute(
            "data", json.dumps(data, ensure_ascii=False, default=str)
        )
    except Exception as e:
        logger.warning(f"Failed to set span data: {e}")


def traced(
    name: str | None = None,
    skip_input: bool = False,
    skip_output: bool = False,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to trace function execution with OTEL.

    Args:
        name: Custom span name (defaults to function name)
        skip_input: Skip logging input parameters (for sensitive data)
        skip_output: Skip logging output (for large responses)

    Usage:
        @traced()
        async def create_order(data: OrderCreate) -> Order:
            ...

        @traced(skip_input=True)  # For functions with sensitive data
        async def authenticate_user(email: str, password: str) -> User:
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        if not settings.otel_enabled:
            return func

        span_name = name or func.__name__
        tracer = get_tracer(func.__module__)

        if tracer is None:
            return func

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with tracer.start_as_current_span(span_name) as span:
                # Log input (skip sensitive data)
                if not skip_input and kwargs:
                    input_data = _serialize_kwargs(kwargs)
                    span_set_data(span, {"input": input_data})

                try:
                    result = await func(*args, **kwargs)

                    # Log output
                    if not skip_output and result is not None:
                        output_data = _serialize_result(result)
                        span_set_data(span, {"output": output_data})

                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with tracer.start_as_current_span(span_name) as span:
                if not skip_input and kwargs:
                    input_data = _serialize_kwargs(kwargs)
                    span_set_data(span, {"input": input_data})

                try:
                    result = func(*args, **kwargs)

                    if not skip_output and result is not None:
                        output_data = _serialize_result(result)
                        span_set_data(span, {"output": output_data})

                    return result
                except Exception as e:
                    span.record_exception(e)
                    raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def _serialize_kwargs(kwargs: dict) -> dict:
    """Serialize function kwargs for logging."""
    result = {}
    for key, value in kwargs.items():
        # Skip db sessions and other non-serializable objects
        if key in ("db", "session", "request", "background_tasks"):
            continue
        try:
            if hasattr(value, "model_dump"):
                result[key] = value.model_dump()
            elif hasattr(value, "__dict__"):
                result[key] = str(value)
            else:
                result[key] = value
        except Exception:
            result[key] = str(value)
    return result


def _serialize_result(result: Any) -> Any:
    """Serialize function result for logging."""
    try:
        if hasattr(result, "model_dump"):
            return result.model_dump()
        elif isinstance(result, (dict, list, str, int, float, bool)):
            return result
        else:
            return str(result)
    except Exception:
        return str(result)
