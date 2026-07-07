"""Architecture API endpoints — S7 Solution Architect (Bible §6.2 S7)."""
# pyright: reportGeneralTypeIssues=false

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.specialists import solution_architect

router = APIRouter(prefix="/projects/{project_id}/architecture", tags=["architecture"])


@router.post("", response_model=dict)
async def generate_architecture(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run the S7 Solution Architect pipeline.

    Generates a complete architecture blueprint including components,
    diagrams, frontend/backend architecture, database design, API contracts,
    authentication, scalability, and trade-offs.
    """
    result = await solution_architect.generate_architecture(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Architecture generated.",
    }


@router.get("", response_model=dict)
async def get_architecture(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get existing architecture without regenerating."""
    result = await solution_architect.get_architecture(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Operation successful",
    }


@router.post("/refresh", response_model=dict)
async def refresh_architecture(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Force-refresh architecture."""
    # Clear existing
    from app.models.architecture import ArchitectureBlueprint
    from sqlalchemy import delete as sa_delete
    await db.execute(sa_delete(ArchitectureBlueprint).where(ArchitectureBlueprint.project_id == project_id))
    await db.commit()
    result = await solution_architect.generate_architecture(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Architecture refreshed.",
    }
