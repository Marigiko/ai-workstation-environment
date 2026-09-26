#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_NAME="awe-postgresql"
COMPOSE_PROJECT="awe-postgresql"
NETWORK="awe-shared"

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

# Foreign container guard
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    OWNER="$(docker inspect -f '{{index .Config.Labels "com.docker.compose.project"}}' "$CONTAINER_NAME")"
    if [[ "$OWNER" != "$COMPOSE_PROJECT" ]]; then
        echo "ERROR: container '$CONTAINER_NAME' exists but is not managed by compose project '$COMPOSE_PROJECT' (owner: '$OWNER')." >&2
        exit 1
    fi
fi

if docker network inspect "$NETWORK" &>/dev/null; then
    :
else
    docker network create --driver bridge "$NETWORK"
fi

# Idempotency: already healthy -> done
if [[ "$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || true)" == "healthy" ]]; then
    echo "PostgreSQL is already running and healthy"
    exit 0
fi

docker compose -p "$COMPOSE_PROJECT" -f "$SCRIPT_DIR/docker-compose.yaml" up -d

echo "Waiting for PostgreSQL to become healthy..."
for _ in $(seq 1 60); do
    STATUS="$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || true)"
    if [[ "$STATUS" == "healthy" ]]; then
        echo "PostgreSQL is healthy on 127.0.0.1:5433"
        exit 0
    fi
    sleep 1
done

echo "ERROR: PostgreSQL did not become healthy within 60s." >&2
exit 1
