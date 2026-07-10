#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Distributed AI Workspace..."

cd "$SCRIPT_DIR" || exit

if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
    echo "Starting workspace services..."
    docker compose up -d
    echo "Waiting for API to be ready..."
    for _ in $(seq 1 30); do
        if curl -s http://localhost:8080/health &>/dev/null; then
            echo "Workspace API is ready!"
            break
        fi
        sleep 2
    done
else
    echo "Docker not available. Install docker component first."
    exit 1
fi

echo "Distributed AI Workspace installed!"
echo "  API: http://localhost:8080"
echo "  Docs: http://localhost:8080/docs"
echo "  Health: http://localhost:8080/health"
