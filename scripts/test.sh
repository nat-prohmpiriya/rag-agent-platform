#!/bin/bash
# Run backend tests with pytest

set -e

cd "$(dirname "$0")/../backend"

echo "Running tests..."
uv run pytest -v "$@"
