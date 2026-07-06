"""Direction API endpoints."""
# pyright: reportArgumentType=false

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.blueprint import directions as directions_service

router = APIRouter(prefix="/projects/{project_id}/directions", tags=["directions"])


@router.post("", response_model=dict)
async def generate_directions(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Generate product directions from research data."""
    results = await directions_service.generate_directions(db, project_id)
    return {
        "success": True,
        "data": {"directions": results},
        "message": "Directions generated.",
    }


@router.get("", response_model=dict)
async def get_directions(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get stored directions for a project."""
    results = await directions_service.get_directions(db, project_id)
    return {
        "success": True,
        "data": {"directions": results},
        "message": "Operation successful",
    }


@router.post("/{direction_id}/select", response_model=dict)
async def select_direction(
    project_id: str,
    direction_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Select a direction. Unselects others. Transitions project to READY."""
    result = await directions_service.select_direction(db, project_id, direction_id)
    return {
        "success": True,
        "data": {"direction": result},
        "message": "Direction selected. Project is now ready.",
    }
