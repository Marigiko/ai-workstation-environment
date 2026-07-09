from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db, dispose_db
from app.api.routes import workspaces, sessions, tasks, workflows, notifications, presence
from app.api.websocket.handler import websocket_endpoint
from app.api.middleware.logging import RequestLoggingMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="Distributed AI Workspace",
        description="Multi-device AI Engineering Workspace Manager",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    app.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
    app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
    app.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
    app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
    app.include_router(notifications.rules_router, prefix="/notification-rules", tags=["notification-rules"])
    app.include_router(presence.router, prefix="/presence", tags=["presence"])

    app.add_api_websocket_route("/ws", websocket_endpoint)

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    @app.on_event("startup")
    async def startup():
        init_db()
        from app.database import engine
        from app.database import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        from app.events.bus import event_bus
        await event_bus.connect()

    @app.on_event("shutdown")
    async def shutdown():
        from app.events.bus import event_bus
        await event_bus.disconnect()
        await dispose_db()

    return app


app = create_app()
