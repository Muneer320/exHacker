import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm.attributes import flag_modified

from app.db.session import get_db
from app.models.workflow import WorkflowStateModel
from app.schemas.state import WorkflowStatus, WorkflowStage
from app.services.workflow.engine import run_workflow

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
async def start_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    """Start workflow execution."""
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
    
    wf.status = WorkflowStatus.RUNNING.value
    flag_modified(wf, "state_json")
    db.add(wf)
    await db.commit()
    
    # Run graph execution loop
    final_state = await run_workflow(state)
    
    # Save results
    wf.state_json = final_state
    wf.status = final_state["metadata"]["status"]
    wf.current_stage = final_state["metadata"]["current_stage"]
    flag_modified(wf, "state_json")
    db.add(wf)
    await db.commit()
    
    return {
        "success": True,
        "data": {
            "workflow_id": workflow_id,
            "status": wf.status
        },
        "message": "Workflow started successfully."
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
async def resume_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    """Resume execution of paused workflow."""
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
    
    wf.status = WorkflowStatus.RUNNING.value
    flag_modified(wf, "state_json")
    db.add(wf)
    await db.commit()
    
    # Re-run graph
    final_state = await run_workflow(state)
    
    wf.state_json = final_state
    wf.status = final_state["metadata"]["status"]
    wf.current_stage = final_state["metadata"]["current_stage"]
    flag_modified(wf, "state_json")
    db.add(wf)
    await db.commit()
    
    return {
        "success": True,
        "data": {
            "status": wf.status
        },
        "message": "Workflow resumed successfully."
    }


@router.post("/{workflow_id}/restart")
async def restart_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    """Reset workflow and execute from start."""
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
    
    wf.status = WorkflowStatus.RUNNING.value
    wf.current_stage = WorkflowStage.CHALLENGE_INTELLIGENCE.value
    wf.state_json = state
    flag_modified(wf, "state_json")
    db.add(wf)
    await db.commit()
    
    # Run graph execution
    final_state = await run_workflow(state)
    
    wf.state_json = final_state
    wf.status = final_state["metadata"]["status"]
    wf.current_stage = final_state["metadata"]["current_stage"]
    flag_modified(wf, "state_json")
    db.add(wf)
    await db.commit()
    
    return {
        "success": True,
        "data": {
            "status": wf.status
        },
        "message": "Workflow restarted successfully."
    }
