# Distributed AI Workspace — Client Integration Guide

## Overview

The Distributed AI Workspace supports multiple AI clients via adapter layers. Each adapter translates between the client's native protocol and the workspace API.

## Supported Clients

| Client | Adapter | Protocol | Status |
|--------|---------|----------|--------|
| Hermes | hermes_adapter.py | MCP/ACP | Implemented |
| MiMo Code | mimo_adapter.py | Terminal/OSC | Implemented |
| OpenCode | opencode_adapter.py | REST API | Implemented |
| Claude Code | (manual) | Terminal | Manual |

## Integration Patterns

### Hermes Integration

Hermes connects to the workspace via the adapter layer:

```python
from app.adapters.hermes_adapter import HermesAdapter

adapter = HermesAdapter("http://localhost:8081")
await adapter.connect()

# Send message to session
await adapter.send_message(session_id, {"role": "user", "content": "Hello"})

# Sync state
state = await adapter.sync_state(session_id)
```

### MiMo Integration

MiMo connects via terminal and OSC markers:

```python
from app.adapters.mimo_adapter import MimoAdapter

adapter = MimoAdapter("http://localhost:3000")
await adapter.connect()

# MiMo auto-detects via OSC 777 markers
# Session state synced via REST API
```

### OpenCode Integration

OpenCode connects via REST API:

```python
from app.adapters.opencode_adapter import OpenCodeAdapter

adapter = OpenCodeAdapter("http://localhost:3001")
await adapter.connect()
```

## Custom Adapter

To add a new client adapter:

1. Create `app/adapters/my_adapter.py`
2. Implement `BaseAdapter` interface
3. Register in `app/adapters/__init__.py`

```python
from app.adapters import BaseAdapter

class MyAdapter(BaseAdapter):
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def send_message(self, session_id: str, message: dict) -> dict: ...
    async def receive_messages(self, session_id: str) -> AsyncIterator[dict]: ...
    async def sync_state(self, session_id: str) -> dict: ...
    async def get_status(self) -> dict: ...
```

## Session Migration

To migrate a session between devices:

1. Device A pauses session: `POST /sessions/{id}/pause`
2. Create checkpoint: `POST /sessions/{id}/checkpoints`
3. Migrate to Device B: `POST /sessions/{id}/migrate?target_device_id=B`
4. Device B resumes: `POST /sessions/{id}/resume`

## Real-Time Events

Connect via WebSocket for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8080/ws?workspace_id=ws_uuid');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data.payload);
};

// Event types:
// session.created, session.message.new, session.paused, session.resumed
// task.created, task.started, task.progress, task.completed, task.failed
// device.online, device.offline
```
