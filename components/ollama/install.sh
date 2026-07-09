#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="awe-ollama"

if ! docker info &>/dev/null; then
    echo "WARNING: Docker is not running. Skip Ollama." >&2
    exit 1
fi

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Ollama is already running"
    exit 0
fi

# Container exists but may have old GPU config - recreate it
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Recreating Ollama container (CPU mode)..."
    docker rm -f awe-ollama >/dev/null 2>&1 || true
fi

echo "Starting Ollama (CPU mode)..."
docker run -d \
    --name awe-ollama \
    --restart unless-stopped \
    -p 11434:11434 \
    -v ollama_data:/root/.ollama \
    ollama/ollama:latest

echo "Ollama started on port 11434 (CPU mode - GPU not available)"
