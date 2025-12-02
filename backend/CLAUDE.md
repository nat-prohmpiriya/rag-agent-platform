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

---

## Project Structure

```
app/
├── main.py              # FastAPI entrypoint
├── config.py            # Environment settings (pydantic-settings)
│
├── schemas/             # Pydantic schemas (Request/Response/Internal DTOs)
│   ├── __init__.py
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
└── core/                # Shared utilities
    ├── __init__.py
    ├── database.py      # DB connection, session
    ├── security.py      # JWT, password hashing
    ├── dependencies.py  # FastAPI dependencies (get_db, get_current_user)
    └── exceptions.py    # Custom exceptions
```

---

## Architecture Rules

1. **Routes**: Only handle HTTP, validate input, call services
2. **Services**: Business logic, DB queries, no HTTP knowledge
3. **Models**: Database tables only, no business logic
4. **Schemas**: Request/Response validation, separate from Models
5. **Providers**: External API clients (stateless)
6. **Core**: Shared utilities used across all layers

### Data Flow

```
Request --> Routes --> Services --> Models/Providers --> Response
               |           |
            Schemas     Database
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
