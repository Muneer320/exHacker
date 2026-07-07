"""Research API endpoints — S2 Research Specialist (Bible §6.2 S2)."""
# pyright: reportArgumentType=false, reportGeneralTypeIssues=false

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.specialists import research_specialist

router = APIRouter(prefix="/projects/{project_id}/research", tags=["research"])


@router.post("", response_model=dict)
async def start_research(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run the S2 Research Specialist pipeline.

    Consumes Challenge Intelligence Report (S1) and produces structured
    research across 10 categories with synthesis, patterns, and recommendations.
    """
    result = await research_specialist.run_research(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Research complete.",
    }


@router.get("", response_model=dict)
async def get_research(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get cached research report without triggering new research."""
    from app.services.research import get_research as get_legacy
    result = await get_legacy(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Operation successful",
    }


@router.post("/refresh", response_model=dict)
async def refresh_research(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Force-refresh research, clearing any cached results."""
    from app.services.research import refresh_research as refresh_legacy
    result = await refresh_legacy(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Research refreshed.",
    }
