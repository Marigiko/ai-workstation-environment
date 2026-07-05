#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="awe-litellm"

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "LiteLLM is already running"
    exit 0
fi

echo "Starting LiteLLM..."
docker compose -f "$SCRIPT_DIR/docker-compose.yaml" up -d

echo "LiteLLM started on port 4000"
