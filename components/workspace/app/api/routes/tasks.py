from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.core.task_manager import TaskManager

router = APIRouter()


@router.post("/", response_model=TaskResponse)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    task = await mgr.create_task(
        data.workspace_id, data.title, data.description, data.priority,
        data.agent_id, data.model, data.session_id, data.input,
    )
    return task


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    workspace_id: UUID = Query(...),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    mgr = TaskManager(db)
    return await mgr.list_tasks(workspace_id, status)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    task = await mgr.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: UUID, data: TaskUpdate, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    updates = data.model_dump(exclude_unset=True)
    task = await mgr.update_task(task_id, **updates)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    deleted = await mgr.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "deleted"}


@router.post("/{task_id}/pause", response_model=TaskResponse)
async def pause_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    task = await mgr.pause_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/resume", response_model=TaskResponse)
async def resume_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    task = await mgr.resume_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/cancel", response_model=TaskResponse)
async def cancel_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    task = await mgr.cancel_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/restart", response_model=TaskResponse)
async def restart_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    task = await mgr.restart_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/approve", response_model=TaskResponse)
async def approve_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    task = await mgr.approve_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/reject", response_model=TaskResponse)
async def reject_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    task = await mgr.reject_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{task_id}/logs")
async def get_task_logs(task_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    task = await mgr.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"logs": task.logs}


@router.get("/{task_id}/metrics")
async def get_task_metrics(task_id: UUID, db: AsyncSession = Depends(get_db)):
    mgr = TaskManager(db)
    task = await mgr.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "duration_ms": task.duration_ms,
        "cost_usd": task.cost_usd,
        "tokens_used": task.tokens_used,
    }
