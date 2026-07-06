"""Research API endpoints — thin HTTP layer over ResearchService."""

from __future__ import annotations
# pyright: reportArgumentType=false

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services import research as research_service

router = APIRouter(prefix="/projects/{project_id}/research", tags=["research"])


@router.post("", response_model=dict)
async def start_research(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Start or retrieve research for a project.

    Returns cached results if available (24h freshness).
    Runs full research pipeline if cache is stale or empty.
    """
    results = await research_service.run_research(db, project_id)
    return {
        "success": True,
        "data": results,
        "message": "Research complete.",
    }


@router.get("", response_model=dict)
async def get_research(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get cached research results without triggering a new search."""
    results = await research_service.get_research(db, project_id)
    return {
        "success": True,
        "data": results,
        "message": "Operation successful",
    }


@router.post("/refresh", response_model=dict)
async def refresh_research(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Force-refresh research, clearing any cached results."""
    results = await research_service.refresh_research(db, project_id)
    return {
        "success": True,
        "data": results,
        "message": "Research refreshed.",
    }
