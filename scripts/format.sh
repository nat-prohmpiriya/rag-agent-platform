#!/bin/bash
# Auto-fix lint issues and format code

set -e

cd "$(dirname "$0")/../backend"

echo "Fixing lint issues..."
uv run ruff check . --fix

echo "Formatting code..."
uv run ruff format .

echo "Done!"
