# AGENTS.md — AI Proxy Server

## Component Overview

AI Proxy Server is a local proxy that sits between Terax/clients and LLM backends (MiMo and Claude). It exposes an **OpenAI-compatible API** (`/v1/chat/completions`) and automatically compresses all requests using **Headroom** before forwarding — saving 60-90% of tokens with zero API keys required.

## Tech Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI + Uvicorn
- **Data validation**: Pydantic v2
- **Compression engine**: Headroom (custom, `headroom.py`)
- **Backends**: MiMo CLI (`mimo run`), Claude CLI (`claude -p`)
- **Shell scripts**: Bash 5+ (`set -euo pipefail`)

## Project Structure

```
components/ai-proxy/
├── server.py          # FastAPI app — routes, backend handlers, model registry
├── headroom.py        # Headroom context compression engine
├── config.yaml        # Server/backend/headroom/model configuration
├── start.sh           # Process manager (start/stop/restart/status)
├── client.sh          # CLI client for quick testing
└── fibonacci.py       # Demo/utility — fibonacci via DP
```

## Commands

```bash
# Start the server
./start.sh start           # Start on port 8090 (background)
./start.sh stop            # Stop the server
./start.sh restart         # Restart
./start.sh status          # Check health + PID

# Test via CLI client
./client.sh mimo-auto "hello world"
./client.sh claude "write a python function"
echo "explain this code" | ./client.sh local

# Direct API calls
curl http://localhost:8090/health
curl -X POST http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"mimo-auto","messages":[{"role":"user","content":"hello"}]}'

# Compression-only endpoint (no LLM call)
curl -X POST http://localhost:8090/v1/compress \
  -H "Content-Type: application/json" \
  -d '{"model":"mimo-auto","messages":[{"role":"user","content":"hello world"}]}'
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server health, version, backend status |
| GET | `/v1/models` | List available models |
| POST | `/v1/chat/completions` | OpenAI-compatible chat completion (with Headroom compression) |
| POST | `/v1/compress` | Standalone compression — returns compressed messages without LLM call |

## Models

| Model ID | Handler | Description |
|----------|---------|-------------|
| `mimo` | MiMoHandler | MiMo Auto (free, no API key) |
| `mimo-auto` | MiMoHandler | MiMo Auto channel |
| `mimo-fast` | MiMoHandler | MiMo Fast (free) |
| `claude` | ClaudeHandler | Claude Code (requires `claude login`) |
| `claude-code` | ClaudeHandler | Claude Code |
| `local` | MiMoHandler | Local model via MiMo |
| `smart` | ClaudeHandler | Smart model via Claude |

## Headroom Compression

The `headroom.py` engine applies a pipeline to every request before forwarding:

1. **Noise stripping** — removes ANSI codes, ASCII art, build banners
2. **Whitespace normalization** — collapses excess spaces, blank lines
3. **Comment stripping** — removes code comments (preserves code blocks)
4. **Line deduplication** — removes repeated lines (content-hash based)
5. **Aggressive compression** — empty literals, collapsed operators, import simplification
6. **Context truncation** — fits within `max_tokens` budget (default 4096)

Config is in `config.yaml` under `headroom:`. Can be disabled per-request with `"headroom": false`.

## Configuration

`config.yaml` controls:
- `server` — host, port (default 8090), workers
- `backends` — binary paths and timeouts for MiMo and Claude
- `headroom` — compression settings (enabled, max_tokens, aggressive, preserve_code, etc.)
- `models` — model routing table (model_id → handler)
- `rate_limit` — requests/tokens per minute
- `logging` — level and format

## Conventions

- **No API keys needed** — MiMo is free, Claude uses `claude login` (browser auth)
- **Binary discovery** — handlers search PATH and common install locations for `mimo`/`claude`
- **Output cleaning** — MiMoHandler strips ANSI codes, CLI banners, and noise from responses
- **OpenAI-compatible** — request/response format matches OpenAI's Chat Completions API
- **CORS** — fully open (`allow_origins=["*"]`) for local development
- **Process management** — `start.sh` uses PID file at `/tmp/ai-proxy.pid`, logs to `/tmp/ai-proxy.log`

## Key Design Decisions

- **Headroom-first**: Every request is compressed before reaching the backend — transparent to clients
- **CLI wrappers, not SDKs**: Backends are invoked via CLI subprocess (`mimo run`, `claude -p`) — no API dependencies
- **Single-process**: Uvicorn runs with 1 worker; PID file for lifecycle management
- **Local-only**: Designed for single-user local workstation use, not production multi-tenant
