#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="awe-n8n"
COMPOSE_PROJECT="awe-n8n"
PG_COMPONENT_DIR="$(cd "$SCRIPT_DIR/../postgresql" && pwd)"

# Load AWE_PG_PASSWORD from the env file if not already set (values are never printed)
if [[ -z "${AWE_PG_PASSWORD:-}" ]]; then
    ENV_FILE="${AWE_ENV_FILE:-$HOME/.config/awe/env/mcp.env}"
    if [[ -f "$ENV_FILE" ]]; then
        set -a
        # shellcheck disable=SC1090
        . "$ENV_FILE"
        set +a
    fi
fi

if [[ -z "${AWE_PG_PASSWORD:-}" ]]; then
    echo "ERROR: AWE_PG_PASSWORD is empty. Set it in \${AWE_ENV_FILE:-$HOME/.config/awe/env/mcp.env}." >&2
    exit 1
fi
export POSTGRES_PASSWORD="$AWE_PG_PASSWORD"

if ! docker info &>/dev/null; then
    echo "ERROR: Docker is not running." >&2
    exit 1
fi

if ! bash "$PG_COMPONENT_DIR/check.sh"; then
    echo "ERROR: PostgreSQL is not healthy. Run components/postgresql/install.sh first." >&2
    exit 1
fi

# Foreign container guard
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    OWNER="$(docker inspect -f '{{index .Config.Labels "com.docker.compose.project"}}' "$CONTAINER_NAME")"
    if [[ "$OWNER" != "$COMPOSE_PROJECT" ]]; then
        echo "ERROR: container '$CONTAINER_NAME' exists but is not managed by compose project '$COMPOSE_PROJECT' (owner: '$OWNER')." >&2
        exit 1
    fi
fi

# Idempotency: already answering -> done
if curl -fsS -o /dev/null http://127.0.0.1:5678/healthz 2>/dev/null; then
    echo "n8n is already running at http://127.0.0.1:5678"
    exit 0
fi

docker compose -p "$COMPOSE_PROJECT" -f "$SCRIPT_DIR/docker-compose.yaml" up -d

echo "Waiting for n8n to answer /healthz..."
for _ in $(seq 1 90); do
    if curl -fsS -o /dev/null http://127.0.0.1:5678/healthz 2>/dev/null; then
        echo "n8n is healthy on http://127.0.0.1:5678"
        exit 0
    fi
    sleep 1
done

echo "ERROR: n8n did not become healthy within 90s." >&2
exit 1
