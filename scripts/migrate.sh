#!/bin/bash
# Run database migrations

set -e

cd "$(dirname "$0")/../backend"

if [ "$1" == "create" ]; then
    if [ -z "$2" ]; then
        echo "Usage: ./scripts/migrate.sh create <migration_name>"
        exit 1
    fi
    echo "Creating migration: $2"
    uv run alembic revision --autogenerate -m "$2"
elif [ "$1" == "down" ]; then
    echo "Rolling back one migration..."
    uv run alembic downgrade -1
elif [ "$1" == "reset" ]; then
    echo "Resetting database to base..."
    uv run alembic downgrade base
else
    echo "Running migrations..."
    uv run alembic upgrade head
fi
