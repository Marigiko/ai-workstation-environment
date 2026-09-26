#!/usr/bin/env bash

CONTAINER_NAME="awe-postgresql"

if ! docker info &>/dev/null; then
    exit 1
fi

if [[ "$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || true)" == "healthy" ]]; then
    exit 0
fi
exit 1
