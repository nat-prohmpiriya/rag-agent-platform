# GitHub Copilot Instructions - RAG Agent Platform

## Project Overview

This is a **RAG (Retrieval-Augmented Generation) Agent Platform** built as a full-stack application:

| Layer | Technology |
|-------|------------|
| **Frontend** | SvelteKit 2.x + Svelte 5 (Runes) + Tailwind CSS v4 + shadcn-svelte |
| **Backend** | FastAPI (Python 3.12+) + SQLAlchemy async + PostgreSQL |
| **LLM Gateway** | LiteLLM Proxy (unified API for OpenAI, Gemini, Groq) |
| **Vector Store** | pgvector (PostgreSQL) |
| **Auth** | JWT + Refresh Token |
| **Observability** | OpenTelemetry + Jaeger |

## Directory Structure

```
/
├── frontend/          # SvelteKit application
├── backend/           # FastAPI Python application
├── infra/             # Infrastructure configs (LiteLLM, Prometheus)
├── scripts/           # Development scripts
├── .docs/             # Project documentation & specs
└── docker-compose.yaml
```

## Coding Standards

### General Rules
- **Language**: Write all code and comments in **English only**
- **Code Style**: Follow existing patterns in the codebase
- **Type Safety**: Use TypeScript (frontend) and type hints (backend) everywhere
- **Avoid `any`**: Never use `any` type unless absolutely necessary

### Frontend (SvelteKit + Svelte 5)
- **MUST use Svelte 5 Runes syntax** - NOT legacy Svelte 4 syntax
- Use `$state()` instead of `let count = 0`
- Use `$derived()` instead of `$: derived = ...`
- Use `$effect()` instead of `$: { ... }`
- Use `$props()` instead of `export let`
- Use Snippets `{@render children()}` instead of `<slot />`
- Use callback props instead of `createEventDispatcher`
- Use shadcn-svelte components from `$lib/components/ui/`
- Use Paraglide for i18n: `import * as m from '$lib/paraglide/messages'`

### Backend (FastAPI + Python)
- Use `async/await` for all DB and HTTP operations
- Use Pydantic v2 with `model_config = ConfigDict(from_attributes=True)`
- Return `BaseResponse[T]` wrapper for all API responses (includes trace_id)
- Use `@traced()` decorator for important service functions
- Follow schema naming: `*Create`, `*Update`, `*Response`, `*Input`
- Use `str | None` syntax instead of `Union[str, None]`

## Architecture Patterns

### Backend Data Flow
```
Request → Middleware → Routes → Services → Models/Providers → Response
              ↓           ↓          ↓
         RequestContext  Schemas   Database
              ↓
          trace_id
```

### Layer Responsibilities
| Layer | Responsibility |
|-------|---------------|
| **Routes** | HTTP handling, validation, call services |
| **Services** | Business logic, DB queries (no HTTP knowledge) |
| **Models** | SQLAlchemy ORM (no business logic) |
| **Schemas** | Pydantic request/response validation |
| **Providers** | External API clients (LiteLLM) |
| **Core** | Shared utilities (security, database, context) |

### Frontend Structure
| Location | Purpose |
|----------|---------|
| `src/routes/` | SvelteKit pages and layouts |
| `src/lib/components/ui/` | shadcn-svelte base components |
| `src/lib/components/custom/` | Business components (ChatWindow, etc.) |
| `src/lib/api/` | API client functions |
| `src/lib/stores/` | Svelte stores |
| `src/lib/types/` | TypeScript interfaces |

## Key Conventions

### File Naming
| Type | Frontend | Backend |
|------|----------|---------|
| Components | `PascalCase.svelte` | - |
| Routes | `lowercase-with-hyphens/` | - |
| Utilities | `camelCase.ts` | `snake_case.py` |
| Types/Schemas | `PascalCase.ts` | `PascalCase` in file |

### API Response Format
All backend responses must include `trace_id`:
```json
{
  "trace_id": "abc123...",
  "data": { ... }
}
```

### Streaming Responses (SSE)
For chat/LLM endpoints, use `StreamingResponse` with `X-Trace-Id` header.

## Commands

### Backend
```bash
cd backend
uv sync                              # Install dependencies
uv run uvicorn app.main:app --reload # Run dev server
uv run alembic upgrade head          # Run migrations
uv run pytest                        # Run tests
uv run ruff check . --fix            # Lint & fix
uv run ruff format .                 # Format code
```

### Frontend
```bash
cd frontend
npm install                          # Install dependencies
npm run dev                          # Run dev server
npm run build                        # Build for production
npm run check                        # Type check
npm run lint                         # Lint code
```

### Docker
```bash
docker-compose up -d                 # Start all services
docker-compose logs -f backend       # View backend logs
```

## Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
JWT_SECRET_KEY=your-secret-key-min-32-chars
LITELLM_API_URL=http://localhost:4000
OTEL_ENABLED=true
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

## Task Tracking

When completing tasks, update `.docs/04-todos.md`:
- Change `[ ]` to `[x]` for completed items
- Update the progress overview table if needed

## References

For detailed instructions, see:
- `frontend/CLAUDE.md` - Frontend-specific patterns
- `backend/CLAUDE.md` - Backend-specific patterns
- `.docs/02-spec.md` - Full project specification
- `.docs/04-todos.md` - Current development status
