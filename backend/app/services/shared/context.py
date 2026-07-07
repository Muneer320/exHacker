"""Shared Context API — automatic context provisioning for all specialists (Bible §7).

Every specialist receives:
  - Current project details
  - Latest shared memory entries
  - Recent decisions
  - Confidence history

No manual wiring. No duplicated serialization.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.shared import SharedMemory, DecisionJournal
from app.services.shared.memory import (
    get_all_memory, get_latest_memory, get_decisions,
)
from app.services.project import get_project as get_project_service


async def load_context(
    db: AsyncSession,
    project_id: str,
    *,
    required_memory: Optional[list[str]] = None,
    include_decisions: bool = True,
    include_project: bool = True,
) -> dict[str, Any]:
    """Load complete shared context for a specialist (Bible §7.3).

    Args:
        db: Database session.
        project_id: Project to load context for.
        required_memory: Specific memory types the specialist needs.
                         If None, loads all available memory.
        include_decisions: Whether to include recent decisions.
        include_project: Whether to include project details.

    Returns:
        Structured context dict that can be directly passed into any specialist.
    """
    context: dict[str, Any] = {"project_id": project_id}

    # 1. Project basics
    if include_project:
        try:
            project = await get_project_service(db, project_id)
            context["project"] = {
                "id": project.id,
                "name": getattr(project, "name", ""),
                "idea": getattr(project, "idea", ""),
                "challenge_statement": getattr(project, "challenge_statement", ""),
                "theme": getattr(project, "theme", ""),
                "available_hours": getattr(project, "available_hours", ""),
                "team_size": getattr(project, "team_size", "4"),
                "skills": getattr(project, "skills", ""),
                "target_platform": getattr(project, "target_platform", ""),
            }
        except Exception:
            context["project"] = {}

    # 2. Shared memory — either specific types or all
    if required_memory:
        memory = {}
        for mem_type in required_memory:
            entry = await get_latest_memory(db, project_id, mem_type)
            if entry:
                memory[mem_type] = entry
        context["memory"] = memory
    else:
        memory_list = await get_all_memory(db, project_id)
        context["memory_list"] = memory_list
        # Also build a latest-by-type map for easy access
        memory_map = {}
        for entry in memory_list:
            mt = entry.get("memory_type")
            if mt and mt not in memory_map:
                memory_map[mt] = entry
        context["memory"] = memory_map

    # 3. Recent decisions
    if include_decisions:
        context["decisions"] = await get_decisions(db, project_id, limit=20)

    return context


def format_context_for_prompt(context: dict[str, Any]) -> str:
    """Format shared context into a string suitable for prompt injection.

    Keeps the output compact — avoids serializing huge JSON blobs.
    Specialists should load only what they need via load_context() first,
    then use this helper to format specific sections for prompt rendering.
    """
    parts = []

    # Project summary
    project = context.get("project", {})
    if project:
        parts.append(f"Project: {project.get('name', 'Unnamed')}")
        parts.append(f"Idea: {project.get('idea', '')[:200]}")
        if project.get("challenge_statement"):
            parts.append(f"Challenge: {project['challenge_statement'][:300]}")
        if project.get("theme"):
            parts.append(f"Theme: {project['theme']}")
        skills = project.get("skills", "")
        if skills:
            parts.append(f"Team Skills: {skills}")
        parts.append("")

    # Memory summaries
    memory = context.get("memory", {})
    for mem_type, entry in memory.items():
        content = entry.get("content", {}) or {}
        summary = (
            content.get("summary")
            or content.get("executive_summary")
            or content.get("landscape_summary")
            or ""
        )
        confidence = entry.get("confidence", "")
        parts.append(f"[{mem_type}] (confidence: {confidence})")
        if summary:
            parts.append(f"  {str(summary)[:200]}")
        parts.append("")

    # Recent decisions
    decisions = context.get("decisions", [])
    if decisions:
        parts.append(f"Recent Decisions ({len(decisions)}):")
        for d in decisions[:5]:
            parts.append(f"  #{d.get('entry_number', '?')} {d.get('title', '')} [{d.get('category', '')}]")
        parts.append("")

    return "\n".join(parts)
