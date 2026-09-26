#!/usr/bin/env bash
set -euo pipefail
# AI Workstation Gateway Installer
# Installs the FastAPI gateway for AI model routing, MCP, memory, and skills.
#
# Architecture:
#   - Python monorepo (uv workspace), 11 packages + gateway + CLI
#   - Uses shared infrastructure: PostgreSQL (5433), Redis (6380), Qdrant (6335)
#   - Gateway runs on port 8000

# Dynamic path detection: use AI_WORKSTATION_DIR env var, or search common locations
_find_gateway_dir() {
    if [ -n "${AI_WORKSTATION_DIR:-}" ] && [ -d "$AI_WORKSTATION_DIR" ]; then
        echo "$AI_WORKSTATION_DIR"
        return
    fi
    # Search common project locations (same logic as core/detect.py)
    for candidate in \
        "$HOME/Projects/ai-workstation" \
        "$HOME/ai-workstation" \
        "/mnt/e/Projects/ai-workstation" \
        "/mnt/c/Projects/ai-workstation" \
        "$HOME/workspace/ai-workstation"; do
        if [ -d "$candidate" ] && [ -f "$candidate/pyproject.toml" ]; then
            echo "$candidate"
            return
        fi
    done
    return 1
}

GATEWAY_DIR=$(_find_gateway_dir) || {
    echo "ERROR: Could not find ai-workstation directory." >&2
    echo "Set AI_WORKSTATION_DIR env var or clone into a standard location." >&2
    exit 1
}
GATEWAY_PORT="${GATEWAY_PORT:-8000}"

# Build PATH dynamically: include common tool locations without hardcoding versions
_detect_path() {
    local p="$1"
    [ -d "$p" ] && echo "$p"
}
PATH_EXTRA=""
for d in \
    "$HOME/.micromamba/bin" \
    "$HOME/.local/bin" \
    "$HOME/.cargo/bin" \
    "$(ls -d "$HOME"/.nvm/versions/node/*/bin 2>/dev/null | sort -V | tail -1)"; do
    detected="$(_detect_path "$d")"
    [ -n "$detected" ] && PATH_EXTRA="${PATH_EXTRA:+${PATH_EXTRA}:}${detected}"
done
export PATH="$PATH_EXTRA${PATH_EXTRA:+:$PATH}"

echo "=== AI Workstation Gateway Installer ==="

# 1. Verify dependencies
echo "[1/5] Checking dependencies..."
if ! command -v uv &>/dev/null; then
    echo "Installing uv (Python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# 2. Clone/pull repo
echo "[2/5] Repository..."
if [ ! -d "$GATEWAY_DIR" ]; then
    echo "ERROR: ai-workstation directory not found at $GATEWAY_DIR" >&2
    echo "Clone it first: git clone <url> $GATEWAY_DIR" >&2
    exit 1
fi

cd "$GATEWAY_DIR"

# 3. Install Python dependencies
echo "[3/5] Installing Python dependencies..."
uv sync --all-packages

# 4. Setup .env (critical for DATABASE_URL)
echo "[4/5] Configuring .env..."
if [ ! -f .env ]; then
    if [ -f infrastructure/compose/.env ]; then
        cp infrastructure/compose/.env .env
        echo "  Created .env from infrastructure/compose/.env"
    else
        cat > .env <<'ENVEOF'
DATABASE_URL=postgresql+asyncpg://awe:awe123@localhost:5433/ai_workstation_gateway
REDIS_URL=redis://localhost:6380/0
QDRANT_URL=http://localhost:6335
GATEWAY_PORT=8000
GATEWAY_HOST=0.0.0.0
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
ENVEOF
        echo "  Created .env with shared infrastructure settings"
    fi
else
    echo "  .env already exists"
fi

# Ensure load_dotenv is in gateway main.py (fixes DATABASE_URL not loading)
if ! grep -q "load_dotenv" apps/gateway/src/gateway/main.py 2>/dev/null; then
    echo "  WARNING: load_dotenv not found in gateway main.py"
    echo "  The gateway may fail to load DATABASE_URL from .env"
fi

# 5. Start gateway
echo "[5/5] Starting gateway..."
if curl -sf "http://localhost:${GATEWAY_PORT}/health" &>/dev/null; then
    echo "  Gateway already running on port ${GATEWAY_PORT}"
    exit 0
fi

# Use setsid+nohup for persistent background process
(setsid nohup .venv/bin/uvicorn gateway.main:app \
    --host 0.0.0.0 \
    --port ${GATEWAY_PORT} \
    --app-dir apps/gateway/src \
    > /tmp/gateway.log 2>&1 < /dev/null &)

echo "  Waiting for startup..."
for i in $(seq 1 30); do
    sleep 2
    if curl -sf "http://localhost:${GATEWAY_PORT}/health" &>/dev/null; then
        echo ""
        echo "=== AI Workstation Gateway READY ==="
        echo "  URL:      http://localhost:${GATEWAY_PORT}"
        echo "  Health:   http://localhost:${GATEWAY_PORT}/health"
        echo "  Docs:     http://localhost:${GATEWAY_PORT}/docs"
        echo "  Logs:     tail -f /tmp/gateway.log"
        exit 0
    fi
    echo "  Waiting... ($((i*2))s)"
done

echo "WARNING: Gateway did not become healthy within 60 seconds." >&2
echo "Check logs: tail -f /tmp/gateway.log" >&2
echo "Common issues:" >&2
echo "  - DATABASE_URL not loading: check load_dotenv in main.py" >&2
echo "  - PostgreSQL not running: check port 5433" >&2
echo "  - OmniRoute gateway not running: run scripts/install_omniroute.sh" >&2
exit 1
