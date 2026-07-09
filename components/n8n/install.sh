#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="awe-n8n"

if ! docker info &>/dev/null; then
    echo "WARNING: Docker is not running. Skip n8n." >&2
    exit 1
fi

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "n8n is already running"
    exit 0
fi

# Container exists but is stopped - start it
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Starting existing n8n container..."
    docker start awe-n8n
    echo "n8n started on port 5678"
    exit 0
fi

echo "Starting n8n..."
docker run -d \
    --name awe-n8n \
    --restart unless-stopped \
    -p 5678:5678 \
    -e DB_TYPE=postgresdb \
    -e DB_POSTGRESDB_HOST=awe-postgresql \
    -e DB_POSTGRESDB_PORT=5432 \
    -e DB_POSTGRESDB_DATABASE=awe \
    -e DB_POSTGRESDB_USER=awe \
    -e DB_POSTGRESDB_PASSWORD=awe-password \
    -e N8N_HOST=localhost \
    -e N8N_PORT=5678 \
    -e WEBHOOK_URL=http://localhost:5678/ \
    -v n8n_data:/home/node/.n8n \
    n8nio/n8n:latest

echo "n8n started on port 5678"
