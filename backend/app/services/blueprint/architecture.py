"""Architecture Generator — applies deterministic templates + optional AI enrichment.

SDPD:
  Tier 0: Architecture templates (deterministic) — covers 80% of use cases
  Tier 2: AI enrichment (optional) — customizes components for the specific idea
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from app.ai.gateway import Prompt, ModelTier, gateway
from app.services.blueprint import templates as arch_templates
from app.services.blueprint.tech_stack import recommend_stack

logger = logging.getLogger(__name__)


async def generate_architecture(
    idea: str,
    project_type: Optional[str] = None,
    enrich_with_ai: bool = True,
) -> dict[str, Any]:
    """Generate a complete system architecture.

    Args:
        idea: The project idea.
        project_type: Optional override for project type.
        enrich_with_ai: Whether to use AI for custom enrichment.

    Returns:
        Architecture dict with components, tech stack, and data flow.
    """
    # 1. Get tech stack (deterministic)
    stack = recommend_stack(idea)

    # 2. Get project type from stack
    proj_type = project_type or stack["project_type"]

    # 3. Get architecture template (deterministic)
    components = arch_templates.get_template(proj_type)

    # 4. Optionally enrich with AI
    if enrich_with_ai:
        enriched = await _enrich_architecture(idea, components, proj_type)
        if enriched:
            components = enriched

    return {
        "project_type": proj_type,
        "components": components,
        "tech_stack": stack,
        "notes": _generate_notes(proj_type, components),
    }


async def _enrich_architecture(
    idea: str, components: list[dict[str, Any]], proj_type: str
) -> Optional[list[dict[str, Any]]]:
    """Use AI to customize the architecture template for the specific idea.

    Returns enriched components or None if AI fails (graceful degradation).
    """
    try:
        prompt = Prompt(
            system=(
                "You are a software architect. Given a project idea and a base architecture template, "
                "customize the components for the specific requirements. "
                "You may add, remove, or modify components as needed. "
                "Return ONLY a JSON array of component objects. "
                "Each component has: name, description, responsibilities (list), tech, sub_components (list)."
            ),
            user=(
                f"Project idea: {idea}\n"
                f"Project type: {proj_type}\n"
                f"Base template: {json.dumps(components, indent=2)}\n\n"
                "Customize this architecture for the specific project. "
                "Return ONLY a JSON array of component objects."
            ),
        )

        response = await gateway.generate(prompt, model_tier=ModelTier.TIER_2)
        enriched = _parse_components(response.content)

        if enriched and len(enriched) >= 2:
            logger.info("AI architecture enrichment successful: %d components", len(enriched))
            return enriched

        logger.warning("AI enrichment returned invalid structure, using template")
        return None

    except Exception as e:
        logger.warning("AI architecture enrichment failed: %s. Using template.", e)
        return None


def _parse_components(text: str) -> Optional[list[dict[str, Any]]]:
    """Parse AI response into component list."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3]

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return None

    try:
        components = json.loads(text[start: end + 1])
    except json.JSONDecodeError:
        return None

    if not isinstance(components, list):
        return None

    # Validate each component has required fields
    valid = []
    for c in components:
        if isinstance(c, dict) and c.get("name"):
            valid.append(c)
    return valid if valid else None


def _generate_notes(proj_type: str, components: list[dict[str, Any]]) -> list[str]:
    """Generate architectural notes based on project type and components."""
    notes = []

    if len(components) > 5:
        notes.append(f"The system has {len(components)} components — consider using a monorepo for easier management.")

    if proj_type == "mobile_app":
        notes.append("Mobile apps benefit from offline-first architecture with local caching.")
    elif proj_type == "ai_app":
        notes.append("Streaming AI responses require Server-Sent Events or WebSocket connections.")
    elif proj_type == "web_app":
        notes.append("Consider ISR (Incremental Static Regeneration) for pages with dynamic but cacheable content.")

    notes.append("Each component should have its own isolated testing strategy.")

    return notes
