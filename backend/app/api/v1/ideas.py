"""Idea Generation API endpoints — S5 (Bible §6.2 S5)."""
# pyright: reportGeneralTypeIssues=false

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.specialists import idea_generator

router = APIRouter(prefix="/projects/{project_id}/ideas", tags=["ideas"])


@router.post("", response_model=dict)
async def generate_ideas(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run the S5 Idea Generation pipeline.

    Consumes shared context (S1+S2+S3) and generates 5 differentiated
    product ideas with full scoring, reasoning, and comparisons.
    """
    result = await idea_generator.generate_ideas(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Ideas generated.",
    }


@router.get("", response_model=dict)
async def get_ideas(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get existing ideas without regenerating."""
    result = await idea_generator.get_ideas(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Operation successful",
    }


@router.post("/{idea_id}/select", response_model=dict)
async def select_idea(
    project_id: str,
    idea_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Select an idea as the project direction."""
    result = await idea_generator.select_idea(db, project_id, idea_id)
    return {
        "success": True,
        "data": {"idea": result},
        "message": "Idea selected.",
    }


@router.post("/refresh", response_model=dict)
async def refresh_ideas(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Force-refresh and regenerate ideas."""
    result = await idea_generator.refresh_ideas(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Ideas refreshed.",
    }
