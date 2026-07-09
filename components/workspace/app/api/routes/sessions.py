from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.session import (
    SessionCreate, SessionResponse, MessageCreate, MessageResponse,
    CheckpointResponse, SyncRequest, SyncResponse,
)
from app.core.session_manager import SessionManager
from app.sync.engine import SyncEngine

router = APIRouter()


@router.post("/", response_model=SessionResponse)
async def create_session(data: SessionCreate, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    session = await mgr.create_session(data.workspace_id, data.title, data.metadata)
    return SessionResponse.from_orm_model(session)


@router.get("/", response_model=list[SessionResponse])
async def list_sessions(workspace_id: UUID = Query(...), db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    sessions = await mgr.list_sessions(workspace_id)
    return [SessionResponse.from_orm_model(s) for s in sessions]


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    session = await mgr.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.from_orm_model(session)


@router.delete("/{session_id}")
async def delete_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    session = await mgr.archive_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "archived"}


@router.post("/{session_id}/messages", response_model=MessageResponse)
async def add_message(session_id: UUID, data: MessageCreate, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    msg = await mgr.add_message(session_id, data.role, data.content, data.tool_calls, data.tool_results)
    if not msg:
        raise HTTPException(status_code=404, detail="Session not found")
    return msg


@router.get("/{session_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    session_id: UUID,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    mgr = SessionManager(db)
    return await mgr.get_messages(session_id, limit, offset)


@router.post("/{session_id}/pause", response_model=SessionResponse)
async def pause_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    session = await mgr.pause_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.from_orm_model(session)


@router.post("/{session_id}/resume", response_model=SessionResponse)
async def resume_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    session = await mgr.resume_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.from_orm_model(session)


@router.post("/{session_id}/migrate", response_model=SessionResponse)
async def migrate_session(session_id: UUID, target_device_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    session = await mgr.migrate_session(session_id, target_device_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse.from_orm_model(session)


@router.post("/{session_id}/checkpoints", response_model=CheckpointResponse)
async def create_checkpoint(session_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    checkpoint = await mgr.create_checkpoint(session_id)
    if not checkpoint:
        raise HTTPException(status_code=404, detail="Session not found")
    return checkpoint


@router.get("/{session_id}/checkpoints", response_model=list[CheckpointResponse])
async def list_checkpoints(session_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    return await mgr.list_checkpoints(session_id)


@router.post("/{session_id}/checkpoints/{checkpoint_id}/restore", response_model=SessionResponse)
async def restore_checkpoint(session_id: UUID, checkpoint_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = SessionManager(db)
    session = await mgr.restore_checkpoint(session_id, checkpoint_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session or checkpoint not found")
    return SessionResponse.from_orm_model(session)


@router.post("/{session_id}/sync", response_model=SyncResponse)
async def sync_messages(session_id: UUID, data: SyncRequest, db: AsyncSession = Depends(get_db)):
    sync_engine = SyncEngine(db)
    messages_dicts = [m.model_dump() for m in data.messages]
    result = await sync_engine.sync_messages(session_id, messages_dicts, data.last_sequence)
    return result
