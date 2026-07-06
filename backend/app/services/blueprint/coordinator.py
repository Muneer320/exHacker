"""Blueprint Coordinator — orchestrates all generators to produce a complete blueprint.

The coordinator:
  1. Generates tech stack (deterministic)
  2. Generates architecture (template + optional AI enrichment)
  3. Generates data model (deterministic from idea keywords)
  4. Generates API contracts (deterministic from data model)
  5. Generates implementation plan (deterministic from architecture)
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from app.services.blueprint import api_contracts, architecture, data_model, plan

# Explicitly reference tech_stack to ensure it's importable
from app.services.blueprint.tech_stack import recommend_stack

logger = logging.getLogger(__name__)


async def generate_blueprint(
    idea: str,
    project_type: Optional[str] = None,
    enrich_architecture: bool = True,
) -> dict[str, Any]:
    """Generate a complete project blueprint.

    All generators run in dependency order.
    Each generator can fail independently — partial results are still returned.

    Args:
        idea: The project description.
        project_type: Optional project type override.
        enrich_architecture: Whether to AI-enrich the architecture.

    Returns:
        Complete blueprint dict with all sections.
    """
    blueprint: dict[str, Any] = {
        "summary": {},
        "tech_stack": None,
        "architecture": None,
        "data_model": None,
        "api_contracts": None,
        "plan": None,
        "generated_at": "",
    }

    from datetime import datetime, timezone
    blueprint["generated_at"] = datetime.now(timezone.utc).isoformat()

    # 1. Tech stack (deterministic, always succeeds)
    try:
        stack = recommend_stack(idea)
        blueprint["tech_stack"] = stack
        logger.info("Tech stack generated: %s", stack.get("project_type"))
    except Exception as e:
        logger.error("Tech stack generation failed: %s", e)

    # 2. Architecture (template + optional AI)
    try:
        arch = await architecture.generate_architecture(
            idea=idea,
            project_type=project_type,
            enrich_with_ai=enrich_architecture,
        )
        blueprint["architecture"] = arch
        logger.info("Architecture generated: %d components", len(arch.get("components", [])))
    except Exception as e:
        logger.error("Architecture generation failed: %s", e)

    # 3. Data model (deterministic)
    try:
        dm = data_model.generate_data_model(idea)
        blueprint["data_model"] = dm
        logger.info("Data model generated: %d entities", len(dm.get("entities", [])))
    except Exception as e:
        logger.error("Data model generation failed: %s", e)

    # 4. API contracts (depends on data model)
    try:
        if blueprint["data_model"]:
            api = api_contracts.generate_api_contracts(blueprint["data_model"])
            blueprint["api_contracts"] = api
            logger.info("API contracts generated: %d endpoints", len(api.get("endpoints", [])))
    except Exception as e:
        logger.error("API contract generation failed: %s", e)

    # 5. Plan (depends on architecture)
    try:
        if blueprint["architecture"]:
            pl = plan.generate_plan(blueprint["architecture"])
            blueprint["plan"] = pl
            logger.info("Plan generated: %d tasks across %d phases",
                        pl.get("total_tasks", 0), len(pl.get("phases", [])))
    except Exception as e:
        logger.error("Plan generation failed: %s", e)

    # Summary
    blueprint["summary"] = _build_summary(blueprint)

    return blueprint


def _build_summary(blueprint: dict[str, Any]) -> dict[str, Any]:
    """Build a summary of the blueprint contents."""
    arch = blueprint.get("architecture")
    dm = blueprint.get("data_model")
    api = blueprint.get("api_contracts")
    pl = blueprint.get("plan")

    return {
        "has_tech_stack": blueprint.get("tech_stack") is not None,
        "components": len(arch.get("components", [])) if arch else 0,
        "entities": len(dm.get("entities", [])) if dm else 0,
        "endpoints": len(api.get("endpoints", [])) if api else 0,
        "tasks": pl.get("total_tasks", 0) if pl else 0,
        "estimated_hours": pl.get("estimated_hours", 0) if pl else 0,
    }
