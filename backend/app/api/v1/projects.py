"""Project API endpoints — thin HTTP layer over ProjectService.
# pyright: reportAttributeAccessIssue=false, reportArgumentType=false
# SQLAlchemy Column descriptors resolve at runtime; Pyright false positive."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.project import ProjectStatus
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
    StateTransitionRequest,
    StateTransitionResponse,
)
from app.services import project as project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=dict, status_code=201)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """Create a new project in DRAFT state."""
    project = await project_service.create_project(
        db=db,
        idea=payload.idea,
        name=payload.name,
        description=payload.description,
    )
    return {
        "success": True,
        "data": ProjectResponse.model_validate(project).model_dump(),
        "message": "Project created.",
    }


@router.get("", response_model=dict)
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects, newest first."""
    projects = await project_service.list_projects(db)
    return {
        "success": True,
        "data": ProjectListResponse(
            projects=[ProjectResponse.model_validate(p) for p in projects]
        ).model_dump(),
        "message": "Operation successful",
    }


@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single project by ID."""
    project = await project_service.get_project(db, project_id)
    return {
        "success": True,
        "data": ProjectResponse.model_validate(project).model_dump(),
        "message": "Operation successful",
    }


@router.patch("/{project_id}", response_model=dict)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update project metadata. Does not change state."""
    project = await project_service.update_project(
        db=db,
        project_id=project_id,
        name=payload.name,
        description=payload.description,
        idea=payload.idea,
    )
    return {
        "success": True,
        "data": ProjectResponse.model_validate(project).model_dump(),
        "message": "Project updated.",
    }


@router.delete("/{project_id}", response_model=dict)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Hard-delete a project."""
    await project_service.delete_project(db, project_id)
    return {
        "success": True,
        "data": None,
        "message": "Project deleted.",
    }


@router.post("/{project_id}/transition", response_model=dict)
async def transition_project(
    project_id: str,
    payload: StateTransitionRequest,
    db: AsyncSession = Depends(get_db),
):
    """Transition a project to a new state.

    Valid transitions:
      DRAFT → PROCESSING, ARCHIVED
      PROCESSING → READY, DRAFT
      READY → DRAFT, ARCHIVED
      ARCHIVED → (terminal — no transitions out)
    """
    target = ProjectStatus(payload.transition)
    project = await project_service.transition_state(db, project_id, target)
    return {
        "success": True,
        "data": StateTransitionResponse(
            id=project.id,
            status=project.status,
            message=f"Project transitioned to '{project.status}'.",
        ).model_dump(),
        "message": "State transition successful.",
    }
