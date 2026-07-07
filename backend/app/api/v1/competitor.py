"""Competitor Intelligence API endpoints — S3 Competitor Analyst (Bible §6.2 S3)."""
# pyright: reportGeneralTypeIssues=false

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.specialists import competitor_analyst

router = APIRouter(prefix="/projects/{project_id}/competitors", tags=["competitors"])


@router.post("", response_model=dict)
async def analyze_competitors(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Run the S3 Competitor Intelligence pipeline.

    Consumes Challenge Intelligence (S1) + Research Report (S2) and produces
    competitor profiles, comparison matrix, gap analysis, differentiation
    opportunities, innovation scores, and warnings.
    """
    result = await competitor_analyst.analyze_competitors(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Competitor analysis complete.",
    }


@router.get("", response_model=dict)
async def get_competitor_analysis(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get existing competitor analysis without regenerating."""
    result = await competitor_analyst.get_analysis(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Operation successful",
    }


@router.post("/refresh", response_model=dict)
async def refresh_competitor_analysis(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Force-refresh competitor analysis."""
    result = await competitor_analyst.refresh_analysis(db, project_id)
    return {
        "success": True,
        "data": result,
        "message": "Competitor analysis refreshed.",
    }
