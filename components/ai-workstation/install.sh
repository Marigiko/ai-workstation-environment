#!/usr/bin/env bash
set -euo pipefail

GATEWAY_DIR="${AI_WORKSTATION_DIR:-$HOME/ai-workstation}"
GATEWAY_PORT="${GATEWAY_PORT:-8000}"

if ! docker info &>/dev/null; then
    echo "ERROR: Docker is not running. Start Docker first." >&2
    exit 1
fi

# Check if already running
if curl -sf "http://localhost:${GATEWAY_PORT}/health" &>/dev/null; then
    echo "AI Workstation Gateway is already running on port ${GATEWAY_PORT}"
    exit 0
fi

# Clone if not exists
if [ ! -d "$GATEWAY_DIR" ]; then
    echo "Cloning ai-workstation gateway..."
    git clone https://github.com/keyz/ai-workstation.git "$GATEWAY_DIR"
else
    echo "ai-workstation directory found at ${GATEWAY_DIR}"
    cd "$GATEWAY_DIR"
    git pull --ff-only 2>/dev/null || true
fi

cd "$GATEWAY_DIR"

# Setup .env if missing
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    if [ -f infrastructure/compose/.env.example ]; then
        cp infrastructure/compose/.env.example .env
    else
        touch .env
    fi

    # Generate strong random passwords
    POSTGRES_PASSWORD=$(openssl rand -hex 24)
    GRAFANA_PASSWORD=$(openssl rand -hex 16)

    cat >> .env <<EOF
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
GRAFANA_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
EOF

    echo "Generated secure passwords for PostgreSQL and Grafana."
    echo "IMPORTANT: Add your LLM API keys to ${GATEWAY_DIR}/ .env"
    echo "  (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)"
fi

# Start gateway stack
echo "Starting AI Workstation Gateway..."
docker compose -f infrastructure/compose/docker-compose.prod.yml up -d

# Wait for health
echo "Waiting for gateway to be ready..."
for i in $(seq 1 60); do
    if curl -sf "http://localhost:${GATEWAY_PORT}/health" &>/dev/null; then
        echo "AI Workstation Gateway is ready!"
        echo "  Gateway:  http://localhost:${GATEWAY_PORT}"
        echo "  Health:   http://localhost:${GATEWAY_PORT}/health"
        echo "  Grafana:  http://localhost:3000"
        exit 0
    fi
    sleep 2
done

echo "WARNING: Gateway did not become healthy within 120 seconds." >&2
echo "Check logs: docker compose -f ${GATEWAY_DIR}/infrastructure/compose/docker-compose.prod.yml logs" >&2
exit 1
