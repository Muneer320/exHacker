"""Blueprint API endpoints."""
# pyright: reportGeneralTypeIssues=false

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.blueprint.coordinator import generate_blueprint

router = APIRouter(prefix="/projects/{project_id}/blueprint", tags=["blueprint"])


@router.post("", response_model=dict)
async def create_blueprint(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Generate a complete project blueprint (tech stack, architecture, data model, plan)."""
    from app.services.project import get_project

    project = await get_project(db, project_id)
    blueprint = await generate_blueprint(idea=project.idea)
    return {
        "success": True,
        "data": {"blueprint": blueprint},
        "message": "Blueprint generated.",
    }


@router.post("/basic", response_model=dict)
async def create_basic_blueprint(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Generate a basic blueprint without AI enrichment (faster, deterministic only)."""
    from app.services.project import get_project

    project = await get_project(db, project_id)
    blueprint = await generate_blueprint(idea=project.idea, enrich_architecture=False)
    return {
        "success": True,
        "data": {"blueprint": blueprint},
        "message": "Basic blueprint generated (no AI enrichment).",
    }
