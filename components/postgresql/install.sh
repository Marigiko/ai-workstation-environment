#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="awe-postgresql"

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "PostgreSQL is already running"
    exit 0
fi

echo "Starting PostgreSQL..."
docker compose -f "$SCRIPT_DIR/docker-compose.yaml" up -d

echo "PostgreSQL started on port 5432"
