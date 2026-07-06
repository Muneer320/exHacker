"""Direction Generator — uses AI Gateway Tier 2 to generate product directions.
# pyright: reportAttributeAccessIssue=false, reportArgumentType=false, reportGeneralTypeIssues=false
# SQLAlchemy Column descriptors resolve at runtime; Pyright false positives.

Pipeline:
  1. Load research data for the project
  2. Summarize competitors, APIs, and OSS projects
  3. Generate directions via AI Gateway (Tier 2 — glm-5.2)
  4. Parse, validate, and store in database
  5. Return structured directions

SDPD: Direction generation uses AI (Tier 2 — medium model for reasoning).
      Everything else (parsing, storage) is deterministic.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gateway import Prompt, ModelTier, gateway
from app.ai.prompts import prompt_manager
from app.core.exceptions import BlueprintGenerationError
from app.models.direction import Direction
from app.models.project import ProjectStatus
from app.services.project import get_project, transition_state
from app.services.research import get_research

logger = logging.getLogger(__name__)


async def generate_directions(
    db: AsyncSession,
    project_id: str,
) -> list[dict[str, Any]]:
    """Generate product directions from research data.

    Args:
        db: Database session.
        project_id: The project to generate directions for.

    Returns:
        List of direction dicts with title, tagline, description, scores.
    """
    # 1. Check for existing directions
    existing = await get_directions(db, project_id)
    if existing:
        logger.info("Using existing directions for project %s (%d found)", project_id, len(existing))
        return existing

    # 2. Load project and research data
    project = await get_project(db, project_id)

    # Auto-transition DRAFT → PROCESSING
    if project.status == ProjectStatus.DRAFT.value:
        await transition_state(db, project_id, ProjectStatus.PROCESSING)
        await db.refresh(project)
    research = await get_research(db, project_id)

    # 3. Build research summaries
    competitor_summary = _summarize_results(research.get("competitors", []), "competitor")
    api_summary = _summarize_results(research.get("apis", []), "API")
    oss_summary = _summarize_results(research.get("oss_projects", []), "open-source project")

    # 4. Generate directions via AI Gateway
    try:
        system, user = prompt_manager.render(
            "directions",
            idea=project.idea,
            competitor_summary=competitor_summary or "None found",
            api_summary=api_summary or "None found",
            oss_summary=oss_summary or "None found",
            num_directions=3,
        )
    except FileNotFoundError:
        # Fallback: use inline prompt if prompt file isn't loaded
        system = (
            "You are a product strategist. Generate 3 distinct product directions "
            "based on the user's idea and research. "
            "Return ONLY a JSON array of objects with title, tagline, description, innovation_score, feasibility_score."
        )
        user = (
            f"Idea: {project.idea}\n"
            f"Competitors: {competitor_summary or 'None'}\n"
            f"APIs: {api_summary or 'None'}\n"
            f"OSS: {oss_summary or 'None'}\n"
            f"Generate 3 product directions as a JSON array."
        )

    response = await gateway.generate(
        Prompt(system=system, user=user),
        model_tier=ModelTier.TIER_2,
    )

    # 5. Parse the response
    raw_directions = _parse_directions(response.content)
    if not raw_directions:
        logger.warning("Failed to parse directions from AI response for project %s", project_id)
        # Return fallback directions
        raw_directions = _fallback_directions(project.idea)

    # 6. Store in database
    stored = []
    for raw in raw_directions:
        direction = Direction(
            project_id=project_id,
            title=raw.get("title", "Untitled Direction"),
            tagline=raw.get("tagline", ""),
            description=raw.get("description", ""),
            innovation_score=raw.get("innovation_score"),
            feasibility_score=raw.get("feasibility_score"),
        )
        db.add(direction)
        stored.append(direction)

    await db.commit()

    # Refresh to get IDs
    for d in stored:
        await db.refresh(d)

    return [_direction_to_dict(d) for d in stored]


async def get_directions(
    db: AsyncSession,
    project_id: str,
) -> list[dict[str, Any]]:
    """Get stored directions for a project."""
    result = await db.execute(
        select(Direction)
        .where(Direction.project_id == project_id)
        .order_by(Direction.created_at.asc())
    )
    directions = list(result.scalars().all())
    return [_direction_to_dict(d) for d in directions]


async def select_direction(
    db: AsyncSession,
    project_id: str,
    direction_id: str,
) -> dict[str, Any]:
    """Select a direction for a project. Unselects any previously selected.

    Returns the selected direction.
    """
    # Unselect all directions for this project
    await db.execute(
        update(Direction)
        .where(Direction.project_id == project_id)
        .values(is_selected=False)
    )

    # Select the target direction
    result = await db.execute(
        select(Direction).where(
            Direction.id == direction_id,
            Direction.project_id == project_id,
        )
    )
    direction = result.scalar_one_or_none()
    if not direction:
        from app.core.exceptions import ProjectNotFoundError
        raise ProjectNotFoundError(
            message="Direction not found.",
            detail={"direction_id": direction_id, "project_id": project_id},
        )

    direction.is_selected = True
    await db.commit()
    await db.refresh(direction)

    # Update project status: PROCESSING → READY
    from app.services.project import transition_state
    await transition_state(db, project_id, ProjectStatus.READY)

    return _direction_to_dict(direction)


# ─── Helpers ────────────────────────────────────────────────────────────────


def _summarize_results(results: list[dict[str, Any]], label: str) -> str:
    """Create a brief text summary from a list of research results."""
    if not results:
        return ""
    names = [r.get("title", "") for r in results[:5] if r.get("title")]
    if not names:
        return ""
    summary = f"{len(names)} {label}(s) found: " + "; ".join(names[:3])
    if len(names) > 3:
        summary += f" (+{len(names) - 3} more)"
    return summary


def _parse_directions(text: str) -> list[dict[str, Any]]:
    """Parse the AI response into a list of direction dicts."""
    text = text.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3]

    # Try to find JSON array
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        logger.warning("No JSON array found in AI response")
        return []

    text = text[start:end + 1]

    try:
        directions = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON from AI response")
        return []

    if not isinstance(directions, list):
        return []

    # Validate each direction
    valid = []
    for d in directions:
        if isinstance(d, dict) and d.get("title"):
            valid.append(d)
    return valid


def _fallback_directions(idea: str) -> list[dict[str, Any]]:
    """Return fallback directions when AI generation fails."""
    return [
        {
            "title": f"{idea[:40]} — Core",
            "tagline": f"Build the essential version of {idea[:30]}",
            "description": f"A focused implementation of {idea[:60]}, prioritizing the core features that deliver immediate value.",
            "innovation_score": 70,
            "feasibility_score": 85,
        },
        {
            "title": f"{idea[:40]} — AI-First",
            "tagline": f"Add intelligent features to {idea[:30]}",
            "description": f"Leverage AI to provide personalized recommendations, automation, and smart insights on top of the core {idea[:40]} concept.",
            "innovation_score": 85,
            "feasibility_score": 65,
        },
        {
            "title": f"{idea[:40]} — Platform",
            "tagline": f"Build a platform around {idea[:30]}",
            "description": f"Create an extensible platform that allows third-party integrations, community contributions, and customization on top of {idea[:40]}.",
            "innovation_score": 80,
            "feasibility_score": 55,
        },
    ]


def _direction_to_dict(d: Direction) -> dict[str, Any]:
    """Convert a Direction model to a dict for API responses."""
    return {
        "id": d.id,
        "project_id": d.project_id,
        "title": d.title,
        "tagline": d.tagline,
        "description": d.description,
        "innovation_score": d.innovation_score,
        "feasibility_score": d.feasibility_score,
        "is_selected": d.is_selected,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }
