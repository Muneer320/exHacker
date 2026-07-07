"""Idea Generator (S5) — the heart of exHacker (Bible §6.2 S5).

This is the single most important specialist in the system.
Everything before gathers intelligence. Everything after builds the chosen idea.

Pipeline:
  1. Load shared context (S1, S2, S3, project, decisions)
  2. Generate 5 ideas via AI Gateway (Tier 2)
  3. Self-critique and improve (Tier 2)
  4. Parse, validate, enhance with metadata
  5. Store in database
  6. Log decision journal entries
  7. Store in shared memory
  8. Return structured response
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gateway import Prompt, ModelTier, gateway
from app.ai.prompts import prompt_manager
from app.models.idea import Idea
from app.services.shared.memory import store_memory, log_decision
from app.services.shared.context import load_context, format_context_for_prompt
from app.services.project import get_project

logger = logging.getLogger(__name__)


async def generate_ideas(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Run the full Idea Generation pipeline (S5)."""
    # 1. Check cache
    cached = await _get_existing(db, project_id)
    if cached:
        return cached

    # 2. Load shared context
    ctx = await load_context(db, project_id)
    project = ctx.get("project", {})

    # 3. Build context dict for prompts
    context = _build_context(ctx, project)
    context_str = format_context_for_prompt(ctx)

    logger.info("Generating ideas for project %s with %d memory entries",
                project_id, len(ctx.get("memory_list", [])))

    # 4. Generate ideas (Tier 2)
    ideas_data = await _generate(context)

    # 5. Self-critique (Tier 2)
    ideas_data = await _critique(ideas_data, project)

    # 6. Parse and validate
    parsed = _parse_ideas(ideas_data)
    if not parsed:
        logger.warning("Failed to parse ideas for project %s, using fallback", project_id)
        parsed = _fallback_ideas()

    # 7. Enrich with metadata
    generation_id = str(uuid.uuid4())
    stored = []
    for i, idea in enumerate(parsed):
        entry = await _store_idea(db, project_id, generation_id, idea, i)
        stored.append(entry)

    # 8. Log decisions
    await log_decision(
        db, project_id=project_id,
        title=f"Generated {len(stored)} product ideas",
        category="direction_generated",
        description=f"S5 generated {len(stored)} distinct product ideas across different strategic directions.",
        originating_specialist="idea_generator",
        references=[s["id"] for s in stored],
    )

    # 9. Store in shared memory
    await store_memory(
        db, project_id=project_id,
        specialist="idea_generator",
        memory_type="ideas_generated",
        content={"generation_id": generation_id, "count": len(stored)},
        confidence=0.85,
        references=[s["id"] for s in stored],
    )

    result = {
        "generation_id": generation_id,
        "ideas": stored,
        "count": len(stored),
    }
    return result


async def get_ideas(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Get existing ideas without regenerating."""
    result = await db.execute(
        select(Idea)
        .where(Idea.project_id == project_id)
        .order_by(Idea.rank)
    )
    ideas = [_idea_to_dict(e) for e in result.scalars().all()]
    if ideas:
        gen_id = ideas[0].get("generation_id", "")
        return {"generation_id": gen_id, "ideas": ideas, "count": len(ideas)}
    return {"generation_id": "", "ideas": [], "count": 0}


async def refresh_ideas(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Force-refresh ideas."""
    result = await db.execute(
        select(Idea).where(Idea.project_id == project_id)
    )
    for e in result.scalars().all():
        await db.delete(e)
    await db.commit()
    return await generate_ideas(db, project_id)


async def select_idea(
    db: AsyncSession,
    project_id: str,
    idea_id: str,
) -> dict[str, Any]:
    """Select an idea as the project direction."""
    # Unselect all
    result = await db.execute(
        select(Idea).where(Idea.project_id == project_id)
    )
    for idea in result.scalars().all():
        if idea.id == idea_id:
            idea.is_selected = "selected"
        else:
            idea.is_selected = None
    await db.commit()

    # Get the selected idea
    result = await db.execute(
        select(Idea).where(Idea.id == idea_id)
    )
    idea = result.scalar_one_or_none()
    if idea:
        await log_decision(
            db, project_id=project_id,
            title=f"Direction selected: {idea.title}",
            category="opportunity_selected",
            description=idea.elevator_pitch or idea.hook or idea.title,
            originating_specialist="idea_generator",
            references=[idea_id],
        )
        return _idea_to_dict(idea)
    return {}


# ─── AI Generation (Tier 2) ─────────────────────────────────────────────


async def _generate(context: dict[str, str]) -> Optional[str]:
    """Generate ideas via AI Gateway (Tier 2 — strongest reasoning)."""
    try:
        system, user = prompt_manager.render("idea_generator", **context)
    except FileNotFoundError:
        system = "You are a senior hackathon mentor. Generate 5 differentiated product ideas. Return ONLY a JSON object with key 'ideas'."
        user = f"Challenge: {context.get('challenge_statement', '')}\nTeam: {context.get('team_size', '4')} people, {context.get('available_hours', '48')} hours"

    response = await gateway.generate(
        Prompt(system=system, user=user),
        model_tier=ModelTier.TIER_2,
    )
    return response.content


async def _critique(
    ideas_raw: Optional[str],
    project: dict[str, Any],
) -> Optional[str]:
    """Self-critique generated ideas (Tier 2)."""
    if not ideas_raw:
        return None
    try:
        system, user = prompt_manager.render("idea_critique", **{
            "ideas_json": ideas_raw[:6000],
            "available_hours": project.get("available_hours", "48"),
            "team_size": project.get("team_size", "4"),
            "skills": project.get("skills", "general"),
        })
        response = await gateway.generate(
            Prompt(system=system, user=user),
            model_tier=ModelTier.TIER_2,
        )
        return response.content
    except Exception as e:
        logger.warning("Idea critique failed, using raw ideas: %s", e)
        return ideas_raw


def _parse_ideas(text: Optional[str]) -> Optional[list[dict[str, Any]]]:
    """Parse AI response into list of idea dicts."""
    if not text:
        return None
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
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    ideas = data.get("ideas", []) if isinstance(data, dict) else data
    if not isinstance(ideas, list):
        return None
    # Must have at least 2 ideas
    return ideas if len(ideas) >= 2 else None


def _build_context(ctx: dict[str, Any], project: dict[str, Any]) -> dict[str, str]:
    """Build flat context dict for prompt rendering."""
    challenge = ctx.get("memory", {}).get("challenge_intelligence", {}).get("content", {}) or {}
    competitor = ctx.get("memory", {}).get("competitor_intelligence", {}).get("content", {}) or {}

    decisions = ctx.get("decisions", [])
    decisions_text = "\n".join(
        f"  #{d.get('entry_number', '?')} {d.get('title', '')} [{d.get('category', '')}]"
        for d in decisions[:5]
    ) if decisions else "No decisions yet."

    competitor_details = ""
    competitors_list = competitor.get("competitors", [])
    for c in competitors_list[:5]:
        competitor_details += f"  - {c.get('name', '')}: {c.get('description', '')[:80]}\n"

    gap = competitor.get("gap_analysis", {}) or {}
    context = {
        "project_name": project.get("name", "Unnamed"),
        "project_idea": project.get("idea", ""),
        "challenge_statement": project.get("challenge_statement", project.get("idea", "")),
        "theme": project.get("theme", ""),
        "available_hours": project.get("available_hours", "48"),
        "team_size": project.get("team_size", "4"),
        "skills": project.get("skills", "general"),
        "target_platform": project.get("target_platform", "web"),
        "team_experience": project.get("team_experience", "intermediate"),
        "challenge_summary": (challenge.get("executive_summary") or "")[:500],
        "core_problem": (challenge.get("core_problem", {}).get("problem") or "")[:300],
        "hidden_problems": ", ".join((challenge.get("hidden_problems") or [])[:3]),
        "opportunity_areas": ", ".join((challenge.get("opportunity_areas") or [])[:5]),
        "innovation_opportunities": ", ".join(
            [io.get("area", "") for io in (challenge.get("innovation_opportunities") or [])[:3]]
        ),
        "competitors_found": str(len(competitors_list)),
        "competitor_details": competitor_details or "  - No specific competitors found.",
        "key_opportunities": ", ".join(
            (competitor.get("synthesis", {}).get("key_opportunities") or [])[:3]
        ) if isinstance(competitor, dict) else "",
        "critical_gaps": ", ".join(
            (competitor.get("synthesis", {}).get("critical_gaps") or [])[:3]
        ) if isinstance(competitor, dict) else "",
        "tech_recommendations": ", ".join(
            [t.get("technology", "") for t in (competitor.get("technology_recommendations") or [])[:3]]
        ) if isinstance(competitor, dict) else "",
        "landscape_summary": (competitor.get("landscape_summary") or "")[:300],
        "white_space": ", ".join((gap.get("white_space") or [])[:5]),
        "to_avoid": ", ".join((gap.get("to_avoid") or [])[:3]),
        "diff_opportunities": ", ".join(
            [d.get("area", "") for d in (competitor.get("quick_wins") or [])[:3] + (competitor.get("medium_innovations") or [])[:2]]
        ) if isinstance(competitor, dict) else "",
        "innovation_range": str((competitor.get("innovation_score") or 60)),
        "recent_decisions": decisions_text,
    }
    return context


# ─── Database ───────────────────────────────────────────────────────────


async def _get_existing(db: AsyncSession, project_id: str) -> Optional[dict[str, Any]]:
    result = await db.execute(
        select(Idea).where(Idea.project_id == project_id).order_by(Idea.rank)
    )
    ideas = [_idea_to_dict(e) for e in result.scalars().all()]
    if ideas:
        return {"generation_id": ideas[0].get("generation_id", ""), "ideas": ideas, "count": len(ideas)}
    return None


async def _store_idea(
    db: AsyncSession,
    project_id: str,
    generation_id: str,
    idea: dict[str, Any],
    rank: int,
) -> dict[str, Any]:
    """Store a single parsed idea in the database."""
    scores = idea.get("scores", {}) or {}
    risks = idea.get("technical_risks", [])

    entry = Idea(
        project_id=project_id,
        generation_id=generation_id,
        title=(idea.get("title") or f"Idea {rank + 1}")[:200],
        hook=(idea.get("hook") or "")[:500],
        elevator_pitch=(idea.get("elevator_pitch") or "")[:1000],
        problem_statement=(idea.get("problem_statement") or "")[:2000],
        solution=(idea.get("solution") or "")[:2000],
        target_users=(idea.get("target_users") or "")[:500],
        why_now=(idea.get("why_now") or "")[:1000],
        usp=(idea.get("unique_selling_proposition") or "")[:500],
        strategy_label=(idea.get("strategy_label") or "")[:200],
        innovation_summary=(idea.get("innovation_summary") or "")[:1000],
        competitive_differentiation=(idea.get("competitive_differentiation") or "")[:1000],
        technical_highlights=(idea.get("technical_highlights") or "")[:1000],
        core_features=idea.get("core_features", []),
        stretch_features=idea.get("stretch_features", []),
        demo_scenario=(idea.get("demo_scenario") or "")[:2000],
        judge_wow_moment=(idea.get("judge_wow_moment") or "")[:1000],
        technical_risks=risks[:10],
        business_potential=(idea.get("business_potential") or "")[:1000],
        estimated_build_hours=idea.get("estimated_build_hours"),
        estimated_difficulty=idea.get("estimated_difficulty"),
        recommended_team_size=(idea.get("recommended_team_size") or "3-4")[:20],
        recommended_roles=idea.get("recommended_roles", []),
        future_roadmap=idea.get("future_roadmap", []),
        target_platform=idea.get("target_platform", ""),
        score_innovation=scores.get("innovation"),
        score_creativity=scores.get("creativity"),
        score_technical_depth=scores.get("technical_depth"),
        score_feasibility=scores.get("feasibility"),
        score_demo_potential=scores.get("demo_potential"),
        score_judge_appeal=scores.get("judge_appeal"),
        score_business_potential=scores.get("business_potential"),
        score_originality=scores.get("originality"),
        score_confidence=scores.get("confidence"),
        score_overall=scores.get("overall"),
        why_generated=(idea.get("why_generated") or "")[:2000],
        gap_addressed=(idea.get("gap_addressed") or "")[:500],
        comparison_tags=idea.get("comparison_tags", []),
        rank=rank,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return _idea_to_dict(entry)


# ─── Response Formatting ────────────────────────────────────────────────


def _idea_to_dict(entry: Idea) -> dict[str, Any]:
    """Convert Idea model to API response dict."""
    return {
        "id": entry.id,
        "project_id": entry.project_id,
        "generation_id": entry.generation_id,
        "title": entry.title,
        "hook": entry.hook or "",
        "elevator_pitch": entry.elevator_pitch or "",
        "problem_statement": entry.problem_statement or "",
        "solution": entry.solution or "",
        "target_users": entry.target_users or "",
        "why_now": entry.why_now or "",
        "usp": entry.usp or "",
        "strategy_label": entry.strategy_label or "",
        "innovation_summary": entry.innovation_summary or "",
        "competitive_differentiation": entry.competitive_differentiation or "",
        "technical_highlights": entry.technical_highlights or "",
        "core_features": entry.core_features or [],
        "stretch_features": entry.stretch_features or [],
        "demo_scenario": entry.demo_scenario or "",
        "judge_wow_moment": entry.judge_wow_moment or "",
        "technical_risks": entry.technical_risks or [],
        "business_potential": entry.business_potential or "",
        "estimated_build_hours": entry.estimated_build_hours,
        "estimated_difficulty": entry.estimated_difficulty,
        "recommended_team_size": entry.recommended_team_size or "",
        "recommended_roles": entry.recommended_roles or [],
        "future_roadmap": entry.future_roadmap or [],
        "target_platform": entry.target_platform or "",
        "scores": {
            "innovation": entry.score_innovation,
            "creativity": entry.score_creativity,
            "technical_depth": entry.score_technical_depth,
            "feasibility": entry.score_feasibility,
            "demo_potential": entry.score_demo_potential,
            "judge_appeal": entry.score_judge_appeal,
            "business_potential": entry.score_business_potential,
            "originality": entry.score_originality,
            "confidence": entry.score_confidence,
            "overall": entry.score_overall,
        },
        "why_generated": entry.why_generated or "",
        "gap_addressed": entry.gap_addressed or "",
        "comparison_tags": entry.comparison_tags or [],
        "is_selected": entry.is_selected == "selected",
        "rank": entry.rank or 0,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


def _fallback_ideas() -> list[dict[str, Any]]:
    """Return 5 fallback ideas when AI generation fails."""
    return [
        {
            "title": "AI-Powered Personal Assistant",
            "hook": "Your intelligent copilot for everyday tasks",
            "elevator_pitch": "An AI assistant that learns your habits and proactively helps you manage tasks, schedule, and priorities.",
            "problem_statement": "People are overwhelmed with daily tasks and struggle to prioritize effectively.",
            "solution": "AI-powered assistant that learns user behavior and provides proactive suggestions.",
            "strategy_label": "Most Practical",
            "core_features": ["Smart scheduling", "Task prioritization", "Habit tracking"],
            "stretch_features": ["Calendar integration", "Email summarization"],
            "estimated_build_hours": 24,
            "estimated_difficulty": 50,
            "scores": {"innovation": 70, "creativity": 65, "technical_depth": 68, "feasibility": 80, "demo_potential": 75, "judge_appeal": 72, "business_potential": 75, "originality": 68, "confidence": 70, "overall": 72},
            "why_generated": "Fallback — AI generation was unavailable.",
            "comparison_tags": ["most_practical", "fastest_to_build"],
        },
        {
            "title": "Collaborative Project Hub",
            "hook": "Build better together",
            "elevator_pitch": "A real-time collaboration platform for teams to brainstorm, plan, and execute projects together.",
            "problem_statement": "Teams lack a unified space for project ideation and planning.",
            "solution": "Real-time collaborative workspace with AI-enhanced brainstorming tools.",
            "strategy_label": "Highest Judge Appeal",
            "core_features": ["Real-time collaboration", "AI brainstorming", "Task management"],
            "stretch_features": ["Video calls", "Whiteboard"],
            "estimated_build_hours": 36,
            "estimated_difficulty": 65,
            "scores": {"innovation": 65, "creativity": 72, "technical_depth": 75, "feasibility": 70, "demo_potential": 85, "judge_appeal": 82, "business_potential": 70, "originality": 72, "confidence": 68, "overall": 70},
            "why_generated": "Fallback — AI generation was unavailable.",
            "comparison_tags": ["best_judge_appeal", "most_collaborative"],
        },
        {
            "title": "Smart Budget Tracker",
            "hook": "Know where every dollar goes",
            "elevator_pitch": "An intelligent expense tracker that categorizes spending and provides actionable savings insights automatically.",
            "problem_statement": "People struggle to track spending and save money effectively.",
            "solution": "Automated expense categorization with personalized savings recommendations.",
            "strategy_label": "Most Innovative",
            "core_features": ["Auto-categorization", "Spending insights", "Savings goals"],
            "stretch_features": ["Investment tracking", "Bill reminders"],
            "estimated_build_hours": 30,
            "estimated_difficulty": 60,
            "scores": {"innovation": 82, "creativity": 78, "technical_depth": 70, "feasibility": 75, "demo_potential": 80, "judge_appeal": 78, "business_potential": 85, "originality": 80, "confidence": 75, "overall": 78},
            "why_generated": "Fallback — AI generation was unavailable.",
            "comparison_tags": ["most_innovative", "highest_business"],
        },
        {
            "title": "Health & Wellness Coach",
            "hook": "Your personal wellness companion",
            "elevator_pitch": "An AI wellness coach that creates personalized fitness, nutrition, and mindfulness plans based on your goals and habits.",
            "problem_statement": "People want personalized wellness guidance but can't afford coaches.",
            "solution": "AI wellness coach that adapts to individual goals, preferences, and progress.",
            "strategy_label": "Highest Tech Depth",
            "core_features": ["Personalized plans", "Progress tracking", "AI recommendations"],
            "stretch_features": ["Meal planning", "Meditation guides"],
            "estimated_build_hours": 40,
            "estimated_difficulty": 75,
            "scores": {"innovation": 75, "creativity": 80, "technical_depth": 85, "feasibility": 60, "demo_potential": 78, "judge_appeal": 85, "business_potential": 80, "originality": 78, "confidence": 72, "overall": 76},
            "why_generated": "Fallback — AI generation was unavailable.",
            "comparison_tags": ["highest_technical_depth", "best_judge_appeal"],
        },
        {
            "title": "Eco Lifestyle Tracker",
            "hook": "Small changes, big impact",
            "elevator_pitch": "Track your carbon footprint, discover sustainable alternatives, and earn rewards for eco-friendly choices.",
            "problem_statement": "People want to live sustainably but don't know where to start.",
            "solution": "Gamified sustainability tracker with personalized recommendations and community challenges.",
            "strategy_label": "Highest Business Potential",
            "core_features": ["Carbon tracker", "Green alternatives", "Community challenges"],
            "stretch_features": ["Brand ratings", "Offset purchasing"],
            "estimated_build_hours": 32,
            "estimated_difficulty": 55,
            "scores": {"innovation": 85, "creativity": 82, "technical_depth": 68, "feasibility": 72, "demo_potential": 82, "judge_appeal": 80, "business_potential": 88, "originality": 84, "confidence": 78, "overall": 80},
            "why_generated": "Fallback — AI generation was unavailable.",
            "comparison_tags": ["highest_business", "most_innovative"],
        },
    ]
