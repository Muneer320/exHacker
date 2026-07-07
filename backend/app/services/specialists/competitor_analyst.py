"""Competitor Analyst (S3) — competitive intelligence from research data.

Bible §6.2 S3:
  Purpose: Analyze competitive landscape and identify differentiation opportunities.
  Model: Tier 2 (reasoning — glm-5.2).
  Inputs: Challenge Intelligence (S1) + Research Report (S2).
  Outputs: Competitor profiles, comparison matrix, gap analysis,
           differentiation opportunities, innovation scores, warnings.
  Limits: Must NOT suggest copying competitors. Focus on gaps and weaknesses.
  Success: Identifies 3+ meaningful differentiation strategies.
  Failure: Returns generic analysis. Fallback: template-based SWOT format.
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
from app.models.competitor import CompetitorIntelligence
from app.services.specialists.challenge_analyst import get_analysis as get_challenge
from app.services.specialists.research_specialist import run_research as run_s2_research
from app.services.project import get_project

logger = logging.getLogger(__name__)


async def analyze_competitors(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Run the full Competitor Intelligence pipeline (S3).

    1. Check cache
    2. Load S1 (Challenge) and S2 (Research)
    3. Build context from both
    4. Generate analysis via AI Gateway (Tier 2)
    5. Parse, validate, store
    6. Return structured report
    """
    # 1. Check cache
    existing = await _get_existing(db, project_id)
    if existing and existing.get("confidence", 0) >= 0.5:
        logger.info("Using cached competitor analysis for project %s", project_id)
        return existing

    # 2. Load inputs (auto-trigger S2 research if not available)
    challenge = await get_challenge(db, project_id)
    has_challenge = bool(challenge and challenge.get("executive_summary"))

    # Ensure research is available
    research = await _ensure_research(db, project_id)
    if not research or not research.get("summary", {}).get("total_results", 0):
        logger.warning("No research data available for project %s, using empty analysis", project_id)
        return await _store_analysis(db, project_id, _fallback_analysis())

    # 3. Build context
    context = _build_context(challenge, research, has_challenge)

    # 4. Generate analysis via AI Gateway (Tier 2)
    analysis = await _generate_analysis(context)
    if not analysis:
        logger.warning("AI analysis failed for project %s, using fallback", project_id)
        analysis = _fallback_analysis()

    # 5. Calculate confidence
    analysis["confidence"] = _calculate_confidence(analysis)

    # 6. Store
    stored = await _store_analysis(db, project_id, analysis)
    return stored


async def get_analysis(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Get existing competitor analysis without regenerating."""
    existing = await _get_existing(db, project_id)
    if existing:
        return existing
    return _empty_response()


async def refresh_analysis(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Force-refresh competitor analysis."""
    await _clear_existing(db, project_id)
    return await analyze_competitors(db, project_id)


# ─── Context Building ────────────────────────────────────────────────────


async def _ensure_research(db: AsyncSession, project_id: str) -> dict[str, Any]:
    """Ensure research data exists, triggering S2 if needed."""
    project = await get_project(db, project_id)
    research = await run_s2_research(db, project_id)
    return research


def _build_context(
    challenge: dict[str, Any],
    research: dict[str, Any],
    has_challenge: bool,
) -> dict[str, str]:
    """Build context dict for the S3 prompt."""
    summary = research.get("summary", {})
    categories = summary.get("categories", [])

    # Extract details per category
    product_details = _cat_details(categories, "product")
    api_details = _cat_details(categories, "api")
    oss_details = _cat_details(categories, "oss")
    winner_details = _cat_details(categories, "hackathon_winner")
    trend_details = _cat_details(categories, "trend")

    synthesis = research.get("synthesis", {}) or {}
    syn = synthesis.get("synthesis", {}) or {}
    tech_recs = synthesis.get("technology_recommendations", []) or []
    diff_opps = synthesis.get("differentiation_opportunities", []) or []
    risks = synthesis.get("risks_from_research", []) or []
    priorities = synthesis.get("recommended_priorities", []) or []

    ctx = {
        "executive_summary": challenge.get("executive_summary", "") if has_challenge else "",
        "core_problem": challenge.get("core_problem", {}).get("problem", "") if has_challenge else "",
        "themes": _join(challenge.get("themes", [])),
        "opportunity_areas": _join(challenge.get("opportunity_areas", [])),
        "innovation_opportunities": _join([io.get("area", "") for io in challenge.get("innovation_opportunities", [])]),
        "product_count": str(len(product_details)),
        "product_details": "\n".join(product_details)[:2000],
        "api_count": str(len(api_details)),
        "api_details": "\n".join(api_details)[:1000],
        "oss_count": str(len(oss_details)),
        "oss_details": "\n".join(oss_details)[:1000],
        "winner_count": str(len(winner_details)),
        "winner_details": "\n".join(winner_details)[:1000],
        "trend_count": str(len(trend_details)),
        "trend_details": "\n".join(trend_details)[:1000],
        "key_opportunities": _join(syn.get("key_opportunities", [])),
        "critical_gaps": _join(syn.get("critical_gaps", [])),
        "competitor_landscape": syn.get("competitor_landscape", ""),
        "differentiation_opportunities": _join([d.get("area", "") for d in diff_opps]),
        "tech_recommendations": _join([t.get("technology", "") for t in tech_recs]),
        "risks_from_research": _join([r.get("risk", "") for r in risks]),
        "recommended_priorities": _join(priorities),
    }
    return ctx


def _cat_details(categories: list[dict[str, Any]], cat_id: str) -> list[str]:
    """Extract item details from a research category."""
    for cat in categories:
        if cat.get("id") == cat_id:
            items = cat.get("items", [])
            return [f"  - {i.get('title', '')}: {i.get('snippet', '')[:100]}" for i in items[:5]]
    return []


# ─── AI Generation (Tier 2) ──────────────────────────────────────────────


async def _generate_analysis(context: dict[str, str]) -> Optional[dict[str, Any]]:
    """Generate competitive analysis via AI Gateway (Tier 2)."""
    try:
        system, user = prompt_manager.render("competitor_analyst", **context)
    except FileNotFoundError:
        system = (
            "You are a senior startup strategist. Analyze the competitive landscape "
            "based on the following research data. Return ONLY a JSON object with "
            "competitor profiles, comparison matrix, gap analysis, differentiation "
            "opportunities, innovation score, and warnings."
        )
        user = f"Research context: {json.dumps(context)[:3000]}"

    response = await gateway.generate(
        Prompt(system=system, user=user),
        model_tier=ModelTier.TIER_2,
    )
    return _parse_analysis(response.content)


def _parse_analysis(text: str) -> Optional[dict[str, Any]]:
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


def _calculate_confidence(analysis: dict[str, Any]) -> float:
    """Calculate confidence based on completeness."""
    required = ["competitors", "gap_analysis", "innovation_score"]
    present = sum(1 for f in required if analysis.get(f))
    return round(present / len(required), 2)


# ─── Fallback ────────────────────────────────────────────────────────────


def _fallback_analysis() -> dict[str, Any]:
    """Return fallback analysis when AI fails."""
    return {
        "summary": "Competitive analysis could not be completed with available data.",
        "landscape_summary": "Limited data available for competitive analysis.",
        "competitors": [],
        "comparison_matrix": [],
        "gap_analysis": {
            "patterns": ["Limited data to identify patterns"],
            "white_space": ["Unknown — additional research needed"],
            "pain_points": ["Unknown"],
            "hackathon_opportunities": ["Build a focused prototype that addresses the core problem"],
            "oversaturated": ["Unknown"],
            "to_avoid": ["Over-engineering for a hackathon timeline"],
        },
        "quick_wins": [
            {"title": "Core feature prototype", "difficulty": 30, "impact": 70, "judge_appeal": 65, "effort_hours": 4},
        ],
        "medium_innovations": [],
        "moonshots": [],
        "innovation_score": 50,
        "innovation_breakdown": {
            "market_saturation": 50,
            "technical_novelty": 50,
            "execution_feasibility": 70,
            "judge_memorability": 50,
            "business_potential": 50,
        },
        "warnings": [
            {"warning": "Insufficient research data", "why": "The research pipeline did not find enough competitors to do a thorough analysis.", "alternative": "Run additional targeted searches or manually add competitive data."},
        ],
    }


# ─── Database ────────────────────────────────────────────────────────────


async def _get_existing(db: AsyncSession, project_id: str) -> Optional[dict[str, Any]]:
    result = await db.execute(
        select(CompetitorIntelligence).where(CompetitorIntelligence.project_id == project_id)
    )
    ci = result.scalar_one_or_none()
    if ci:
        return _to_response(ci)
    return None


async def _store_analysis(
    db: AsyncSession, project_id: str, analysis: dict[str, Any],
) -> dict[str, Any]:
    result = await db.execute(
        select(CompetitorIntelligence).where(CompetitorIntelligence.project_id == project_id)
    )
    existing = result.scalar_one_or_none()

    innovation = analysis.get("innovation_breakdown", {}) or {}

    data = {
        "summary": analysis.get("summary") or analysis.get("landscape_summary", ""),
        "landscape_summary": analysis.get("landscape_summary", analysis.get("summary", "")),
        "competitors": analysis.get("competitors", []),
        "comparison_matrix": analysis.get("comparison_matrix", []),
        "gap_analysis": analysis.get("gap_analysis", {}),
        "quick_wins": analysis.get("quick_wins", []),
        "medium_innovations": analysis.get("medium_innovations", []),
        "moonshots": analysis.get("moonshots", []),
        "innovation_score": analysis.get("innovation_score", 0),
        "innovation_breakdown": innovation,
        "warnings": analysis.get("warnings", []),
        "keywords": analysis.get("keywords", []),
        "themes": analysis.get("themes", []),
        "model_used": analysis.get("model_used", ""),
        "confidence": analysis.get("confidence", 0.0),
    }

    if existing:
        for key, value in data.items():
            if value is not None and hasattr(existing, key):
                setattr(existing, key, value)
        await db.commit()
        await db.refresh(existing)
        return _to_response(existing)

    ci = CompetitorIntelligence(project_id=project_id, **data)
    db.add(ci)
    await db.commit()
    await db.refresh(ci)
    return _to_response(ci)


async def _clear_existing(db: AsyncSession, project_id: str) -> None:
    result = await db.execute(
        select(CompetitorIntelligence).where(CompetitorIntelligence.project_id == project_id)
    )
    ci = result.scalar_one_or_none()
    if ci:
        await db.delete(ci)
        await db.commit()


# ─── Response Formatting ─────────────────────────────────────────────────


def _to_response(ci: CompetitorIntelligence) -> dict[str, Any]:
    return {
        "id": ci.id,
        "project_id": ci.project_id,
        "summary": ci.summary or "",
        "landscape_summary": ci.landscape_summary or "",
        "competitors": ci.competitors or [],
        "comparison_matrix": ci.comparison_matrix or [],
        "gap_analysis": ci.gap_analysis or {},
        "quick_wins": ci.quick_wins or [],
        "medium_innovations": ci.medium_innovations or [],
        "moonshots": ci.moonshots or [],
        "innovation_score": ci.innovation_score,
        "innovation_breakdown": ci.innovation_breakdown or {},
        "warnings": ci.warnings or [],
        "keywords": ci.keywords or [],
        "themes": ci.themes or [],
        "confidence": ci.confidence or 0.0,
        "model_used": ci.model_used or "",
        "created_at": ci.created_at.isoformat() if ci.created_at else None,
    }


def _join(items: list) -> str:
    return ", ".join(str(i) for i in items if i) if items else ""


def _empty_response() -> dict[str, Any]:
    return {
        "summary": "", "landscape_summary": "",
        "competitors": [], "comparison_matrix": [],
        "gap_analysis": {}, "quick_wins": [], "medium_innovations": [],
        "moonshots": [], "innovation_score": None,
        "innovation_breakdown": {}, "warnings": [],
        "keywords": [], "themes": [],
        "confidence": 0.0, "model_used": "",
    }
