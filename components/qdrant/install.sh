#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="awe-qdrant"

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Qdrant is already running"
    exit 0
fi

echo "Starting Qdrant..."
docker compose -f "$SCRIPT_DIR/docker-compose.yaml" up -d

echo "Qdrant started on port 6333 (API) and 6334 (gRPC)"
