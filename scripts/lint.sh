#!/bin/bash
# Run linter and formatter check

set -e

cd "$(dirname "$0")/../backend"

echo "Running ruff check..."
uv run ruff check .

echo "Running ruff format check..."
uv run ruff format --check .

echo "All checks passed!"
