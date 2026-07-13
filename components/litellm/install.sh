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

# Generate or read master key
if [ -f "$SCRIPT_DIR/.litellm_key" ]; then
    LITELLM_MASTER_KEY=$(cat "$SCRIPT_DIR/.litellm_key")
else
    LITELLM_MASTER_KEY=$(openssl rand -hex 16)
    echo "$LITELLM_MASTER_KEY" > "$SCRIPT_DIR/.litellm_key"
    echo "Generated LiteLLM master key: $LITELLM_MASTER_KEY"
fi

echo "Starting LiteLLM..."
docker run -d \
    --name awe-litellm \
    --restart unless-stopped \
    -p 4000:4000 \
    -e LITELLM_LOG=info \
    -e LITELLM_MASTER_KEY="$LITELLM_MASTER_KEY" \
    ghcr.io/berriai/litellm:main-latest

echo "LiteLLM started on port 4000"
