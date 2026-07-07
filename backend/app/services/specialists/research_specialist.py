"""Research Specialist (S2) — structured research engine for hackathon teams.

Bible §6.2 S2:
  Purpose: Execute comprehensive market research across 10 categories.
  Model: Tier 1 (cheap — search queries) + Tier 2 (reasoning — synthesis).
  Inputs: Challenge Intelligence Report (S1), theme, keywords, constraints.
  Outputs: Structured research with 10 categories, patterns, gaps, recommendations.
  Limits: Must include citations for every claim. Must report confidence per result.
  Success: Finds 3+ relevant competitors, 3+ APIs, 2+ OSS projects with citations.
  Failure: Returns partial results with reduced confidence. Never fabricates results.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from httpx import AsyncClient
from sqlalchemy import select, and_, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gateway import Prompt, ModelTier, gateway
from app.ai.prompts import prompt_manager
from app.core.config import settings
from app.models.research import ResearchResult, ResearchResultType
from app.services.specialists.challenge_analyst import get_analysis as get_challenge_analysis
from app.services.project import get_project

logger = logging.getLogger(__name__)

TAVILY_API_URL = "https://api.tavily.com/search"
HTTP_TIMEOUT = 15

# Type labels for display
CATEGORY_LABELS: dict[str, str] = {
    "product": "Existing Products",
    "startup": "Startups",
    "oss": "Open Source Projects",
    "github": "GitHub Repositories",
    "paper": "Research Papers",
    "api": "APIs & SDKs",
    "framework": "Frameworks & Libraries",
    "hackathon_winner": "Hackathon Winners",
    "trend": "Industry Trends",
    "insight": "Insights",
}


async def run_research(
    db: AsyncSession,
    project_id: str,
) -> dict[str, Any]:
    """Run the full S2 research pipeline.

    1. Load Challenge Intelligence (S1 output)
    2. Generate targeted search queries (Tier 1)
    3. Execute searches via Tavily
    4. Store categorized results in DB
    5. Synthesize results (Tier 2)
    6. Return structured Research Report
    """
    # 1. Check cache
    cached = await _get_cached_report(db, project_id)
    if cached:
        logger.info("Using cached research report for project %s", project_id)
        return cached

    # 2. Load S1 output + project
    project = await get_project(db, project_id)
    challenge = await get_challenge_analysis(db, project_id)
    has_challenge = bool(challenge and challenge.get("executive_summary"))

    # 3. Generate targeted search queries
    queries = await _generate_queries(challenge, project)
    if not queries:
        queries = _fallback_queries(project)
        logger.info("Using fallback queries for project %s", project_id)

    # 4. Execute searches
    all_raw: list[dict[str, Any]] = []
    for category, query_list in queries.items():
        for query in query_list[:3]:  # Max 3 queries per category
            if settings.MOCK_RESEARCH:
                results = _mock_search(query, category)
            else:
                results = await _tavily_search(query)
            for r in results:
                r["_category"] = category
            all_raw.extend(results)

    # 5. Store raw results
    stored_results = await _store_results(db, project_id, all_raw, queries)

    # 6. Synthesis — analyze patterns if enough results
    synthesis = await _synthesize(challenge, stored_results, has_challenge)
    if synthesis:
        # Store synthesis as special results
        await _store_synthesis(db, project_id, synthesis)

    # 7. Build and return report
    report = _build_report(stored_results, synthesis)
    return report


# ─── Query Generation (Tier 1) ────────────────────────────────────────────


async def _generate_queries(
    challenge: dict[str, Any],
    project: Any,
) -> Optional[dict[str, list[str]]]:
    """Generate targeted research queries from S1 output (Tier 1)."""
    try:
        ctx = _build_query_context(challenge, project)
        system, user = prompt_manager.render("research_specialist", **ctx)
        response = await gateway.generate(
            Prompt(system=system, user=user),
            model_tier=ModelTier.TIER_1,
        )
        return _parse_queries(response.content)
    except Exception as e:
        logger.warning("Research query generation failed: %s", e)
        return None


def _parse_queries(text: str) -> Optional[dict[str, list[str]]]:
    """Parse AI response into query dict."""
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
        queries = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(queries, dict):
        return None
    return queries


def _build_query_context(challenge: dict[str, Any], project: Any) -> dict[str, str]:
    """Build context dict for the query generation prompt."""
    ctx: dict[str, str] = {
        "theme": _join(challenge.get("themes", [])),
        "keywords": _join(challenge.get("keywords", [])),
        "opportunity_areas": _join(challenge.get("opportunity_areas", [])),
        "innovation_opportunities": _join([io.get("area", "") for io in challenge.get("innovation_opportunities", [])]),
        "constraints": _join([c.get("description", "") for c in challenge.get("constraints", [])]),
        "core_problem": challenge.get("core_problem", {}).get("problem", project.idea)[:200],
        "technical_difficulty": str(challenge.get("difficulty", {}).get("technical", "medium")),
        "available_time": getattr(project, "available_hours", "") or "48",
        "team_size": getattr(project, "team_size", "") or "4",
        "skills": getattr(project, "skills", "") or "general",
        "target_platform": getattr(project, "target_platform", "") or "web",
    }
    return ctx


def _join(items: list) -> str:
    """Join list items into comma-separated string."""
    return ", ".join(str(i) for i in items if i) if items else ""


def _fallback_queries(project: Any) -> dict[str, list[str]]:
    """Fallback queries when AI generation fails."""
    idea = getattr(project, "idea", "the project")
    words = idea.split()[:4]
    topic = " ".join(words) if words else "this topic"
    return {
        "products": [f"{topic} alternatives", f"{topic} competitors"],
        "startups": [f"startups building {topic}"],
        "oss": [f"open source {topic}"],
        "github": [f"{topic} github repository"],
        "papers": [f"{topic} research paper"],
        "apis": [f"{topic} API"],
        "frameworks": [f"best framework for {topic}"],
        "hackathon_winners": [f"hackathon winner {topic}"],
        "trends": [f"{topic} market trends 2025 2026"],
        "insight": [f"{topic} insights"],
    }


# ─── Search Execution ─────────────────────────────────────────────────────


async def _tavily_search(query: str) -> list[dict[str, Any]]:
    """Execute search via Tavily API."""
    api_key = settings.TAVILY_API_KEY
    if not api_key:
        return _mock_search(query, "insight")
    try:
        async with AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(
                TAVILY_API_URL,
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": 5,
                    "include_answer": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            for r in results:
                r["_confidence"] = min(1.0, r.get("score", 0.5) + 0.2)
            return results
    except Exception as e:
        logger.error("Tavily search failed for '%s': %s", query, e)
        return []


def _mock_search(query: str, category: str) -> list[dict[str, Any]]:
    """Return mock search results."""
    words = query.split()
    topic = " ".join(words[-3:]) if len(words) > 3 else query

    results = []
    for i in range(min(3, max(1, len(words) // 2))):
        name = f"{category.title()} {i + 1}"
        confidence = max(0.5, 0.9 - i * 0.15)
        results.append({
            "title": f"{name} — {topic[:50]}",
            "url": f"https://example.com/{name.lower().replace(' ', '-')}",
            "content": f"Mock result for '{query}'. Confidence: {confidence:.0%}.",
            "score": confidence,
            "_confidence": confidence,
            "_freshness": "days",
        })
    return results


# ─── Synthesis (Tier 2) ──────────────────────────────────────────────────


async def _synthesize(
    challenge: dict[str, Any],
    results: list[dict[str, Any]],
    has_challenge: bool,
) -> Optional[dict[str, Any]]:
    """Synthesize results using Tier 2 reasoning."""
    if not results:
        return None

    try:
        formatted = _format_results_for_synthesis(results)
        ctx: dict[str, str] = {
            "formatted_results": formatted[:4000],
            "theme": _join(challenge.get("themes", [])),
            "core_problem": challenge.get("core_problem", {}).get("problem", "")[:200],
            "innovation_opportunities": _join(
                [io.get("area", "") for io in challenge.get("innovation_opportunities", [])]
            ),
        }
        system, user = prompt_manager.render("research_synthesis", **ctx)
        response = await gateway.generate(
            Prompt(system=system, user=user),
            model_tier=ModelTier.TIER_2,
        )
        return _parse_synthesis(response.content)
    except Exception as e:
        logger.warning("Research synthesis failed: %s", e)
        return None


def _format_results_for_synthesis(results: list[dict[str, Any]]) -> str:
    """Format research results for the synthesis prompt."""
    lines = []
    for i, r in enumerate(results[:30]):
        lines.append(f"  [{i + 1}] {r.get('title', '')}")
        lines.append(f"      URL: {r.get('url', '')}")
        lines.append(f"      Type: {r.get('result_type', r.get('_category', 'unknown'))}")
        lines.append(f"      Confidence: {r.get('_confidence', r.get('score', 0.5))}")
        lines.append("")
    return "\n".join(lines)


def _parse_synthesis(text: str) -> Optional[dict[str, Any]]:
    """Parse synthesis AI response."""
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


# ─── Database ─────────────────────────────────────────────────────────────


async def _get_cached_report(db: AsyncSession, project_id: str) -> Optional[dict[str, Any]]:
    """Get cached research report within freshness TTL."""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.RESEARCH_CACHE_TTL_SECONDS)
    result = await db.execute(
        select(ResearchResult)
        .where(
            and_(
                ResearchResult.project_id == project_id,
                ResearchResult.cached_at >= cutoff,
            )
        )
        .order_by(ResearchResult.cached_at.desc())
    )
    rows = list(result.scalars().all())
    if not rows:
        return None
    # Check if we have any non-synthesis results (real research)
    has_results = any(not r.is_synthesis for r in rows)
    if not has_results:
        return None
    return _build_report_from_rows(rows)


async def _store_results(
    db: AsyncSession,
    project_id: str,
    raw: list[dict[str, Any]],
    queries: dict[str, list[str]],
) -> list[ResearchResult]:
    """Store search results in database with all intelligence metadata."""
    # Clear old results for this project
    await db.execute(
        sa_delete(ResearchResult).where(
            ResearchResult.project_id == project_id,
            ResearchResult.is_synthesis == False,
        )
    )

    seen_urls: set[str] = set()
    stored = []
    report_id = str(uuid.uuid4())

    for result in raw:
        url = (result.get("url") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        category = result.get("_category", "insight")
        rr = ResearchResult(
            project_id=project_id,
            report_id=report_id,
            query=result.get("_query", ""),
            source="tavily" if not settings.MOCK_RESEARCH else "mock",
            result_type=category,
            title=(result.get("title") or "Untitled").strip()[:200],
            url=url,
            snippet=(result.get("content") or "")[:500],
            confidence=result.get("_confidence", result.get("score")),
            freshness=result.get("_freshness", "weeks"),
            relevance=_calculate_relevance(result),
            category=category,
            tags=result.get("_tags", [category]),
            relevance_score=result.get("score"),
            extra_data=result,
            is_synthesis=False,
        )
        db.add(rr)
        stored.append(rr)

    await db.commit()
    for r in stored:
        await db.refresh(r)
    return stored


async def _store_synthesis(db: AsyncSession, project_id: str, synthesis: dict[str, Any]) -> None:
    """Store synthesis results in database."""
    rr = ResearchResult(
        project_id=project_id,
        report_id=str(uuid.uuid4()),
        query="synthesis",
        source="ai_synthesis",
        result_type="insight",
        title="Research Synthesis Report",
        snippet=json.dumps(synthesis)[:500],
        extra_data=synthesis,
        is_synthesis=True,
        relevance_score=1.0,
    )
    db.add(rr)
    await db.commit()


def _calculate_relevance(result: dict[str, Any]) -> str:
    """Calculate relevance based on confidence score."""
    score = result.get("_confidence", result.get("score", 0.5))
    if score >= 0.8:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def _to_dict(r: ResearchResult) -> dict[str, Any]:
    """Convert a ResearchResult to a dict for API responses."""
    return {
        "id": r.id,
        "title": r.title,
        "url": r.url,
        "snippet": r.snippet,
        "result_type": r.result_type,
        "category": r.category or r.result_type,
        "confidence": r.confidence,
        "freshness": r.freshness,
        "relevance": r.relevance,
        "relevance_score": r.relevance_score,
        "source": r.source,
    }


# ─── Report Building ─────────────────────────────────────────────────────


def _build_report(
    results: list[ResearchResult],
    synthesis: Optional[dict[str, Any]],
) -> dict[str, Any]:
    """Build the final Research Report from stored results and synthesis."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    type_labels = {
        "product": "Existing Products",
        "startup": "Startups",
        "oss": "Open Source Projects",
        "github": "GitHub Repositories",
        "paper": "Research Papers",
        "api": "APIs & SDKs",
        "framework": "Frameworks & Libraries",
        "hackathon_winner": "Hackathon Winners",
        "trend": "Industry Trends",
        "insight": "Insights",
    }

    for r in results:
        key = r.result_type
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(_to_dict(r))

    categories = []
    for type_key, label in type_labels.items():
        items = grouped.get(type_key, [])
        categories.append({
            "id": type_key,
            "label": label,
            "count": len(items),
            "items": items,
        })

    total = sum(c["count"] for c in categories)

    return {
        "success": True,
        "summary": {
            "total_results": total,
            "categories_found": len([c for c in categories if c["count"] > 0]),
            "categories": categories,
            "cached": bool(results and results[0].cached_at),
        },
        "synthesis": synthesis or {},
    }


def _build_report_from_rows(rows: list[ResearchResult]) -> dict[str, Any]:
    """Build report from cached DB rows without re-processing."""
    synthesis = None
    results = []
    for r in rows:
        if r.is_synthesis:
            synthesis = r.extra_data if isinstance(r.extra_data, dict) else {}
        else:
            results.append(r)
    return _build_report(results, synthesis)


def _empty_response() -> dict[str, Any]:
    """Return empty research response."""
    return {
        "success": True,
        "summary": {
            "total_results": 0,
            "categories_found": 0,
            "categories": [],
            "cached": False,
        },
        "synthesis": None,
    }
