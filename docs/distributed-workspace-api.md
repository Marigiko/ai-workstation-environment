# Distributed AI Workspace — API Reference

## Overview

The Distributed AI Workspace provides a RESTful API for managing workspaces, sessions, tasks, workflows, notifications, and device presence across multiple devices.

**Base URL**: `http://localhost:8080`

**Interactive Docs**: `http://localhost:8080/docs` (Swagger UI)

## Authentication

All endpoints require either:
- `Authorization: Bearer <token>` header
- `X-API-Key: <key>` header

## Endpoints

### Workspaces

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workspaces` | Create workspace |
| GET | `/workspaces` | List workspaces |
| GET | `/workspaces/{id}` | Get workspace |
| PUT | `/workspaces/{id}` | Update workspace |
| DELETE | `/workspaces/{id}` | Delete workspace |
| POST | `/workspaces/{id}/devices` | Register device |
| GET | `/workspaces/{id}/devices` | List devices |
| DELETE | `/workspaces/{id}/devices/{device_id}` | Remove device |

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions` | Create session |
| GET | `/sessions?workspace_id=` | List sessions |
| GET | `/sessions/{id}` | Get session |
| DELETE | `/sessions/{id}` | Archive session |
| POST | `/sessions/{id}/messages` | Add message |
| GET | `/sessions/{id}/messages` | Get messages |
| POST | `/sessions/{id}/pause` | Pause session |
| POST | `/sessions/{id}/resume` | Resume session |
| POST | `/sessions/{id}/migrate?target_device_id=` | Migrate session |
| POST | `/sessions/{id}/checkpoints` | Create checkpoint |
| GET | `/sessions/{id}/checkpoints` | List checkpoints |
| POST | `/sessions/{id}/checkpoints/{cid}/restore` | Restore checkpoint |
| POST | `/sessions/{id}/sync` | Sync messages |

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks` | Create task |
| GET | `/tasks?workspace_id=` | List tasks |
| GET | `/tasks/{id}` | Get task |
| PUT | `/tasks/{id}` | Update task |
| DELETE | `/tasks/{id}` | Delete task |
| POST | `/tasks/{id}/pause` | Pause task |
| POST | `/tasks/{id}/resume` | Resume task |
| POST | `/tasks/{id}/cancel` | Cancel task |
| POST | `/tasks/{id}/restart` | Restart task |
| POST | `/tasks/{id}/approve` | Approve task |
| POST | `/tasks/{id}/reject` | Reject task |
| GET | `/tasks/{id}/logs` | Get task logs |
| GET | `/tasks/{id}/metrics` | Get task metrics |

### Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/workflows` | Create workflow |
| GET | `/workflows?workspace_id=` | List workflows |
| GET | `/workflows/{id}` | Get workflow |
| POST | `/workflows/{id}/execute` | Execute workflow |
| POST | `/workflows/{id}/pause` | Pause workflow |
| POST | `/workflows/{id}/resume` | Resume workflow |
| POST | `/workflows/{id}/cancel` | Cancel workflow |
| GET | `/workflows/{id}/steps` | Get workflow steps |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/notifications?workspace_id=` | List notifications |
| GET | `/notifications/{id}` | Get notification |
| POST | `/notifications/{id}/read` | Mark as read |
| POST | `/notifications/{id}/dismiss` | Dismiss notification |
| POST | `/notification-rules` | Create rule |
| GET | `/notification-rules?workspace_id=` | List rules |
| PUT | `/notification-rules/{id}` | Update rule |
| DELETE | `/notification-rules/{id}` | Delete rule |

### Presence

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/presence/heartbeat?device_id=` | Send heartbeat |
| GET | `/presence/devices?workspace_id=` | List online devices |
| GET | `/presence/users?workspace_id=` | List active users |
| GET | `/presence/activity?workspace_id=` | Get activity feed |

### WebSocket

Connect to `ws://localhost:8080/ws?workspace_id=<id>` for real-time events.

**Messages**:
```json
{
  "type": "session.message.new",
  "id": "msg_uuid",
  "timestamp": "2026-07-07T10:00:00Z",
  "workspace_id": "ws_uuid",
  "payload": { ... }
}
```

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

## Data Models

### Workspace
```json
{
  "id": "uuid",
  "name": "My Workspace",
  "description": "AI Engineering",
  "owner_id": "user-1",
  "metadata": {},
  "created_at": "2026-07-07T10:00:00Z",
  "updated_at": "2026-07-07T10:00:00Z"
}
```

### Session
```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "title": "Debug Session",
  "status": "active|paused|archived|migrating",
  "current_device_id": "uuid",
  "metadata": {},
  "created_at": "2026-07-07T10:00:00Z",
  "updated_at": "2026-07-07T10:00:00Z"
}
```

### Task
```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "title": "Run benchmark",
  "status": "pending|running|paused|completed|failed|cancelled",
  "priority": 5,
  "progress": 0.75,
  "duration_ms": 5000,
  "cost_usd": 0.05,
  "tokens_used": 300
}
```
