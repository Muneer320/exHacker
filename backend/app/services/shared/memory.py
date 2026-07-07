"""Shared Project Memory service — structured specialist output store (Bible §7.4)."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, desc, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shared import SharedMemory, DecisionJournal, ReviewRecord

logger = logging.getLogger(__name__)


# ─── Shared Memory ───────────────────────────────────────────────────────


async def store_memory(
    db: AsyncSession,
    project_id: str,
    specialist: str,
    memory_type: str,
    content: dict[str, Any],
    confidence: Optional[float] = None,
    references: Optional[list[str]] = None,
    model_used: Optional[str] = None,
) -> dict[str, Any]:
    """Store a specialist output in shared memory (append-only).

    Each write creates a new version. Previous entries are never modified.
    """
    # Determine the next version number
    latest = await get_latest_memory(db, project_id, memory_type)
    version = (latest.get("version", 0) if latest else 0) + 1

    entry = SharedMemory(
        project_id=project_id,
        specialist=specialist,
        memory_type=memory_type,
        version=version,
        content=content,
        confidence=confidence,
        references=references or [],
        model_used=model_used,
        is_active=True,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    # Log decision for significant events
    if _is_significant_event(memory_type):
        await _log_from_memory(db, entry)

    return _memory_to_dict(entry)


async def get_latest_memory(
    db: AsyncSession,
    project_id: str,
    memory_type: str,
) -> Optional[dict[str, Any]]:
    """Get the latest active memory entry for a given type."""
    result = await db.execute(
        select(SharedMemory)
        .where(
            SharedMemory.project_id == project_id,
            SharedMemory.memory_type == memory_type,
            SharedMemory.is_active == True,
        )
        .order_by(desc(SharedMemory.version))
        .limit(1)
    )
    entry = result.scalar_one_or_none()
    return _memory_to_dict(entry) if entry else None


async def get_all_memory(
    db: AsyncSession,
    project_id: str,
) -> list[dict[str, Any]]:
    """Get all active memory entries for a project, newest first."""
    result = await db.execute(
        select(SharedMemory)
        .where(
            SharedMemory.project_id == project_id,
            SharedMemory.is_active == True,
        )
        .order_by(desc(SharedMemory.created_at))
    )
    return [_memory_to_dict(e) for e in result.scalars().all()]


async def get_memory_by_specialist(
    db: AsyncSession,
    project_id: str,
    specialist: str,
) -> list[dict[str, Any]]:
    """Get all memory entries from a specific specialist."""
    result = await db.execute(
        select(SharedMemory)
        .where(
            SharedMemory.project_id == project_id,
            SharedMemory.specialist == specialist,
            SharedMemory.is_active == True,
        )
        .order_by(desc(SharedMemory.version))
    )
    return [_memory_to_dict(e) for e in result.scalars().all()]


async def get_all_memory_types(
    db: AsyncSession,
    project_id: str,
) -> list[str]:
    """Get all distinct memory types available for a project."""
    result = await db.execute(
        select(SharedMemory.memory_type)
        .where(
            SharedMemory.project_id == project_id,
            SharedMemory.is_active == True,
        )
        .distinct()
    )
    return [row[0] for row in result.all()]


def _memory_to_dict(entry: SharedMemory) -> dict[str, Any]:
    """Convert a SharedMemory entry to a dict for API responses."""
    return {
        "id": entry.id,
        "project_id": entry.project_id,
        "specialist": entry.specialist,
        "memory_type": entry.memory_type,
        "version": entry.version,
        "content": entry.content,
        "confidence": entry.confidence,
        "references": entry.references or [],
        "model_used": entry.model_used,
        "is_active": entry.is_active,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


def _is_significant_event(memory_type: str) -> bool:
    """Determine if a memory write should automatically create a journal entry."""
    significant = {
        "direction_selected", "challenge_intelligence", "architecture",
        "tech_stack", "plan_generated",
    }
    return memory_type in significant


async def _log_from_memory(db: AsyncSession, entry: SharedMemory) -> None:
    """Automatically create a journal entry from a significant memory write."""
    content = entry.content or {}
    title_map = {
        "challenge_intelligence": "Challenge analyzed",
        "direction_selected": "Product direction selected",
        "architecture": "System architecture defined",
        "tech_stack": "Technology stack chosen",
        "plan_generated": "Implementation plan generated",
    }
    title = title_map.get(entry.memory_type, f"{entry.specialist} completed")
    await log_decision(
        db,
        project_id=entry.project_id,
        title=title,
        category="specialist_review",
        description=content.get("summary", content.get("executive_summary", title))[:500],
        originating_specialist=entry.specialist,
        confidence=entry.confidence,
        references=[entry.id],
    )


# ─── Decision Journal ────────────────────────────────────────────────────


async def log_decision(
    db: AsyncSession,
    project_id: str,
    title: str,
    category: str,
    description: str,
    rationale: Optional[str] = None,
    alternatives_considered: Optional[list[dict[str, Any]]] = None,
    confidence: Optional[float] = None,
    originating_specialist: str = "system",
    references: Optional[list[str]] = None,
    status: str = "accepted",
) -> dict[str, Any]:
    """Log an immutable decision entry (Bible §7.5).

    Decisions are append-only. New entries supersede old ones.
    """
    # Get the next entry number for this project
    max_entry = await db.execute(
        select(func.max(DecisionJournal.entry_number))
        .where(DecisionJournal.project_id == project_id)
    )
    next_number = (max_entry.scalar() or 0) + 1

    entry = DecisionJournal(
        project_id=project_id,
        entry_number=next_number,
        title=title,
        category=category,
        description=description,
        rationale=rationale,
        alternatives_considered=alternatives_considered or [],
        confidence=confidence,
        originating_specialist=originating_specialist,
        references=references or [],
        status=status,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return _decision_to_dict(entry)


async def get_decisions(
    db: AsyncSession,
    project_id: str,
    category: Optional[str] = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Get decision journal entries, newest first."""
    query = select(DecisionJournal).where(
        DecisionJournal.project_id == project_id,
    )
    if category:
        query = query.where(DecisionJournal.category == category)
    query = query.order_by(desc(DecisionJournal.entry_number)).limit(limit)

    result = await db.execute(query)
    return [_decision_to_dict(e) for e in result.scalars().all()]


async def get_decision_categories(
    db: AsyncSession,
    project_id: str,
) -> list[str]:
    """Get all distinct decision categories for a project."""
    result = await db.execute(
        select(DecisionJournal.category)
        .where(DecisionJournal.project_id == project_id)
        .distinct()
    )
    return [row[0] for row in result.all()]


def _decision_to_dict(entry: DecisionJournal) -> dict[str, Any]:
    """Convert a DecisionJournal entry to a dict for API responses."""
    return {
        "id": entry.id,
        "project_id": entry.project_id,
        "entry_number": entry.entry_number,
        "title": entry.title,
        "category": entry.category,
        "description": entry.description,
        "rationale": entry.rationale,
        "alternatives_considered": entry.alternatives_considered or [],
        "confidence": entry.confidence,
        "originating_specialist": entry.originating_specialist,
        "references": entry.references or [],
        "status": entry.status,
        "superseded_by": entry.superseded_by,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
    }
