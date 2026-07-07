"""Shared Intelligence API endpoints — memory, journal, and context (Bible §7)."""
# pyright: reportGeneralTypeIssues=false

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.shared import memory as memory_service
from app.services.shared import context as context_service

router = APIRouter(prefix="/projects/{project_id}/shared", tags=["shared"])


# ─── Shared Memory ────────────────────────────────────────────────────────


@router.get("/memory", response_model=dict)
async def list_memory(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get all shared memory entries for a project."""
    entries = await memory_service.get_all_memory(db, project_id)
    return {"success": True, "data": {"entries": entries}, "message": "Operation successful"}


@router.get("/memory/latest/{memory_type}", response_model=dict)
async def get_latest_memory(
    project_id: str, memory_type: str, db: AsyncSession = Depends(get_db),
):
    """Get the latest memory entry for a specific type."""
    entry = await memory_service.get_latest_memory(db, project_id, memory_type)
    return {"success": True, "data": {"entry": entry}, "message": "Operation successful"}


@router.get("/memory/types", response_model=dict)
async def list_memory_types(project_id: str, db: AsyncSession = Depends(get_db)):
    """List all available memory types for a project."""
    types = await memory_service.get_all_memory_types(db, project_id)
    return {"success": True, "data": {"types": types}, "message": "Operation successful"}


# ─── Decision Journal ─────────────────────────────────────────────────────


@router.get("/decisions", response_model=dict)
async def list_decisions(
    project_id: str,
    category: str = Query(None, description="Filter by decision category"),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get decision journal entries, newest first."""
    entries = await memory_service.get_decisions(db, project_id, category=category, limit=limit)
    return {"success": True, "data": {"entries": entries, "count": len(entries)}, "message": "Operation successful"}


@router.get("/decisions/categories", response_model=dict)
async def list_decision_categories(project_id: str, db: AsyncSession = Depends(get_db)):
    """List all decision categories for a project."""
    categories = await memory_service.get_decision_categories(db, project_id)
    return {"success": True, "data": {"categories": categories}, "message": "Operation successful"}


# ─── Context ──────────────────────────────────────────────────────────────


@router.get("/context", response_model=dict)
async def get_shared_context(
    project_id: str,
    required: str = Query(None, description="Comma-separated memory types needed"),
    db: AsyncSession = Depends(get_db),
):
    """Get the complete shared context for specialist consumption."""
    required_list = required.split(",") if required else None
    ctx = await context_service.load_context(
        db, project_id, required_memory=required_list,
    )
    return {"success": True, "data": ctx, "message": "Operation successful"}
