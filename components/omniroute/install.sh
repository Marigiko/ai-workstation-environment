#!/usr/bin/env bash
set -euo pipefail

# Resolve the OmniRoute checkout: OMNIROUTE_DIR, else $AWE_PROJECTS_DIR/OmniRoute.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECTS_DIR="${AWE_PROJECTS_DIR:-$(dirname "$REPO_ROOT")}"
OMNIROUTE_DIR="${OMNIROUTE_DIR:-$PROJECTS_DIR/OmniRoute}"

GATEWAY_URL="http://127.0.0.1:20128/v1/models"

if [ ! -d "$OMNIROUTE_DIR" ]; then
    echo "ERROR: OmniRoute checkout not found at: $OMNIROUTE_DIR" >&2
    echo "Clone it manually (never cloned automatically):" >&2
    echo "  git clone https://github.com/diegosouzapw/OmniRoute \"$OMNIROUTE_DIR\"" >&2
    exit 1
fi

cd "$OMNIROUTE_DIR"

if ! [ -f ".env" ]; then
    echo "ERROR: $OMNIROUTE_DIR/.env is missing." >&2
    echo "Create it from .env.example before installing:" >&2
    echo "  cp .env.example .env  # then edit it" >&2
    exit 1
fi

# Loopback-only port override (gitignored): never overwrite an existing file.
if [ ! -f "docker-compose.override.yml" ]; then
    cat > docker-compose.override.yml <<'EOF'
# Local override (gitignored): publish OmniRoute ports on loopback only.
# WSL mirrored networking shares the Windows host network, so a bare
# "20128:20128" mapping would expose the gateway on every LAN interface.
services:
  omniroute-base:
    ports: !override
      - "127.0.0.1:${DASHBOARD_PORT:-20128}:${DASHBOARD_PORT:-20128}"
      - "127.0.0.1:${API_PORT:-20129}:${API_PORT:-20129}"
      - "127.0.0.1:${LIVE_WS_PORT:-20132}:${LIVE_WS_PORT:-20132}"
EOF
    echo "Wrote docker-compose.override.yml (loopback-only ports)"
fi

# Idempotency: if the gateway is already healthy, do nothing.
if "$SCRIPT_DIR/check.sh"; then
    echo "OmniRoute is already running"
    exit 0
fi

echo "Starting OmniRoute via Docker Compose..."
docker compose --profile base up -d

# Poll the gateway until it answers 200 or 401 (reachable), up to 120 s.
last_error=""
for _ in $(seq 1 60); do
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$GATEWAY_URL" || true)
    if [ "$code" = "200" ] || [ "$code" = "401" ]; then
        echo "OmniRoute is up (HTTP $code)"
        exit 0
    fi
    last_error="HTTP ${code:-none}"
    sleep 2
done

echo "ERROR: OmniRoute did not become reachable within 120 s (last: $last_error)" >&2
docker compose --profile base ps >&2 || true
exit 1
