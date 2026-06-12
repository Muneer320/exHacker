import uuid
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from sqlalchemy.orm.attributes import flag_modified
from app.db.session import get_db
from app.models.project import ProjectModel
from app.models.workflow import WorkflowStateModel
from app.schemas.api import ProjectCreateRequest, IdeaSelectRequest
from app.schemas.state import ExHackerStateSchema, WorkflowStatus, WorkflowStage
from app.services.workflow.engine import run_workflow, run_workflow_background

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreateRequest, db: AsyncSession = Depends(get_db)):
    """Initialize a project and its workflow state record."""
    project_id = str(uuid.uuid4())
    workflow_id = str(uuid.uuid4())
    
    # Store project
    project_db = ProjectModel(
        id=project_id,
        name=payload.name,
        challenge_statements=payload.challenge_statements,
        duration_hours=payload.duration_hours,
        team_profile=payload.team_profile.model_dump()
    )
    db.add(project_db)
    
    # Setup initial state
    now_str = datetime.datetime.utcnow().isoformat() + "Z"
    initial_state = {
        "metadata": {
            "workflow_id": workflow_id,
            "project_id": project_id,
            "status": WorkflowStatus.CREATED.value,
            "current_stage": WorkflowStage.CHALLENGE_INTELLIGENCE.value,
            "created_at": now_str,
            "updated_at": now_str
        },
        "project": {
            "id": project_id,
            "name": payload.name,
            "challenge_statements": payload.challenge_statements,
            "duration_hours": payload.duration_hours,
            "resources": [],
            "created_at": now_str
        },
        "team_profile": payload.team_profile.model_dump(),
        "execution": {
            "total_duration_seconds": 0.0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "provider_usage": [],
            "stage_metrics": []
        },
        "errors": []
    }
    
    # Validate structure using schema
    try:
        validated_state = ExHackerStateSchema(**initial_state)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Initial state schema validation failed: {str(e)}"
        )
        
    workflow_db = WorkflowStateModel(
        id=workflow_id,
        project_id=project_id,
        status=WorkflowStatus.CREATED.value,
        current_stage=WorkflowStage.CHALLENGE_INTELLIGENCE.value,
        state_json=validated_state.model_dump()
    )
    db.add(workflow_db)
    
    await db.commit()
    
    return {
        "success": True,
        "data": {
            "project_id": project_id,
            "workflow_id": workflow_id,
            "status": WorkflowStatus.CREATED.value
        },
        "message": "Project created and workflow initialized."
    }


@router.get("")
async def list_projects(db: AsyncSession = Depends(get_db)):
    """Retrieve all projects."""
    result = await db.execute(select(ProjectModel))
    projects = result.scalars().all()
    
    project_list = []
    for proj in projects:
        project_list.append({
            "id": proj.id,
            "name": proj.name,
            "challenge_statements": proj.challenge_statements,
            "duration_hours": proj.duration_hours,
            "team_profile": proj.team_profile,
            "created_at": proj.created_at.isoformat() + "Z"
        })
        
    return {
        "success": True,
        "data": {
            "projects": project_list
        },
        "message": "Operation successful"
    }


@router.get("/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve detailed project info."""
    result = await db.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    proj = result.scalar_one_or_none()
    
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PROJECT_NOT_FOUND",
                "message": f"Project {project_id} does not exist"
            }
        )
        
    return {
        "success": True,
        "data": {
            "project": {
                "id": proj.id,
                "name": proj.name,
                "challenge_statements": proj.challenge_statements,
                "duration_hours": proj.duration_hours,
                "team_profile": proj.team_profile,
                "created_at": proj.created_at.isoformat() + "Z"
            }
        },
        "message": "Operation successful"
    }


@router.get("/{project_id}/ideas")
async def get_project_ideas(project_id: str, db: AsyncSession = Depends(get_db)):
    """Fetch generated ideas and validation reports from workflow state."""
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.project_id == project_id))
    wf = result.scalar_one_or_none()
    
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow for project {project_id} not found"
            }
        )
        
    state = wf.state_json
    return {
        "success": True,
        "data": {
            "ideas": state.get("generated_ideas") or [],
            "validation_reports": state.get("validation_reports") or []
        },
        "message": "Operation successful"
    }


@router.post("/{project_id}/ideas/select")
async def select_idea(
    project_id: str,
    payload: IdeaSelectRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """User selects an idea. Resume the workflow engine in the background."""
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.project_id == project_id))
    wf = result.scalar_one_or_none()
    
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "WORKFLOW_NOT_FOUND",
                "message": f"Workflow for project {project_id} not found"
            }
        )
        
    state = wf.state_json
    ideas = state.get("generated_ideas") or []
    
    # Locate selected idea
    selected_idea = None
    for idea in ideas:
        if idea["id"] == payload.idea_id:
            selected_idea = idea
            break
            
    if not selected_idea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "IDEA_NOT_FOUND",
                "message": f"Idea {payload.idea_id} not found in generated ideas list."
            }
        )
        
    # Lock selected idea (user selection is immutable once written)
    state["selected_idea"] = selected_idea
    state["metadata"]["status"] = WorkflowStatus.RUNNING.value
    state["metadata"]["current_stage"] = WorkflowStage.TECH_STACK.value
    state["metadata"]["updated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    
    # Add selection confirmed log
    if "logs" not in state or state["logs"] is None:
        state["logs"] = []
    state["logs"].append({
        "stage": "human_selection",
        "message": f"Idea confirmed: '{selected_idea.get('title')}' chosen by user.",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    })
    
    wf.state_json = state
    wf.status = WorkflowStatus.RUNNING.value
    wf.current_stage = WorkflowStage.TECH_STACK.value
    flag_modified(wf, "state_json")
    db.add(wf)
    await db.commit()
    
    # Run the remaining workflow nodes as a background task
    background_tasks.add_task(run_workflow_background, wf.id)
    
    return {
        "success": True,
        "data": {
            "selected_idea": payload.idea_id,
            "workflow_status": wf.status
        },
        "message": "Idea confirmed. AI agents started generating full architecture, tech stack, build roadmap, pitch deck, and exports in the background."
    }


# Results queries
@router.get("/{project_id}/architecture")
async def get_architecture(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.project_id == project_id))
    wf = result.scalar_one_or_none()
    if not wf or not wf.state_json.get("architecture"):
        raise HTTPException(status_code=404, detail="Architecture package not generated yet.")
    return {"success": True, "data": {"architecture": wf.state_json["architecture"]}}


@router.get("/{project_id}/tech-stack")
async def get_tech_stack(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.project_id == project_id))
    wf = result.scalar_one_or_none()
    if not wf or not wf.state_json.get("tech_stack"):
        raise HTTPException(status_code=404, detail="Tech stack not recommended yet.")
    return {"success": True, "data": {"tech_stack": wf.state_json["tech_stack"]}}


@router.get("/{project_id}/presentation")
async def get_presentation(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.project_id == project_id))
    wf = result.scalar_one_or_none()
    if not wf or not wf.state_json.get("presentation"):
        raise HTTPException(status_code=404, detail="Presentation slides not generated yet.")
    return {"success": True, "data": {"presentation": wf.state_json["presentation"]}}


@router.get("/{project_id}/pitch")
async def get_pitch(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.project_id == project_id))
    wf = result.scalar_one_or_none()
    if not wf or not wf.state_json.get("pitch"):
        raise HTTPException(status_code=404, detail="Pitch coach plan not ready yet.")
    return {"success": True, "data": {"pitch": wf.state_json["pitch"]}}


@router.get("/{project_id}/exports")
async def get_exports(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkflowStateModel).where(WorkflowStateModel.project_id == project_id))
    wf = result.scalar_one_or_none()
    if not wf or not wf.state_json.get("exports"):
        raise HTTPException(status_code=404, detail="Exports package not ready yet.")
    return {"success": True, "data": {"exports": wf.state_json["exports"]}}
