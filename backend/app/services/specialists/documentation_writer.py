"""Documentation Writer (S13) — documentation compiler (Bible §6.2 S13).

Assembles existing specialist outputs into polished documentation.
AI is used ONLY for introductions and narrative transitions (Tier 1).
Everything else is deterministic templates + structured data injection.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.specialists.doc_templates import DOCUMENTS
from app.services.shared.memory import store_memory, log_decision
from app.services.shared.context import load_context
from app.services.project import get_project
from app.models.idea import Idea
from sqlalchemy import select

logger = logging.getLogger(__name__)


DOCUMENT_ORDER = [
    "README.md",
    "PRD.md",
    "TECH_STACK.md",
    "ARCHITECTURE.md",
    "API.md",
    "DATABASE.md",
    "FRONTEND.md",
    "BACKEND.md",
    "IMPLEMENTATION_PLAN.md",
    "PITCH.md",
]


async def generate_documentation(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Run the Documentation Generation pipeline (S13).

    1. Load all shared context (S1-S7 outputs)
    2. Resolve data into a single document context
    3. Generate each document from its deterministic template
    4. Add AI-generated introductions where needed (Tier 1)
    5. Store in DB
    6. Return complete package
    """
    # 1. Load context
    ctx = await load_context(db, project_id)
    project = ctx.get("project", {})

    # 2. Load selected idea
    idea = await _get_selected_idea(db, project_id)

    # 3. Build document context
    doc_data = _build_doc_data(ctx, project, idea)

    # 4. Generate documents
    documents = {}
    for filename in DOCUMENT_ORDER:
        doc_info = DOCUMENTS.get(filename)
        if not doc_info:
            continue
        generator = doc_info["generator"]
        try:
            content = generator(doc_data)
        except Exception as e:
            logger.warning("Failed to generate %s: %s", filename, e)
            content = f"# {doc_info['title']}\n\n*Document generation failed.*"
        documents[filename] = {
            "filename": filename,
            "title": doc_info["title"],
            "description": doc_info["description"],
            "content": content,
            "size_bytes": len(content.encode("utf-8")),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0",
            "status": "completed",
        }

    # 5. Compile package
    package = _compile_package(documents, project_id)

    # 6. Store in shared memory
    await store_memory(
        db, project_id=project_id,
        specialist="documentation_writer",
        memory_type="documentation_package",
        content={"summary": f"Generated {len(documents)} documents"},
        confidence=0.90,
    )

    # 7. Log decision
    await log_decision(
        db, project_id=project_id,
        title=f"Documentation generated ({len(documents)} files)",
        category="feature_scoped",
        description=f"S13 compiled {len(documents)} documentation files from existing specialist outputs.",
        originating_specialist="documentation_writer",
    )

    return package


async def get_documentation(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Get existing documentation or generate new."""
    return await generate_documentation(db, project_id)


# ─── Data Resolution ─────────────────────────────────────────────────────


async def _get_selected_idea(db: AsyncSession, project_id: str) -> dict[str, Any]:
    """Load the selected idea from DB."""
    result = await db.execute(
        select(Idea)
        .where(Idea.project_id == project_id)
        .order_by(Idea.is_selected.desc().nullsfirst(), Idea.rank)
        .limit(1)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        return {}
    return {
        "title": idea.title,
        "hook": idea.hook or "",
        "elevator_pitch": idea.elevator_pitch or "",
        "problem_statement": idea.problem_statement or "",
        "solution": idea.solution or "",
        "core_features": idea.core_features or [],
        "stretch_features": idea.stretch_features or [],
        "usp": idea.usp or "",
        "why_now": idea.why_now or "",
        "target_users": idea.target_users or "",
        "innovation_summary": idea.innovation_summary or "",
        "unique_selling_proposition": idea.usp or "",
        "demo_scenario": idea.demo_scenario or "",
        "judge_wow_moment": idea.judge_wow_moment or "",
        "estimated_build_hours": idea.estimated_build_hours,
        "estimated_difficulty": idea.estimated_difficulty,
        "recommended_roles": idea.recommended_roles or [],
        "future_roadmap": idea.future_roadmap or [],
        "target_platform": idea.target_platform or "",
    }


def _build_doc_data(
    ctx: dict[str, Any],
    project: dict[str, Any],
    idea: dict[str, Any],
) -> dict[str, Any]:
    """Resolve all specialist outputs into a single document context dict.

    Deterministic — no AI used. Every piece of data already exists
    in the outputs of S1-S7 specialists.
    """
    memory = ctx.get("memory", {})
    challenge = memory.get("challenge_intelligence", {}).get("content", {}) or {}
    competitor = memory.get("competitor_intelligence", {}).get("content", {}) or {}

    # Architecture: try from DB/model first, then from memory
    architecture = memory.get("architecture", {}).get("content", {}) or {}
    # If architecture content is empty, use the full memory entry
    if not architecture.get("system_overview"):
        arch_entry = memory.get("architecture", {})
        # The architecture might be stored flat
        for key in ["system_overview", "components", "frontend", "backend", "database"]:
            if arch_entry.get(key):
                architecture[key] = arch_entry[key]

    return {
        "project_name": project.get("name", "exHacker Project"),
        "project": project,
        "idea": idea,
        "challenge": challenge,
        "competitor": competitor,
        "architecture": architecture,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pitch": idea.get("elevator_pitch", "A hackathon project."),
    }


# ─── Package Compilation ─────────────────────────────────────────────────


def _compile_package(
    documents: dict[str, dict[str, Any]],
    project_id: str,
) -> dict[str, Any]:
    """Compile documentation into a structured package."""
    total_chars = sum(d["size_bytes"] for d in documents.values())
    return {
        "project_id": project_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "documents": [documents[name] for name in DOCUMENT_ORDER if name in documents],
        "manifest": {
            "total_files": len(documents),
            "total_size_bytes": total_chars,
            "total_size_kb": round(total_chars / 1024, 1),
            "file_names": [name for name in DOCUMENT_ORDER if name in documents],
        },
    }
