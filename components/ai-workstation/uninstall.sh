#!/usr/bin/env bash
set -euo pipefail

GATEWAY_DIR="${AI_WORKSTATION_DIR:-$HOME/ai-workstation}"

if [ -d "$GATEWAY_DIR" ]; then
    cd "$GATEWAY_DIR"
    if [ -f infrastructure/compose/docker-compose.prod.yml ]; then
        echo "Stopping AI Workstation Gateway..."
        docker compose -f infrastructure/compose/docker-compose.prod.yml down
        echo "Gateway stopped."
    fi
else
    echo "ai-workstation directory not found at ${GATEWAY_DIR}. Nothing to uninstall."
fi
