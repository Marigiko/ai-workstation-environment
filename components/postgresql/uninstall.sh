#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Stopping PostgreSQL (volume is kept)..."
# Compose interpolates the whole file even for `down`; the password is not used here.
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-unused-for-down}" docker compose -p awe-postgresql -f "$SCRIPT_DIR/docker-compose.yaml" down
