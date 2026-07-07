"""Solution Architect (S7) — produces complete technical blueprints (Bible §6.2 S7).

This specialist transforms a selected idea into a complete, actionable architecture.
Every downstream engineering specialist depends on this output.

Deterministic-first approach:
  - Architecture templates for common project types
  - Deterministic API contract generation from data model templates
  - Deterministic Mermaid diagram generation from component lists
  - AI (Tier 2) only for genuine architectural reasoning and trade-off analysis
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gateway import Prompt, ModelTier, gateway
from app.ai.prompts import prompt_manager
from app.models.architecture import ArchitectureBlueprint
from app.models.idea import Idea
from app.services.shared.memory import store_memory, log_decision
from app.services.shared.context import load_context
from app.services.project import get_project

logger = logging.getLogger(__name__)


async def generate_architecture(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Run the complete Architecture generation pipeline (S7).

    1. Find selected idea (or first idea)
    2. Load shared context (project, team, challenge, research)
    3. Build template from project type
    4. Generate AI reasoning (Tier 2)
    5. Assemble complete blueprint
    6. Store in DB + shared memory + journal
    """
    # 1. Check cache
    existing = await _get_existing(db, project_id)
    if existing:
        return existing

    # 2. Load selected idea
    selected_idea = await _get_selected_idea(db, project_id)
    if not selected_idea:
        logger.warning("No selected idea for project %s, using project context", project_id)
        selected_idea = {}

    # 3. Load context
    ctx = await load_context(db, project_id)
    project = ctx.get("project", {})

    # 4. Build prompt context
    context = _build_context(project, selected_idea, ctx)

    # 5. Generate AI reasoning (Tier 2)
    ai_output = await _generate_reasoning(context)

    # 6. Assemble complete blueprint
    blueprint = _assemble_blueprint(project, selected_idea, ai_output, context)

    # 7. Store in DB
    stored = await _store_blueprint(db, project_id, blueprint)

    # 8. Log decision
    await log_decision(
        db, project_id=project_id,
        title="Architecture designed",
        category="architecture_tradeoff",
        description=f"Complete technical architecture generated for {selected_idea.get('title', 'the project')}.",
        originating_specialist="solution_architect",
    )

    # 9. Store in shared memory
    await store_memory(
        db, project_id=project_id,
        specialist="solution_architect",
        memory_type="architecture",
        content={"summary": f"Architecture for {selected_idea.get('title', '')}"},
        confidence=0.85,
    )

    return stored


async def get_architecture(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Get existing architecture without regenerating."""
    result = await db.execute(
        select(ArchitectureBlueprint).where(ArchitectureBlueprint.project_id == project_id)
    )
    bp = result.scalar_one_or_none()
    if bp:
        return _to_response(bp)
    return _empty_response()


# ─── Data Loading ────────────────────────────────────────────────────────


async def _get_selected_idea(db: AsyncSession, project_id: str) -> Optional[dict[str, Any]]:
    """Find the selected idea, or the first idea if none selected."""
    result = await db.execute(
        select(Idea)
        .where(Idea.project_id == project_id)
        .order_by(Idea.is_selected.desc().nullsfirst(), Idea.rank)
        .limit(1)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        return None
    return {
        "title": idea.title,
        "hook": idea.hook or "",
        "elevator_pitch": idea.elevator_pitch or "",
        "problem_statement": idea.problem_statement or "",
        "solution": idea.solution or "",
        "core_features": idea.core_features or [],
        "target_users": idea.target_users or "",
        "target_platform": idea.target_platform or "",
    }


def _build_context(
    project: dict[str, Any],
    idea: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, str]:
    """Build flat context dict for prompt rendering."""
    competitor = ctx.get("memory", {}).get("competitor_intelligence", {}).get("content", {}) or {}
    challenge = ctx.get("memory", {}).get("challenge_intelligence", {}).get("content", {}) or {}

    return {
        "idea_title": idea.get("title", project.get("idea", ""))[:200],
        "idea_hook": (idea.get("hook") or "")[:200],
        "elevator_pitch": (idea.get("elevator_pitch") or "")[:500],
        "problem_statement": (idea.get("problem_statement") or project.get("idea", ""))[:500],
        "solution": (idea.get("solution") or "")[:500],
        "core_features": ", ".join((idea.get("core_features") or [])[:6]),
        "target_users": (idea.get("target_users") or "")[:200],
        "target_platform": idea.get("target_platform", project.get("target_platform", "web")),
        "available_hours": project.get("available_hours", "48"),
        "team_size": project.get("team_size", "4"),
        "skills": project.get("skills", "general"),
        "team_experience": project.get("team_experience", "intermediate"),
        "preferred_languages": project.get("preferred_languages", ""),
        "preferred_frameworks": project.get("preferred_frameworks", ""),
        "excluded_technologies": project.get("excluded_technologies", ""),
        "challenge_statement": project.get("challenge_statement", project.get("idea", ""))[:300],
        "theme": project.get("theme", ""),
        "key_opportunities": ", ".join(
            [io.get("area", "") for io in (challenge.get("innovation_opportunities") or [])[:3]]
        ) if isinstance(challenge, dict) else "",
        "tech_recommendations": ", ".join(
            [t.get("technology", "") for t in (competitor.get("technology_recommendations") or [])[:3]]
        ) if isinstance(competitor, dict) else "",
        "to_avoid": ", ".join(
            (competitor.get("gap_analysis", {}).get("to_avoid") or [])[:3]
        ) if isinstance(competitor, dict) else "",
    }


# ─── AI Generation (Tier 2) ─────────────────────────────────────────────


async def _generate_reasoning(context: dict[str, str]) -> Optional[dict[str, Any]]:
    """Generate architecture reasoning via AI Gateway (Tier 2).

    AI handles: system overview, rationale, trade-offs, architecture review.
    Everything else (templates, diagrams, API contracts) is deterministic.
    """
    try:
        system, user = prompt_manager.render("solution_architect", **context)
    except FileNotFoundError:
        system = "You are a Staff Engineer. Generate a complete technical architecture for this project."
        user = f"Idea: {context.get('idea_title', '')}\nFeatures: {context.get('core_features', '')}\nTeam: {context.get('team_size', '4')} people, {context.get('available_hours', '48')} hours"

    response = await gateway.generate(
        Prompt(system=system, user=user),
        model_tier=ModelTier.TIER_2,
    )
    return _parse_architecture(response.content)


def _parse_architecture(text: str) -> Optional[dict[str, Any]]:
    """Parse AI response into structured dict."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3]
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


# ─── Blueprint Assembly ──────────────────────────────────────────────────


def _assemble_blueprint(
    project: dict[str, Any],
    idea: dict[str, Any],
    ai_output: Optional[dict[str, Any]],
    context: dict[str, str],
) -> dict[str, Any]:
    """Assemble the complete architecture blueprint from AI + templates."""
    if not ai_output:
        # Use fallback template
        return _fallback_blueprint(project, idea)

    # Fill in any gaps with fallback data
    template = _fallback_blueprint(project, idea)

    return {
        "system_overview": ai_output.get("system_overview", template["system_overview"]),
        "architecture_rationale": ai_output.get("architecture_rationale", template["architecture_rationale"]),
        "components": ai_output.get("components", template["components"]),
        "mermaid_system": ai_output.get("mermaid_system", template["mermaid_system"]),
        "mermaid_request_flow": ai_output.get("mermaid_request_flow", template["mermaid_request_flow"]),
        "mermaid_data_flow": ai_output.get("mermaid_data_flow", template["mermaid_data_flow"]),
        "mermaid_deployment": ai_output.get("mermaid_deployment", template["mermaid_deployment"]),
        "frontend": ai_output.get("frontend", template["frontend"]),
        "backend": ai_output.get("backend", template["backend"]),
        "database": ai_output.get("database", template["database"]),
        "api_contracts": ai_output.get("api_contracts", template["api_contracts"]),
        "authentication": ai_output.get("authentication", template["authentication"]),
        "external_services": ai_output.get("external_services", template["external_services"]),
        "scalability": ai_output.get("scalability", template["scalability"]),
        "tradeoffs": ai_output.get("tradeoffs", template["tradeoffs"]),
        "review": ai_output.get("review", template["review"]),
    }


# ─── Fallback ────────────────────────────────────────────────────────────


def _fallback_blueprint(project: dict[str, Any], idea: dict[str, Any]) -> dict[str, Any]:
    """Return fallback architecture when AI is unavailable.

    Uses deterministic templates based on project type.
    """
    platform = idea.get("target_platform", project.get("target_platform", "web"))
    title = idea.get("title", project.get("idea", "the project"))[:40]

    if platform == "mobile":
        return _mobile_template(title)
    return _web_template(title)


def _web_template(title: str) -> dict[str, Any]:
    return {
        "system_overview": f"Architecture for {title}. Next.js frontend serving a FastAPI backend with PostgreSQL.",
        "architecture_rationale": "Three-tier architecture chosen for clear separation of concerns. Next.js for fast frontend development. FastAPI for type-safe APIs.",
        "components": [
            {"name": "Frontend Web App", "description": "Next.js with App Router", "tech": "Next.js 16, React 19, TypeScript", "purpose": "User interface"},
            {"name": "Backend API", "description": "REST API server", "tech": "FastAPI, Python 3.11+, SQLAlchemy", "purpose": "Business logic and data"},
            {"name": "PostgreSQL Database", "description": "Primary data store", "tech": "PostgreSQL 16", "purpose": "Persistent storage"},
        ],
        "mermaid_system": "graph TD\n  A[User Browser] --> B[Next.js Frontend]\n  B --> C[FastAPI Backend]\n  C --> D[PostgreSQL DB]\n  C --> E[AI Gateway]\n  C --> F[External APIs]",
        "mermaid_request_flow": "sequenceDiagram\n  User->>Frontend: Interact\n  Frontend->>API: HTTP Request\n  API->>DB: Query\n  API->>AI: Generate\n  API-->>Frontend: JSON Response\n  Frontend-->>User: Update UI",
        "mermaid_data_flow": "flowchart LR\n  UI[User Input] --> FE[Next.js]\n  FE --> BE[FastAPI]\n  BE --> DB[(PostgreSQL)]\n  BE --> AI[AI Gateway]\n  BE --> EXT[External APIs]",
        "mermaid_deployment": "flowchart LR\n  FE[Next.js] --> Vercel\n  BE[FastAPI] --> Vercel Serverless\n  DB[(PostgreSQL)] --> Supabase\n  AI[AI Gateway] --> Cloud Provider",
        "frontend": {"framework": "Next.js 16 (App Router)", "folder_structure": ["app/", "components/", "lib/", "hooks/", "types/"], "component_hierarchy": ["Layout", "Page", "FeatureCard", "UIComponent"], "state_management": "React Context + Server Components", "routing": [{"path": "/", "component": "Landing", "auth": False}, {"path": "/dashboard", "component": "Dashboard", "auth": True}]},
        "backend": {"framework": "FastAPI + SQLAlchemy async", "modules": ["api/", "services/", "models/", "core/"], "api_organization": [{"prefix": "/api/v1", "module": "Main router", "description": "All endpoints"}]},
        "database": {"entities": [{"name": "User", "fields": [{"name": "id", "type": "UUID", "pk": True}, {"name": "created_at", "type": "timestamp"}]}, {"name": "Project", "fields": [{"name": "id", "type": "UUID"}, {"name": "user_id", "type": "UUID (FK)"}, {"name": "data", "type": "JSON"}]}], "relationships": [{"from": "Project", "to": "User", "type": "many_to_one"}], "mermaid_er": "erDiagram\n  User ||--o{ Project : owns", "notes": "SQLite for dev, PostgreSQL for prod. Add indexes on FKs."},
        "api_contracts": [
            {"method": "GET", "path": "/api/v1/projects", "description": "List projects", "request": {}, "response": {"projects": []}, "auth": False, "errors": []},
            {"method": "POST", "path": "/api/v1/projects", "description": "Create project", "request": {"body": {"title": "string"}}, "response": {"project": {}}, "auth": False, "errors": ["400: Validation"]},
            {"method": "GET", "path": "/api/v1/projects/{id}", "description": "Get project", "request": {}, "response": {"project": {}}, "auth": False, "errors": ["404: Not found"]},
        ],
        "authentication": {"provider": "NextAuth.js / Supabase Auth", "model": "JWT sessions. No auth for V1 demo.", "permissions": ["Owner: full access"]},
        "external_services": [{"name": "AI Provider", "purpose": "LLM inference", "rate_limit": "Varies", "fallback": "Mock mode", "alternative": "Multiple providers"}],
        "scalability": {"hackathon_version": "Monolith with clear module boundaries", "production_version": "Separate frontend/backend, Redis cache, background workers", "migration_path": "Extract services only when needed"},
        "tradeoffs": [{"decision": "FastAPI over Express.js", "rationale": "Python preferred, async support, Pydantic", "alternatives": ["Express.js", "Flask"], "pros": ["Type safety", "Auto docs"], "cons": ["Smaller web ecosystem"], "hackathon_justification": "Fast development with Pydantic", "production_justification": "Good performance"}],
        "review": {"weak_points": ["No caching layer", "Single DB"], "failure_modes": ["Database outage takes everything down"], "technical_debt": ["No tests for edge cases"], "future_improvements": ["Add Redis caching", "Implement circuit breaker"]},
    }


def _mobile_template(title: str) -> dict[str, Any]:
    t = _web_template(title)
    t["components"] = [
        {"name": "Mobile App", "description": "Cross-platform mobile app", "tech": "React Native / Expo", "purpose": "User interface"},
        {"name": "Backend API", "description": "REST API server", "tech": "FastAPI, Python", "purpose": "Business logic"},
        {"name": "PostgreSQL Database", "description": "Primary data store", "tech": "PostgreSQL 16", "purpose": "Persistent storage"},
    ]
    t["frontend"]["framework"] = "React Native with Expo"
    t["mermaid_system"] = "graph TD\n  A[Mobile App] --> B[FastAPI Backend]\n  B --> C[PostgreSQL]\n  B --> D[AI Gateway]"
    return t


# ─── Database ────────────────────────────────────────────────────────────


async def _get_existing(db: AsyncSession, project_id: str) -> Optional[dict[str, Any]]:
    result = await db.execute(
        select(ArchitectureBlueprint).where(ArchitectureBlueprint.project_id == project_id)
    )
    bp = result.scalar_one_or_none()
    if bp:
        return _to_response(bp)
    return None


async def _store_blueprint(db: AsyncSession, project_id: str, blueprint: dict[str, Any]) -> dict[str, Any]:
    result = await db.execute(
        select(ArchitectureBlueprint).where(ArchitectureBlueprint.project_id == project_id)
    )
    existing = result.scalar_one_or_none()

    data = {
        "system_overview": blueprint.get("system_overview"),
        "architecture_rationale": blueprint.get("architecture_rationale"),
        "components": blueprint.get("components", []),
        "mermaid_system": blueprint.get("mermaid_system"),
        "mermaid_request_flow": blueprint.get("mermaid_request_flow"),
        "mermaid_data_flow": blueprint.get("mermaid_data_flow"),
        "mermaid_deployment": blueprint.get("mermaid_deployment"),
        "frontend_framework": blueprint.get("frontend", {}).get("framework"),
        "frontend_folders": blueprint.get("frontend", {}).get("folder_structure", []),
        "frontend_component_hierarchy": blueprint.get("frontend", {}).get("component_hierarchy", []),
        "frontend_state": blueprint.get("frontend", {}).get("state_management"),
        "frontend_routing": blueprint.get("frontend", {}).get("routing", []),
        "backend_framework": blueprint.get("backend", {}).get("framework"),
        "backend_modules": blueprint.get("backend", {}).get("modules", []),
        "backend_api_organization": blueprint.get("backend", {}).get("api_organization", []),
        "database_entities": blueprint.get("database", {}).get("entities", []),
        "database_relationships": blueprint.get("database", {}).get("relationships", []),
        "mermaid_er": blueprint.get("database", {}).get("mermaid_er"),
        "database_notes": blueprint.get("database", {}).get("notes"),
        "api_contracts": blueprint.get("api_contracts", []),
        "auth_provider": blueprint.get("authentication", {}).get("provider"),
        "auth_model": blueprint.get("authentication", {}).get("model"),
        "external_services": blueprint.get("external_services", []),
        "hackathon_version": blueprint.get("scalability", {}).get("hackathon_version"),
        "production_version": blueprint.get("scalability", {}).get("production_version"),
        "migration_path": blueprint.get("scalability", {}).get("migration_path"),
        "tradeoffs": blueprint.get("tradeoffs", []),
        "weak_points": blueprint.get("review", {}).get("weak_points", []),
        "failure_modes": blueprint.get("review", {}).get("failure_modes", []),
    }

    if existing:
        for key, value in data.items():
            if value is not None and hasattr(existing, key):
                setattr(existing, key, value)
        await db.commit()
        await db.refresh(existing)
        return _to_response(existing)

    bp = ArchitectureBlueprint(project_id=project_id, **data)
    db.add(bp)
    await db.commit()
    await db.refresh(bp)
    return _to_response(bp)


# ─── Response ────────────────────────────────────────────────────────────


def _to_response(bp: ArchitectureBlueprint) -> dict[str, Any]:
    return {
        "id": bp.id,
        "project_id": bp.project_id,
        "system_overview": bp.system_overview or "",
        "architecture_rationale": bp.architecture_rationale or "",
        "components": bp.components or [],
        "mermaid_system": bp.mermaid_system or "",
        "mermaid_request_flow": bp.mermaid_request_flow or "",
        "mermaid_data_flow": bp.mermaid_data_flow or "",
        "mermaid_deployment": bp.mermaid_deployment or "",
        "frontend": {
            "framework": bp.frontend_framework or "",
            "folder_structure": bp.frontend_folders or [],
            "component_hierarchy": bp.frontend_component_hierarchy or [],
            "state_management": bp.frontend_state or "",
            "routing": bp.frontend_routing or [],
        },
        "backend": {
            "framework": bp.backend_framework or "",
            "modules": bp.backend_modules or [],
            "api_organization": bp.backend_api_organization or [],
        },
        "database": {
            "entities": bp.database_entities or [],
            "relationships": bp.database_relationships or [],
            "mermaid_er": bp.mermaid_er or "",
            "notes": bp.database_notes or "",
        },
        "api_contracts": bp.api_contracts or [],
        "authentication": {
            "provider": bp.auth_provider or "",
            "model": bp.auth_model or "",
        },
        "external_services": bp.external_services or [],
        "scalability": {
            "hackathon_version": bp.hackathon_version or "",
            "production_version": bp.production_version or "",
            "migration_path": bp.migration_path or "",
        },
        "tradeoffs": bp.tradeoffs or [],
        "review": {
            "weak_points": bp.weak_points or [],
            "failure_modes": bp.failure_modes or [],
        },
    }


def _empty_response() -> dict[str, Any]:
    return {
        "system_overview": "", "architecture_rationale": "",
        "components": [], "mermaid_system": "", "mermaid_request_flow": "",
        "mermaid_data_flow": "", "mermaid_deployment": "",
        "frontend": {"framework": "", "folder_structure": [], "component_hierarchy": [], "state_management": "", "routing": []},
        "backend": {"framework": "", "modules": [], "api_organization": []},
        "database": {"entities": [], "relationships": [], "mermaid_er": "", "notes": ""},
        "api_contracts": [], "authentication": {"provider": "", "model": ""},
        "external_services": [], "scalability": {"hackathon_version": "", "production_version": "", "migration_path": ""},
        "tradeoffs": [], "review": {"weak_points": [], "failure_modes": []},
    }
