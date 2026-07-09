#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="awe-postgresql"

if ! docker info &>/dev/null; then
    echo "WARNING: Docker is not running. Skip PostgreSQL." >&2
    exit 1
fi

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "PostgreSQL is already running"
    exit 0
fi

# Container exists but is stopped - start it
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Starting existing PostgreSQL container..."
    docker start awe-postgresql
    echo "PostgreSQL started on port 5433"
    exit 0
fi

echo "Starting PostgreSQL..."
docker run -d \
    --name awe-postgresql \
    --restart unless-stopped \
    -p 5433:5432 \
    -e POSTGRES_USER=awe \
    -e POSTGRES_PASSWORD=awe-password \
    -e POSTGRES_DB=awe \
    -v postgres_data:/var/lib/postgresql/data \
    postgres:16-alpine

echo "PostgreSQL started on port 5433"
