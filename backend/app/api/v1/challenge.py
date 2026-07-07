"""Challenge Intelligence API endpoints — thin HTTP layer over S1 Challenge Analyst."""
# pyright: reportGeneralTypeIssues=false, reportArgumentType=false

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.specialists import challenge_analyst

router = APIRouter(prefix="/projects/{project_id}/challenge", tags=["challenge"])


@router.post("", response_model=dict)
async def analyze_challenge(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run the Challenge Intelligence pipeline (S1) for a project.

    Produces a structured report: executive summary, core problem analysis,
    hidden problems, stakeholders, constraints, success criteria,
    opportunity areas, innovation opportunities, risks, difficulty assessment,
    and recommended strategy.
    """
    result = await challenge_analyst.analyze_challenge(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Challenge analysis complete.",
    }


@router.get("", response_model=dict)
async def get_challenge_analysis(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get existing challenge analysis without regenerating."""
    result = await challenge_analyst.get_analysis(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Operation successful",
    }


@router.post("/refresh", response_model=dict)
async def refresh_challenge_analysis(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Force-refresh challenge analysis."""
    result = await challenge_analyst.refresh_analysis(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Challenge analysis refreshed.",
    }
