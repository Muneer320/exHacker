"""Challenge Analyst (S1) — produces structured intelligence reports from challenge data.

Bible §6.2 S1:
  Purpose: Understand the hackathon challenge deeply.
  Model: Tier 2 (reasoning — glm-5.2).
  Inputs: Challenge statement, theme, evaluation criteria, team details.
  Outputs: Structured challenge understanding with themes, constraints,
           hidden opportunities, judging priorities.
  Limits: Must NOT propose solutions. Analysis only.
  Success: Correctly identifies 3+ constraints and 2+ hidden opportunities.
  Failure: Returns a generic analysis. Fallback: template-based extraction.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gateway import Prompt, ModelTier, gateway
from app.ai.prompts import prompt_manager
from app.core.config import settings
from app.models.project import ProjectModel
from app.models.challenge import ChallengeIntelligence
from app.services.project import get_project

logger = logging.getLogger(__name__)


async def analyze_challenge(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Run the Challenge Intelligence pipeline for a project.

    Args:
        db: Database session.
        project_id: The project to analyze.

    Returns:
        Structured Challenge Intelligence report dict.
    """
    # 1. Check for existing analysis
    existing = await _get_existing(db, project_id)
    if existing and existing.get("confidence", 0) >= 0.5:
        logger.info("Using existing challenge analysis for project %s", project_id)
        return existing

    # 2. Load project data
    project = await get_project(db, project_id)

    # 3. Build context from project fields
    context = _build_context(project)

    # 4. Generate analysis via AI Gateway (Tier 2 — reasoning model)
    analysis = await _generate_analysis(context)

    # 5. Store in database
    stored = await _store_analysis(db, project_id, analysis)

    return _to_response(stored)


async def get_analysis(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Get existing challenge analysis without regenerating."""
    existing = await _get_existing(db, project_id)
    if existing:
        return existing
    return _empty_response()


async def refresh_analysis(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Force-refresh challenge analysis."""
    await _clear_existing(db, project_id)
    return await analyze_challenge(db, project_id)


# ─── AI Generation (Tier 2 — highest reasoning quality) ────────────────


async def _generate_analysis(context: dict[str, str]) -> dict[str, Any]:
    """Generate challenge intelligence via AI Gateway.

    Uses Tier 2 (glm-5.2) — the strongest reasoning model available.
    This is justified because the quality ceiling of the entire project
    is determined by how well S1 understands the challenge (SDPD §C1).
    """
    try:
        # Try loading from prompt file first
        system, user = prompt_manager.render(
            "challenge_analyst",
            **context,
        )
    except FileNotFoundError:
        # Fallback: inline prompt
        system = (
            "You are a senior hackathon mentor and product strategist. "
            "Analyze the following challenge and produce a structured JSON report. "
            "Return ONLY a JSON object. No markdown. No explanation."
        )
        user = f"Challenge: {context.get('challenge_statement', '')}\nTheme: {context.get('theme', '')}\nTeam: {context.get('team_size', '')} people, {context.get('available_time', '')} hours\nSkills: {context.get('skills', '')}\n\nProduce a complete Challenge Intelligence Report."

    prompt = Prompt(system=system, user=user)
    response = await gateway.generate(prompt, model_tier=ModelTier.TIER_2)

    # Parse the response
    analysis = _parse_analysis(response.content)
    if analysis:
        analysis["model_used"] = response.model_used
        analysis["confidence"] = _calculate_confidence(analysis)
    else:
        logger.warning("Failed to parse challenge analysis, using fallback")
        analysis = _fallback_analysis(context)

    return analysis


def _parse_analysis(text: str) -> Optional[dict[str, Any]]:
    """Parse AI response into structured dict."""
    text = text.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3]

    # Try to find JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None

    text = text[start:end + 1]

    try:
        analysis = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(analysis, dict):
        return None

    return analysis


def _calculate_confidence(analysis: dict[str, Any]) -> float:
    """Calculate confidence score based on completeness of analysis."""
    required_fields = [
        "executive_summary", "core_problem", "constraints",
        "success_criteria", "risk_areas", "recommended_strategy",
    ]
    present = sum(1 for f in required_fields if analysis.get(f))
    return round(present / len(required_fields), 2)


def _fallback_analysis(context: dict[str, str]) -> dict[str, Any]:
    """Return fallback analysis when AI fails."""
    statement = context.get("challenge_statement", "this challenge")
    return {
        "executive_summary": f"A challenge about {statement[:80]}.",
        "core_problem": {
            "problem": str(statement)[:200],
            "who_experiences": "Users of the system",
            "why_important": "This challenge addresses a specific need in the hackathon context.",
        },
        "hidden_problems": ["Complexity underestimated", "Integration challenges"],
        "stakeholders": [
            {"role": "Primary users", "description": "End users of the solution"},
            {"role": "Judges", "description": "Evaluating the project"},
        ],
        "constraints": [
            {"type": "time", "description": f"Limited to {context.get('available_time', '24-48')} hours"},
            {"type": "team", "description": f"Team of {context.get('team_size', '4')} people"},
        ],
        "success_criteria": [
            {"criterion": "Problem fit", "weight": 30, "description": "How well the solution matches the challenge"},
            {"criterion": "Technical quality", "weight": 25, "description": "Quality and completeness of implementation"},
            {"criterion": "Innovation", "weight": 20, "description": "Novelty of the approach"},
            {"criterion": "Presentation", "weight": 15, "description": "Demo and pitch quality"},
            {"criterion": "Feasibility", "weight": 10, "description": "Can be completed in time"},
        ],
        "opportunity_areas": ["Core feature improvements", "Integration opportunities"],
        "innovation_opportunities": [
            {"area": "UX innovation", "description": "Unique user experience that stands out"},
        ],
        "risk_areas": [
            {"area": "Scope", "severity": "high", "description": "Overbuilding is the most common mistake"},
        ],
        "difficulty": {
            "technical": 60,
            "research": 40,
            "demo": 50,
            "judge": 55,
            "overall": 50,
        },
        "recommended_strategy": (
            f"With a team of {context.get('team_size', '4')} and "
            f"{context.get('available_time', '24-48')} hours, focus on a "
            "working prototype over a polished but incomplete product. "
            "Prioritize the demo experience — it matters as much as the code."
        ),
        "themes": ["hackathon"],
        "keywords": [str(statement)[:30]],
        "confidence": 0.4,
    }


# ─── Context Building ─────────────────────────────────────────────────


def _build_context(project: ProjectModel) -> dict[str, str]:
    """Build a context dict from project fields for prompt rendering."""
    return {
        "challenge_statement": getattr(project, "challenge_statement", "") or getattr(project, "idea", ""),
        "theme": getattr(project, "theme", "") or "",
        "organizer": getattr(project, "organizer", "") or "",
        "evaluation_criteria": getattr(project, "evaluation_criteria", "") or "",
        "rules": getattr(project, "rules", "") or "",
        "available_time": str(getattr(project, "available_hours", "")) or "24-48",
        "team_size": str(getattr(project, "team_size", "")) or "4",
        "team_experience": getattr(project, "team_experience", "") or "",
        "preferred_languages": str(getattr(project, "preferred_languages", "") or ""),
        "preferred_frameworks": str(getattr(project, "preferred_frameworks", "") or ""),
        "target_platform": getattr(project, "target_platform", "") or "",
        "skills": str(getattr(project, "skills", "") or ""),
        "excluded_technologies": str(getattr(project, "excluded_technologies", "") or ""),
        "additional_constraints": getattr(project, "constraints", "") or "",
    }


# ─── Database ──────────────────────────────────────────────────────────


async def _get_existing(db: AsyncSession, project_id: str) -> Optional[dict[str, Any]]:
    """Get existing challenge analysis if available."""
    result = await db.execute(
        select(ChallengeIntelligence).where(
            ChallengeIntelligence.project_id == project_id
        )
    )
    ci = result.scalar_one_or_none()
    if ci:
        return _to_response(ci)
    return None


async def _store_analysis(
    db: AsyncSession,
    project_id: str,
    analysis: dict[str, Any],
) -> ChallengeIntelligence:
    """Store or update challenge analysis in database."""
    # Check if exists
    result = await db.execute(
        select(ChallengeIntelligence).where(
            ChallengeIntelligence.project_id == project_id
        )
    )
    existing = result.scalar_one_or_none()

    scores = analysis.get("difficulty", {}) or {}
    core = analysis.get("core_problem", {}) or {}

    if existing:
        # Update
        existing.executive_summary = analysis.get("executive_summary", existing.executive_summary)
        existing.core_problem = core.get("problem", existing.core_problem)
        existing.who_experiences = core.get("who_experiences", existing.who_experiences)
        existing.why_important = core.get("why_important", existing.why_important)
        existing.hidden_problems = analysis.get("hidden_problems", existing.hidden_problems)
        existing.stakeholders = analysis.get("stakeholders", existing.stakeholders)
        existing.constraints = analysis.get("constraints", existing.constraints)
        existing.success_criteria = analysis.get("success_criteria", existing.success_criteria)
        existing.opportunity_areas = analysis.get("opportunity_areas", existing.opportunity_areas)
        existing.innovation_opportunities = analysis.get("innovation_opportunities", existing.innovation_opportunities)
        existing.risk_areas = analysis.get("risk_areas", existing.risk_areas)
        existing.difficulty_technical = scores.get("technical", existing.difficulty_technical)
        existing.difficulty_research = scores.get("research", existing.difficulty_research)
        existing.difficulty_demo = scores.get("demo", existing.difficulty_demo)
        existing.difficulty_judge = scores.get("judge", existing.difficulty_judge)
        existing.difficulty_overall = scores.get("overall", existing.difficulty_overall)
        existing.recommended_strategy = analysis.get("recommended_strategy", existing.recommended_strategy)
        existing.themes = analysis.get("themes", existing.themes)
        existing.keywords = analysis.get("keywords", existing.keywords)
        existing.confidence = analysis.get("confidence", existing.confidence)
        existing.model_used = analysis.get("model_used", existing.model_used)
        ci = existing
    else:
        # Create new
        ci = ChallengeIntelligence(
            project_id=project_id,
            executive_summary=analysis.get("executive_summary"),
            core_problem=core.get("problem"),
            who_experiences=core.get("who_experiences"),
            why_important=core.get("why_important"),
            hidden_problems=analysis.get("hidden_problems"),
            stakeholders=analysis.get("stakeholders"),
            constraints=analysis.get("constraints"),
            success_criteria=analysis.get("success_criteria"),
            opportunity_areas=analysis.get("opportunity_areas"),
            innovation_opportunities=analysis.get("innovation_opportunities"),
            risk_areas=analysis.get("risk_areas"),
            difficulty_technical=scores.get("technical"),
            difficulty_research=scores.get("research"),
            difficulty_demo=scores.get("demo"),
            difficulty_judge=scores.get("judge"),
            difficulty_overall=scores.get("overall"),
            recommended_strategy=analysis.get("recommended_strategy"),
            themes=analysis.get("themes"),
            keywords=analysis.get("keywords"),
            confidence=analysis.get("confidence", 0.0),
            model_used=analysis.get("model_used"),
        )
        db.add(ci)

    await db.commit()
    await db.refresh(ci)
    return ci


async def _clear_existing(db: AsyncSession, project_id: str) -> None:
    """Delete existing challenge analysis."""
    result = await db.execute(
        select(ChallengeIntelligence).where(
            ChallengeIntelligence.project_id == project_id
        )
    )
    ci = result.scalar_one_or_none()
    if ci:
        await db.delete(ci)
        await db.commit()


# ─── Response Formatting ───────────────────────────────────────────────


def _to_response(ci: ChallengeIntelligence) -> dict[str, Any]:
    """Format ChallengeIntelligence model to API response (Bible §8.2)."""
    return {
        "id": ci.id,
        "project_id": ci.project_id,
        "executive_summary": ci.executive_summary or "",
        "core_problem": {
            "problem": ci.core_problem or "",
            "who_experiences": ci.who_experiences or "",
            "why_important": ci.why_important or "",
        },
        "hidden_problems": ci.hidden_problems or [],
        "stakeholders": ci.stakeholders or [],
        "constraints": ci.constraints or [],
        "success_criteria": ci.success_criteria or [],
        "opportunity_areas": ci.opportunity_areas or [],
        "innovation_opportunities": ci.innovation_opportunities or [],
        "risk_areas": ci.risk_areas or [],
        "difficulty": {
            "technical": ci.difficulty_technical,
            "research": ci.difficulty_research,
            "demo": ci.difficulty_demo,
            "judge": ci.difficulty_judge,
            "overall": ci.difficulty_overall,
        },
        "recommended_strategy": ci.recommended_strategy or "",
        "themes": ci.themes or [],
        "keywords": ci.keywords or [],
        "confidence": ci.confidence or 0.0,
        "model_used": ci.model_used or "",
        "created_at": ci.created_at.isoformat() if ci.created_at else None,
    }


def _empty_response() -> dict[str, Any]:
    """Return an empty challenge intelligence response."""
    return {
        "executive_summary": "",
        "core_problem": {"problem": "", "who_experiences": "", "why_important": ""},
        "hidden_problems": [],
        "stakeholders": [],
        "constraints": [],
        "success_criteria": [],
        "opportunity_areas": [],
        "innovation_opportunities": [],
        "risk_areas": [],
        "difficulty": {"technical": None, "research": None, "demo": None, "judge": None, "overall": None},
        "recommended_strategy": "",
        "themes": [],
        "keywords": [],
        "confidence": 0.0,
        "model_used": "",
    }
