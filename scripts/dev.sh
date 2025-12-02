#!/bin/bash
# Start backend development server with hot reload

set -e

cd "$(dirname "$0")/../backend"

echo "Starting FastAPI development server..."
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
