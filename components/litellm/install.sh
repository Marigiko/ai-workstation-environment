#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="awe-litellm"

if ! docker info &>/dev/null; then
    echo "WARNING: Docker is not running. Skip LiteLLM." >&2
    exit 1
fi

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "LiteLLM is already running"
    exit 0
fi

# Container exists but is stopped - start it
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Starting existing LiteLLM container..."
    docker start awe-litellm
    echo "LiteLLM started on port 4000"
    exit 0
fi

echo "Starting LiteLLM..."
docker run -d \
    --name awe-litellm \
    --restart unless-stopped \
    -p 4000:4000 \
    -e LITELLM_LOG=info \
    ghcr.io/berriai/litellm:main-latest

echo "LiteLLM started on port 4000"
