import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.attributes import flag_modified

from app.db.session import get_db
from app.models.workflow import WorkflowStateModel
from app.schemas.state import WorkflowStatus, WorkflowStage
from app.services.workflow.engine import run_workflow, run_workflow_background

router = APIRouter()


# Map stages to estimated progress percentages for UI tracking
STAGE_PROGRESS_MAP = {
    "challenge_intelligence": 10,
    "problem_analysis": 20,
    "opportunity_discovery": 30,
    "idea_generation": 40,
    "idea_validation": 50,
    "human_selection": 60,
    "tech_stack": 70,
    "architecture": 80,
    "build_accelerator": 85,
    "presentation": 90,
    "pitch": 95,
    "export": 100
}


@router.post("/{workflow_id}/start")
async def start_workflow(workflow_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Start workflow execution in the background."""
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.id == workflow_id))
    wf = result.scalar_one_or_none()
    
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow {workflow_id} not found"
            }
        )
        
    if wf.status == WorkflowStatus.RUNNING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "WORKFLOW_ALREADY_RUNNING",
                "message": f"Workflow {workflow_id} is already executing."
            }
        )
        
    state = wf.state_json
    state["metadata"]["status"] = WorkflowStatus.RUNNING.value
    state["metadata"]["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    
    # Add start log
    if "logs" not in state or state["logs"] is None:
        state["logs"] = []
    state["logs"].append({
        "stage": "system",
        "message": "Workflow started by user.",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    })
    
    wf.status = WorkflowStatus.RUNNING.value
    wf.state_json = state
    flag_modified(wf, "state_json")
    db.add(wf)
    await db.commit()
    
    # Run graph execution loop in background
    background_tasks.add_task(run_workflow_background, workflow_id)
    
    return {
        "success": True,
        "data": {
            "workflow_id": workflow_id,
            "status": wf.status
        },
        "message": "Workflow started successfully in background."
    }


@router.get("/{workflow_id}")
async def get_workflow_status(workflow_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve current progress and stage metrics."""
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.id == workflow_id))
    wf = result.scalar_one_or_none()
    
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow {workflow_id} not found"
            }
        )
        
    progress = STAGE_PROGRESS_MAP.get(wf.current_stage, 0)
    if wf.status == WorkflowStatus.COMPLETED.value:
        progress = 100
        
    return {
        "success": True,
        "data": {
            "workflow_id": workflow_id,
            "status": wf.status,
            "current_stage": wf.current_stage,
            "progress": progress
        },
        "message": "Operation successful"
    }


@router.get("/{workflow_id}/state")
async def get_workflow_state(workflow_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve full state snapshot of the workflow."""
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.id == workflow_id))
    wf = result.scalar_one_or_none()
    
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow {workflow_id} not found"
            }
        )
        
    return {
        "success": True,
        "data": {
            "state": wf.state_json
        },
        "message": "Operation successful"
    }


@router.post("/{workflow_id}/resume")
async def resume_workflow(workflow_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Resume execution of paused workflow in the background."""
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.id == workflow_id))
    wf = result.scalar_one_or_none()
    
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow {workflow_id} not found"
            }
        )
        
    state = wf.state_json
    
    # If waiting for selection and selected_idea is missing, we cannot resume
    if wf.current_stage == WorkflowStage.HUMAN_SELECTION.value and state.get("selected_idea") is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "WORKFLOW_PAUSED",
                "message": "Cannot resume: user selection is missing. Please select an idea first."
            }
        )
        
    state["metadata"]["status"] = WorkflowStatus.RUNNING.value
    state["metadata"]["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    
    # Add resume log
    if "logs" not in state or state["logs"] is None:
        state["logs"] = []
    state["logs"].append({
        "stage": "system",
        "message": "Workflow resumed by user.",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    })
    
    wf.status = WorkflowStatus.RUNNING.value
    wf.state_json = state
    flag_modified(wf, "state_json")
    db.add(wf)
    await db.commit()
    
    # Re-run graph in background
    background_tasks.add_task(run_workflow_background, workflow_id)
    
    return {
        "success": True,
        "data": {
            "status": wf.status
        },
        "message": "Workflow resumed successfully."
    }


@router.post("/{workflow_id}/restart")
async def restart_workflow(workflow_id: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """Reset workflow and execute from start in the background."""
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.id == workflow_id))
    wf = result.scalar_one_or_none()
    
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow {workflow_id} not found"
            }
        )
        
    state = wf.state_json
    
    # Clear all domains to force re-execution
    state["challenge_intelligence"] = None
    state["problem_analysis"] = None
    state["opportunity_analysis"] = None
    state["generated_ideas"] = None
    state["validation_reports"] = None
    state["selected_idea"] = None
    state["tech_stack"] = None
    state["architecture"] = None
    state["build_package"] = None
    state["prompt_package"] = None
    state["presentation"] = None
    state["pitch"] = None
    state["exports"] = None
    state["errors"] = []
    state["logs"] = []
    
    # Reset execution metrics
    state["execution"] = {
        "total_duration_seconds": 0.0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "provider_usage": [],
        "stage_metrics": []
    }
    
    state["metadata"]["status"] = WorkflowStatus.RUNNING.value
    state["metadata"]["current_stage"] = WorkflowStage.CHALLENGE_INTELLIGENCE.value
    state["metadata"]["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    
    # Add restart log
    state["logs"].append({
        "stage": "system",
        "message": "Workflow restarted by user.",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    })
    
    wf.status = WorkflowStatus.RUNNING.value
    wf.current_stage = WorkflowStage.CHALLENGE_INTELLIGENCE.value
    wf.state_json = state
    flag_modified(wf, "state_json")
    db.add(wf)
    await db.commit()
    
    # Run graph execution in background
    background_tasks.add_task(run_workflow_background, workflow_id)
    
    return {
        "success": True,
        "data": {
            "status": wf.status
        },
        "message": "Workflow restarted successfully."
    }
