---
applyTo: "**/*"
---

# RAG Agent Platform - General Instructions

## Project Overview

This is a **RAG (Retrieval-Augmented Generation) Agent Platform** - a full-stack application for building AI-powered document retrieval and chat systems.

## Tech Stack

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

## General Coding Standards

### Language
- **Write all code and comments in English only**
- Use clear, descriptive variable and function names
- Add comments only when logic is non-obvious

### Type Safety
- Use TypeScript for frontend (strict mode)
- Use Python type hints for backend
- **Never use `any` type** unless absolutely necessary

### Code Style
- Follow existing patterns in the codebase
- Keep functions small and focused (single responsibility)
- Use meaningful error messages

## Key Documentation

For detailed instructions, reference these files:
- `frontend/CLAUDE.md` - Frontend-specific patterns and Svelte 5 syntax
- `backend/CLAUDE.md` - Backend-specific patterns and Python style
- `.docs/02-spec.md` - Full project specification
- `.docs/04-todos.md` - Current development status

## Task Tracking

When completing tasks, update `.docs/04-todos.md`:
- Change `[ ]` to `[x]` for completed items
- Update the progress overview table if a component status changes
