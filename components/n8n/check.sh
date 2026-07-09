#!/usr/bin/env bash

CONTAINER_NAME="awe-n8n"

if ! docker info &>/dev/null; then
    exit 1
fi

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    exit 0
fi
exit 1
