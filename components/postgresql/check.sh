#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="awe-postgresql"

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    exit 0
fi
exit 1
