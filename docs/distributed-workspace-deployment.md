# Distributed AI Workspace — Deployment Guide

> Historical document (written before 2026-09-25). LiteLLM was later replaced by OmniRoute (http://localhost:20128/v1); see docs/INTEGRATION-ARCHITECTURE.md for the current setup.

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL (from platform or external)
- Redis (included in docker-compose)

## Quick Start

```bash
# 1. Install workspace component
./bootstrap bootstrap --only workspace

# 2. Or install with full profile
./bootstrap bootstrap --profile host
```

## Docker Compose Services

| Service | Container | Port | Description |
|---------|-----------|------|-------------|
| workspace-api | awe-workspace-api | 8080 | FastAPI REST + WebSocket |
| workspace-worker | awe-workspace-worker | — | Background event processor |
| redis | awe-workspace-redis | 6379 | Pub/Sub + cache |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql+asyncpg://postgres:postgres@localhost:5432/workspace | PostgreSQL connection |
| REDIS_URL | redis://localhost:6379/0 | Redis connection |
| QDRANT_URL | http://localhost:6333 | Qdrant vector DB |
| LITELLM_URL | http://localhost:4000 | LiteLLM gateway |
| SECRET_KEY | change-me-in-production | JWT secret |

## Database Setup

```bash
# Create database
createdb workspace

# Run migrations
cd components/workspace
alembic upgrade head
```

## Manual Start (without Docker)

```bash
cd components/workspace
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Health Check

```bash
curl http://localhost:8080/health
# {"status": "ok", "version": "0.1.0"}
```

## Architecture

```
Clients (Hermes/MiMo/OpenCode/Claude/Web)
    ↓ REST + WebSocket
API Gateway (FastAPI :8080)
    ↓
Workspace Layer
├── Workspace Manager
├── Session Manager
├── Task Manager
├── Workflow Engine
├── Notification Service
└── Presence Service
    ↓ Event Bus (Redis)
AI Engineering Platform (LiteLLM, Ollama, Qdrant, n8n, MCP)
    ↓
Storage (PostgreSQL + Redis)
```
