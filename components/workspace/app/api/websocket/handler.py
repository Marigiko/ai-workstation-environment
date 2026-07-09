import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from app.events.bus import event_bus, Event


class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, workspace_id: str):
        await websocket.accept()
        if workspace_id not in self.connections:
            self.connections[workspace_id] = set()
        self.connections[workspace_id].add(websocket)

    def disconnect(self, websocket: WebSocket, workspace_id: str):
        if workspace_id in self.connections:
            self.connections[workspace_id].discard(websocket)

    async def broadcast(self, workspace_id: str, message: dict):
        if workspace_id in self.connections:
            dead = []
            for ws in self.connections[workspace_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.connections[workspace_id].discard(ws)

    async def send_personal(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_json(message)
        except Exception:
            pass


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    workspace_id = websocket.query_params.get("workspace_id", "default")

    await manager.connect(websocket, workspace_id)

    async def event_handler(data: dict):
        await manager.broadcast(workspace_id, data)

    await event_bus.subscribe(workspace_id, event_handler)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type", "")

                if msg_type == "ping":
                    await manager.send_personal(websocket, {"type": "pong"})
                elif msg_type == "subscribe":
                    pass
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, workspace_id)
