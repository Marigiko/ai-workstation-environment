#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Stopping Distributed AI Workspace..."

cd "$SCRIPT_DIR"
docker compose down -v 2>/dev/null || true

echo "Distributed AI Workspace stopped and removed."
