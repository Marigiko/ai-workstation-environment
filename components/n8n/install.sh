#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="awe-n8n"

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "n8n is already running"
    exit 0
fi

echo "Starting n8n..."
docker compose -f "$SCRIPT_DIR/docker-compose.yaml" up -d

echo "n8n started on port 5678"
