#!/bin/bash
# Initial project setup

set -e

cd "$(dirname "$0")/../backend"

echo "Installing backend dependencies..."
uv sync --extra dev

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure"
echo "  2. Start PostgreSQL database"
echo "  3. Run migrations: ./scripts/migrate.sh"
echo "  4. Start dev server: ./scripts/dev.sh"
