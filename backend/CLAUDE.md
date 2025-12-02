# Backend - Claude Instructions

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI |
| **Language** | Python 3.12+ |
| **Package Manager** | uv |
| **Database** | PostgreSQL + SQLAlchemy (async) |
| **Migrations** | Alembic |
| **Validation** | Pydantic v2 |
| **Auth** | JWT (python-jose) + bcrypt |
| **Linter/Formatter** | Ruff |
| **Tracing** | OpenTelemetry + Jaeger |

---

## Project Structure

```
app/
├── main.py              # FastAPI entrypoint
├── config.py            # Environment settings (pydantic-settings)
│
├── schemas/             # Pydantic schemas (Request/Response/Internal DTOs)
│   ├── __init__.py
│   ├── base.py          # BaseResponse[T], ErrorResponse (with trace_id)
│   ├── user.py
│   ├── auth.py
│   ├── project.py
│   ├── chat.py
│   └── document.py
│
├── routes/              # API endpoints (thin layer, call services)
│   ├── __init__.py
│   ├── health.py
│   ├── auth.py
│   ├── users.py
│   ├── projects.py
│   ├── chat.py
│   └── documents.py
│
├── services/            # Business logic + DB operations
│   ├── __init__.py
│   ├── auth.py
│   ├── user.py
│   ├── project.py
│   ├── chat.py
│   └── document.py
│
├── models/              # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── base.py
│   ├── user.py
│   ├── project.py
│   ├── conversation.py
│   └── document.py
│
├── providers/           # External integrations
│   ├── __init__.py
│   ├── llm.py           # LiteLLM client
│   ├── vector_store.py  # ChromaDB client
│   └── embeddings.py    # Sentence-transformers
│
├── middleware/          # Request middleware
│   ├── __init__.py
│   └── trace.py         # Create RequestContext per request
│
└── core/                # Shared utilities
    ├── __init__.py
    ├── database.py      # DB connection, session
    ├── security.py      # JWT, password hashing
    ├── dependencies.py  # FastAPI dependencies (get_db, get_current_user)
    ├── exceptions.py    # Custom exceptions
    ├── telemetry.py     # OTEL setup, span helpers, @traced decorator
    └── context.py       # RequestContext (user_id, trace_id)
```

---

## Architecture Rules

1. **Routes**: Only handle HTTP, validate input, call services
2. **Services**: Business logic, DB queries, no HTTP knowledge
3. **Models**: Database tables only, no business logic
4. **Schemas**: Request/Response validation, separate from Models
5. **Providers**: External API clients (stateless)
6. **Core**: Shared utilities used across all layers
7. **Middleware**: Request-level concerns (tracing, context)

### Data Flow

```
Request --> Middleware --> Routes --> Services --> Models/Providers --> Response
               |             |           |
          RequestContext  Schemas     Database
               |
           trace_id
```

---

## Observability (OTEL Tracing)

### Design Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Logging | ❌ ไม่ใช้แยก | ใช้ Trace แทน (ได้ timing + flow ด้วย) |
| Trace Backend | Jaeger | ฟรี, ง่าย, UI ดี |
| Response | BaseResponse[T] | trace_id ในทุก response body |
| Context | ContextVar | ไม่ต้องส่ง param ทุก function |

### RequestContext

```python
from contextvars import ContextVar
from dataclasses import dataclass
from opentelemetry import trace

@dataclass
class RequestContext:
    user_id: int | None = None

    @property
    def trace_id(self) -> str:
        span = trace.get_current_span()
        return format(span.get_span_context().trace_id, "032x")

    @property
    def span(self):
        return trace.get_current_span()

    def set_data(self, data: dict) -> None:
        span_set_data(self.span, {"user_id": self.user_id, **data})

# Global context
_request_context: ContextVar[RequestContext] = ContextVar("request_context")

def get_context() -> RequestContext:
    return _request_context.get()
```

### BaseResponse Schema

ทุก API response ต้อง return `BaseResponse[T]` เพื่อให้มี trace_id:

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    trace_id: str
    data: T

class ErrorResponse(BaseModel):
    trace_id: str
    error: str
    detail: str | None = None
```

**Usage in routes:**

```python
@router.get("/users/me")
async def get_me(current_user: User = Depends(get_current_user)) -> BaseResponse[UserResponse]:
    ctx = get_context()
    return BaseResponse(
        trace_id=ctx.trace_id,
        data=UserResponse.model_validate(current_user),
    )
```

**Response format:**

```json
{
  "trace_id": "abc123def456789...",
  "data": {
    "id": 1,
    "email": "test@example.com"
  }
}
```

### Streaming Responses (LLM Chat)

For LLM chat endpoints, use `StreamingResponse` instead of `BaseResponse`:

- **DO NOT** use `BaseResponse` for streaming
- **DO** inject `trace_id` in the `X-Trace-Id` header instead
- Use Server-Sent Events (SSE) format

```python
from fastapi.responses import StreamingResponse

@router.post("/chat/stream")
async def chat_stream(
    request: Request,
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    ctx = get_context()

    async def event_generator():
        async for chunk in llm_service.chat_stream(data.message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"X-Trace-Id": ctx.trace_id}
    )
```

### @traced Decorator

ใช้ `@traced()` decorator สำหรับ track input/output ใน function สำคัญ:

```python
from app.core.telemetry import traced

@traced()
async def create_order(db: AsyncSession, data: OrderCreate) -> Order:
    # Auto track: input (data), output (Order), timing
    ...

@traced(skip_input=True)  # สำหรับ function ที่มี sensitive data
async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    ...
```

### Manual Span

สำหรับ custom tracing:

```python
from app.core.telemetry import get_tracer

tracer = get_tracer(__name__)

async def process_payment(amount: float) -> str:
    with tracer.start_as_current_span("payment.process") as span:
        span.set_attribute("payment.amount", amount)

        span.add_event("Validating card")
        # validate...

        span.add_event("Charging card")
        # charge...

        span.add_event("Payment completed", {"transaction_id": "TXN-123"})
        return "TXN-123"
```

### Span Data Helper

```python
import json
from opentelemetry.trace import Span

def span_set_data(span: Span, data: dict) -> None:
    """Set span attribute with JSON data."""
    span.set_attribute(
        "data",
        json.dumps(data, ensure_ascii=False, default=str)
    )
```

### Config

```python
# config.py
class Settings(BaseSettings):
    # ... existing settings ...

    # OpenTelemetry
    otel_enabled: bool = True
    otel_service_name: str = "rag-agent-backend"
    otel_exporter_endpoint: str = "http://localhost:4317"
```

### Environment Variables

```bash
# OpenTelemetry
OTEL_ENABLED=true
OTEL_SERVICE_NAME=rag-agent-backend
OTEL_EXPORTER_ENDPOINT=http://jaeger:4317
```

---

## Python Style Guide

### Data Structures

| Avoid | Use Instead |
|-------|-------------|
| `dict` for structured data | `dataclass` / `Pydantic BaseModel` |
| `Union[str, None]` | `str \| None` |
| No type hints | Type hints on all functions |
| `-> dict` | `-> UserResponse` (specific type) |
| `Any` | Specific types |
| `"Hello " + name` | `f"Hello {name}"` |
| Magic numbers | `UPPER_CASE` constants |

### Function Parameters Rule

| Parameters | Approach |
|------------|----------|
| 1-3 params | Normal parameters OK |
| 4+ params | Use Dataclass / Pydantic BaseModel |

```python
# [Bad] - too many parameters
def create_user(
    username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    is_active: bool = True,
) -> User:
    pass

# [Good] - use Pydantic model
class CreateUserInput(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    is_active: bool = True

def create_user(data: CreateUserInput) -> User:
    pass
```

### Pydantic v2 Config

Always enable ORM mode for response schemas:

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    email: str
    username: str

    # Pydantic v2 syntax (NOT class Config: orm_mode = True)
    model_config = ConfigDict(from_attributes=True)
```

### Schema Naming Convention

| Suffix | Use For | Example |
|--------|---------|---------|
| `*Create` | API Request (POST) | `UserCreate` |
| `*Update` | API Request (PUT/PATCH) | `UserUpdate` |
| `*Response` | API Response | `UserResponse` |
| `*Filter` | Internal query params | `UserFilter` |
| `*Input` | Internal service input | `CreateUserInput` |
| `*Data` | Internal data transfer | `UserData` |

### Async/Await

- Use `async/await` for all DB and HTTP operations
- Use `httpx.AsyncClient` for HTTP calls
- Use `asyncpg` driver for PostgreSQL

### Dependency Injection

- Use FastAPI `Depends()` for dependencies
- Define dependencies in `core/dependencies.py`

```python
# core/dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    # verify token and return user
    ...

# routes/users.py
@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    return current_user
```

---

## Error Handling

### Use Custom Exceptions

```python
# core/exceptions.py
class AppException(Exception):
    """Base exception for application"""
    pass

class NotFoundError(AppException):
    def __init__(self, resource: str, id: int | str):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} with id {id} not found")

class InvalidCredentialsError(AppException):
    pass

class PermissionDeniedError(AppException):
    pass
```

### Exception Handler in main.py

```python
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})
```

---

## Import Order

Follow PEP8 import ordering:

```python
# 1. Standard library
import os
from datetime import datetime
from typing import Optional

# 2. Third-party packages
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import httpx

# 3. Local imports
from app.config import settings
from app.models.user import User
from app.services.auth import AuthService
```

---

## Docstrings

### When to Add

| Case | Add Docstring? |
|------|----------------|
| Public API / Services | Yes |
| Complex logic | Yes |
| Simple/obvious function | No |
| Private helper (`_func`) | No |

### Format

```python
def calculate_price(base: float, tax: float, discount: float) -> float:
    """
    Calculate final price after tax and discount.

    Args:
        base: Base price before tax
        tax: Tax amount
        discount: Discount amount

    Returns:
        Final price after calculations
    """
    return (base + tax) - discount
```

---

## Code Formatting

### Ruff Configuration

Line length: 88 (Black default)

```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py312"
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "SIM", # flake8-simplify
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

---

## Commands

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --port 8000

# Run migrations
uv run alembic upgrade head

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Lint code
uv run ruff check .

# Fix lint issues
uv run ruff check . --fix

# Format code
uv run ruff format .

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app
```

---

## Environment Variables

Required in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname

# LiteLLM
LITELLM_API_URL=http://localhost:4000
LITELLM_API_KEY=sk-xxx

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# App
APP_ENV=development
DEBUG=true

# OpenTelemetry
OTEL_ENABLED=true
OTEL_SERVICE_NAME=rag-agent-backend
OTEL_EXPORTER_ENDPOINT=http://localhost:4317
```

---

## Database Migrations

### Create Migration

```bash
# After changing models
uv run alembic revision --autogenerate -m "add user table"
```

### Run Migrations

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

---

## Testing

### Test Structure

```
tests/
├── conftest.py          # Fixtures
├── test_routes/
│   ├── test_auth.py
│   └── test_users.py
└── test_services/
    ├── test_auth.py
    └── test_user.py
```

### Naming Convention

- Test files: `test_*.py`
- Test functions: `test_*`
- Use descriptive names: `test_create_user_with_valid_data_returns_user`

---

## Testing Strategy

### Test Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | pytest + pytest-asyncio | Async test support |
| **Fixtures** | Factory Boy | Test data generation |
| **Coverage** | pytest-cov | Coverage report |
| **API Testing** | httpx + TestClient | Integration tests |
| **Mocking** | pytest-mock | External service mocking |

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── factories.py             # Factory Boy factories
├── unit/
│   ├── test_services/
│   │   ├── test_auth.py
│   │   └── test_user.py
│   └── test_utils/
│       └── test_security.py
├── integration/
│   ├── test_routes/
│   │   ├── test_auth.py
│   │   └── test_health.py
│   └── conftest.py          # Test DB setup
└── fixtures/
    └── data.json            # Test data
```

### Coverage Target

- **Minimum**: 80%
- **Services**: 90%+
- **Routes**: 80%+
- **Utils**: 90%+

### Test Examples

**Unit Test (Service):**

```python
# tests/unit/test_services/test_auth.py
import pytest
from unittest.mock import AsyncMock

from app.services.auth import authenticate_user
from app.core.exceptions import InvalidCredentialsError


@pytest.mark.asyncio
async def test_authenticate_user_with_valid_credentials(db_session, user_factory):
    # Arrange
    user = await user_factory.create(password="correct_password")

    # Act
    result = await authenticate_user(db_session, user.email, "correct_password")

    # Assert
    assert result.id == user.id
    assert result.email == user.email


@pytest.mark.asyncio
async def test_authenticate_user_with_invalid_password_raises_error(db_session, user_factory):
    # Arrange
    user = await user_factory.create(password="correct_password")

    # Act & Assert
    with pytest.raises(InvalidCredentialsError):
        await authenticate_user(db_session, user.email, "wrong_password")
```

**Integration Test (Route):**

```python
# tests/integration/test_routes/test_auth.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_returns_tokens(client: AsyncClient, user_factory):
    # Arrange
    user = await user_factory.create(password="test_password")

    # Act
    response = await client.post("/api/auth/login", json={
        "email": user.email,
        "password": "test_password"
    })

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "trace_id" in data
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]


@pytest.mark.asyncio
async def test_login_with_invalid_credentials_returns_401(client: AsyncClient):
    # Act
    response = await client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrong_password"
    })

    # Assert
    assert response.status_code == 401
```

**Fixtures (conftest.py):**

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base
from app.core.dependencies import get_db


# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
```

**Factory Boy:**

```python
# tests/factories.py
import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.models.user import User
from app.core.security import hash_password


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None  # Set in conftest

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    hashed_password = factory.LazyAttribute(lambda o: hash_password("default_password"))
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    tier = "free"
```

### Commands

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_services/test_auth.py

# Run with verbose output
uv run pytest -v

# Run only failed tests
uv run pytest --lf
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: uv run pytest --cov=app --cov-fail-under=80
```

---

## Rate Limiting

### Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Library** | slowapi | FastAPI rate limiting |
| **Storage** | Redis (shared with LiteLLM) | Rate limit counters |

### Configuration

```python
# core/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


def get_user_or_ip(request):
    """Get user_id from token or fallback to IP."""
    # Try to get user from request state (set by auth middleware)
    if hasattr(request.state, "user_id"):
        return f"user:{request.state.user_id}"
    return f"ip:{get_remote_address(request)}"


limiter = Limiter(
    key_func=get_user_or_ip,
    storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}",
    default_limits=["100/minute"],
)
```

### Usage in Routes

```python
# routes/chat.py
from app.core.rate_limit import limiter

@router.post("/chat")
@limiter.limit("30/minute")  # Override default
async def chat(
    request: Request,
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> BaseResponse[ChatResponse]:
    ...
```

### Rate Limits by Tier

| Tier | Limit | Endpoint |
|------|-------|----------|
| **Free** | 5/minute | /chat |
| **Pro** | 30/minute | /chat |
| **Enterprise** | 100/minute | /chat |
| **All** | 100/minute | Other endpoints |

### Implementation

```python
# core/rate_limit.py
from enum import Enum


class RateLimitTier(str, Enum):
    FREE = "5/minute"
    PRO = "30/minute"
    ENTERPRISE = "100/minute"


def get_rate_limit_by_tier(tier: str) -> str:
    limits = {
        "free": RateLimitTier.FREE,
        "pro": RateLimitTier.PRO,
        "enterprise": RateLimitTier.ENTERPRISE,
    }
    return limits.get(tier, RateLimitTier.FREE)


# Dynamic rate limiting
@router.post("/chat")
async def chat(
    request: Request,
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> BaseResponse[ChatResponse]:
    # Apply rate limit based on user tier
    limit = get_rate_limit_by_tier(current_user.tier)
    await limiter.check(limit, request)
    ...
```

### Error Response

```json
{
  "trace_id": "abc123...",
  "error": "Rate limit exceeded",
  "detail": "30/minute limit reached. Retry after 45 seconds."
}
```

### Fail Mode Strategy

When Redis is unavailable:

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Fail Open** | Allow request (skip rate limit) | Better UX, recommended |
| **Fail Closed** | Block request | High security requirement |

**Implementation (Fail Open - Recommended):**

```python
# core/rate_limit.py
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
import logging

logger = logging.getLogger(__name__)

class FailOpenLimiter(Limiter):
    """Rate limiter that fails open when Redis is unavailable."""

    async def check(self, limit: str, request):
        try:
            await super().check(limit, request)
        except Exception as e:
            if isinstance(e, RateLimitExceeded):
                raise  # Rate limit exceeded - block
            # Redis connection error - fail open
            logger.warning(f"Rate limit check failed, allowing request: {e}")
```

### Main.py Setup

```python
# main.py
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.rate_limit import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

---

## Backend Metrics (Prometheus)

### Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Library** | prometheus-fastapi-instrumentator | Auto metrics |
| **Endpoint** | /metrics | Prometheus scrape |
| **Storage** | Prometheus (shared with LiteLLM) | Metrics storage |

### Metrics Exposed

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | Request latency |
| `http_requests_in_progress` | Gauge | Current active requests |
| `app_users_total` | Gauge | Total registered users |
| `app_active_sessions` | Gauge | Active sessions |

### Implementation

```python
# core/metrics.py
from prometheus_fastapi_instrumentator import Instrumentator, metrics
from prometheus_client import Gauge, Counter

# Custom metrics
USERS_TOTAL = Gauge("app_users_total", "Total registered users")
ACTIVE_SESSIONS = Gauge("app_active_sessions", "Active sessions")
CHAT_REQUESTS = Counter("app_chat_requests_total", "Total chat requests", ["model", "tier"])


def setup_metrics(app):
    """Setup Prometheus metrics."""
    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/health", "/metrics"],
        inprogress_name="http_requests_in_progress",
        inprogress_labels=True,
    )

    # Add default metrics
    instrumentator.add(metrics.default())
    instrumentator.add(metrics.latency())
    instrumentator.add(metrics.requests())

    # Instrument app
    instrumentator.instrument(app)
    instrumentator.expose(app, endpoint="/metrics")
```

### Main.py Setup

```python
# main.py
from app.core.metrics import setup_metrics

app = FastAPI(...)

# Setup metrics
setup_metrics(app)
```

### Custom Metrics Usage

```python
# services/chat.py
from app.core.metrics import CHAT_REQUESTS

async def process_chat(user: User, model: str, message: str):
    # Increment counter with labels
    CHAT_REQUESTS.labels(model=model, tier=user.tier).inc()
    ...
```

### Prometheus Config (เพิ่มใน prometheus.yml)

```yaml
scrape_configs:
  # Backend API metrics
  - job_name: "backend-api"
    static_configs:
      - targets: ["backend:8000"]
    metrics_path: /metrics
    scrape_interval: 15s
```

### Grafana Dashboard Queries

```promql
# Request rate
rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Chat requests by model
rate(app_chat_requests_total[5m])
```

---

## File Upload Handling (RAG Documents)

### Rules

- Use `UploadFile` for document uploads
- **NEVER** use `await file.read()` for large files (RAM overflow)
- **USE** chunked reading or stream directly to storage/parser
- Validate file magic numbers (mime-type) using `python-magic` or `filetype`

### Implementation

```python
# routes/documents.py
from fastapi import UploadFile, File, HTTPException
import filetype

ALLOWED_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/projects/{project_id}/documents")
async def upload_document(
    project_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> BaseResponse[DocumentResponse]:
    ctx = get_context()

    # Validate file type by magic number (not just extension)
    header = await file.read(2048)
    await file.seek(0)  # Reset position

    kind = filetype.guess(header)
    if kind is None or kind.mime not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Stream to storage (chunked)
    file_path = await storage.save_chunked(file, project_id)

    # Process document
    document = await document_service.process(file_path, project_id)

    return BaseResponse(trace_id=ctx.trace_id, data=document)


# services/storage.py
async def save_chunked(file: UploadFile, project_id: int) -> str:
    """Save file in chunks to prevent memory overflow."""
    file_path = f"/data/uploads/{project_id}/{file.filename}"

    async with aiofiles.open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await f.write(chunk)

    return file_path
```

---

## Background Tasks / Job Queue (Fine-tuning)

### Pattern: DB-based Queue

For Fine-tuning jobs that run on GPU cloud:

- Use DB-based Queue pattern (Jobs table)
- `POST /jobs` → Create 'pending' record → Return Job ID immediately
- **DO NOT** wait for completion in the request
- External worker polls for pending jobs

### Implementation

```python
# models/job.py
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)  # embedding, classifier, llm_lora
    status = Column(String, default=JobStatus.PENDING)
    config = Column(JSON, nullable=False)  # Training config
    result = Column(JSON, nullable=True)   # Output after completion
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


# routes/finetune.py
@router.post("/finetune/jobs")
async def create_job(
    data: JobCreate,
    current_user: User = Depends(get_current_user),
) -> BaseResponse[JobResponse]:
    ctx = get_context()

    # Create job record (returns immediately)
    job = await job_service.create(data, user_id=current_user.id)

    return BaseResponse(
        trace_id=ctx.trace_id,
        data=JobResponse(
            id=job.id,
            status=job.status,
            message="Job queued. Poll GET /finetune/jobs/{id} for status."
        )
    )


# Worker endpoint (called by GPU cloud worker)
@router.get("/finetune/jobs/pending")
async def get_pending_jobs(
    api_key: str = Depends(verify_worker_api_key),
) -> list[JobResponse]:
    """Worker polls this endpoint for pending jobs."""
    return await job_service.get_pending()


@router.patch("/finetune/jobs/{job_id}")
async def update_job_status(
    job_id: int,
    data: JobStatusUpdate,
    api_key: str = Depends(verify_worker_api_key),
) -> BaseResponse[JobResponse]:
    """Worker updates job status after completion/failure."""
    job = await job_service.update_status(job_id, data)
    return BaseResponse(trace_id="worker", data=job)
```

### Lightweight Background Tasks

For quick tasks (notifications, cleanup), use FastAPI's `BackgroundTasks`:

```python
from fastapi import BackgroundTasks

@router.post("/users/register")
async def register(
    data: UserCreate,
    background_tasks: BackgroundTasks,
) -> BaseResponse[UserResponse]:
    user = await auth_service.register(data)

    # Non-blocking: send welcome email
    background_tasks.add_task(email_service.send_welcome, user.email)

    return BaseResponse(trace_id=ctx.trace_id, data=user)
```
