from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.workflow import WorkflowCreate, WorkflowResponse
from app.core.workflow_engine import WorkflowEngine

router = APIRouter()


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(data: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    engine = WorkflowEngine(db)
    wf = await engine.create_workflow(data.workspace_id, data.name, data.description, data.steps, data.input)
    return wf


@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows(workspace_id: UUID, db: AsyncSession = Depends(get_db)):
    engine = WorkflowEngine(db)
    return await engine.list_workflows(workspace_id)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    engine = WorkflowEngine(db)
    wf = await engine.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.post("/{workflow_id}/execute", response_model=WorkflowResponse)
async def execute_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    engine = WorkflowEngine(db)
    wf = await engine.execute_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.post("/{workflow_id}/pause", response_model=WorkflowResponse)
async def pause_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    engine = WorkflowEngine(db)
    wf = await engine.pause_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.post("/{workflow_id}/resume", response_model=WorkflowResponse)
async def resume_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    engine = WorkflowEngine(db)
    wf = await engine.resume_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.post("/{workflow_id}/cancel", response_model=WorkflowResponse)
async def cancel_workflow(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    engine = WorkflowEngine(db)
    wf = await engine.cancel_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.get("/{workflow_id}/steps")
async def get_workflow_steps(workflow_id: UUID, db: AsyncSession = Depends(get_db)):
    engine = WorkflowEngine(db)
    wf = await engine.get_workflow(workflow_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"steps": wf.steps, "current_step": wf.current_step}
