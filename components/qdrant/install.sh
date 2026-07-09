#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="awe-qdrant"

if ! docker info &>/dev/null; then
    echo "WARNING: Docker is not running. Skip Qdrant." >&2
    exit 1
fi

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Qdrant is already running"
    exit 0
fi

# Container exists but is stopped - start it
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Starting existing Qdrant container..."
    docker start awe-qdrant
    echo "Qdrant started on port 6333 (API) and 6334 (gRPC)"
    exit 0
fi

echo "Starting Qdrant..."
docker run -d \
    --name awe-qdrant \
    --restart unless-stopped \
    -p 6333:6333 \
    -p 6334:6334 \
    -v qdrant_data:/qdrant/storage \
    qdrant/qdrant:latest

echo "Qdrant started on port 6333 (API) and 6334 (gRPC)"
