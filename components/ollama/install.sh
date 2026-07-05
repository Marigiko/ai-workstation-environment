#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="awe-ollama"

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Ollama is already running"
    exit 0
fi

echo "Starting Ollama..."
docker compose -f "$SCRIPT_DIR/docker-compose.yaml" up -d

echo "Ollama started on port 11434"
