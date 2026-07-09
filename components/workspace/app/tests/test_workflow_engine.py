import pytest
from uuid import uuid4
from app.core.workspace_manager import WorkspaceManager
from app.core.workflow_engine import WorkflowEngine


@pytest.fixture
async def workspace(db):
    mgr = WorkspaceManager(db)
    return await mgr.create_workspace("WF WS", "", "owner-1")


@pytest.mark.asyncio
async def test_create_workflow(db, workspace):
    engine = WorkflowEngine(db)
    steps = [{"name": "step1", "type": "http"}, {"name": "step2", "type": "script"}]
    wf = await engine.create_workflow(workspace.id, "Test WF", "Desc", steps)
    assert wf.name == "Test WF"
    assert len(wf.steps) == 2


@pytest.mark.asyncio
async def test_execute_workflow(db, workspace):
    engine = WorkflowEngine(db)
    steps = [{"name": "step1", "type": "http"}]
    wf = await engine.create_workflow(workspace.id, "Exec WF", "", steps)
    executed = await engine.execute_workflow(wf.id)
    assert executed.status == "running"


@pytest.mark.asyncio
async def test_pause_resume_workflow(db, workspace):
    engine = WorkflowEngine(db)
    steps = [{"name": "step1", "type": "http"}]
    wf = await engine.create_workflow(workspace.id, "Pause WF", "", steps)
    await engine.execute_workflow(wf.id)
    paused = await engine.pause_workflow(wf.id)
    assert paused.status == "paused"
    resumed = await engine.resume_workflow(wf.id)
    assert resumed.status == "running"


@pytest.mark.asyncio
async def test_cancel_workflow(db, workspace):
    engine = WorkflowEngine(db)
    steps = [{"name": "step1", "type": "http"}]
    wf = await engine.create_workflow(workspace.id, "Cancel WF", "", steps)
    await engine.execute_workflow(wf.id)
    cancelled = await engine.cancel_workflow(wf.id)
    assert cancelled.status == "cancelled"


@pytest.mark.asyncio
async def test_list_workflows(db, workspace):
    engine = WorkflowEngine(db)
    steps = [{"name": "step1", "type": "http"}]
    await engine.create_workflow(workspace.id, "WF1", "", steps)
    await engine.create_workflow(workspace.id, "WF2", "", steps)
    wfs = await engine.list_workflows(workspace.id)
    assert len(wfs) >= 2
