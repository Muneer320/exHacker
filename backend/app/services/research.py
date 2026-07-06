"""Research Service — orchestrates web research for project ideas.

Pipeline:
  1. Generate search queries from the idea (AI Gateway, Tier 1)
  2. Execute queries via Tavily/SerpAPI (deterministic)
  3. Normalize and deduplicate results
  4. Cache results in the database
  5. Return structured research data

SDPD: Research query generation uses AI (Tier 1 — cheap model).
      Everything else is deterministic software.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from httpx import AsyncClient
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.gateway import Prompt, ModelTier, gateway
from app.core.config import settings
from app.core.exceptions import ResearchFailedError
from app.models.research import ResearchResult, ResearchResultType
from app.services.project import get_project

logger = logging.getLogger(__name__)

TAVILY_API_URL = "https://api.tavily.com/search"
HTTP_TIMEOUT = 15  # seconds

# ─── Public API ─────────────────────────────────────────────────────────────


async def run_research(
    db: AsyncSession,
    project_id: str,
) -> list[dict[str, Any]]:
    """Run the full research pipeline for a project.

    1. Checks for cached results (24h freshness)
    2. Generates search queries via AI
    3. Executes searches via Tavily or mock
    4. Normalizes, deduplicates, and stores results
    5. Returns structured research data

    Args:
        db: Database session.
        project_id: The project to research.

    Returns:
        List of research result dicts with title, url, snippet, type.
    """
    # 1. Check cache
    cached = await _get_cached_results(db, project_id)
    if cached:
        logger.info("Using cached research for project %s (%d results)", project_id, len(cached))
        return cached

    # 2. Get the project to know what to research
    project = await get_project(db, project_id)

    # 3. Generate search queries via AI Gateway (Tier 1 — cheap model)
    queries = await _generate_queries(project.idea)
    if not queries:
        queries = _default_queries(project.idea)
        logger.info("AI query generation returned empty, using defaults for project %s", project_id)

    logger.info("Researching project %s with %d queries: %s", project_id, len(queries), queries)

    # 4. Execute searches
    all_raw: list[dict[str, Any]] = []
    for query in queries:
        if settings.MOCK_RESEARCH:
            results = _mock_search(query)
        else:
            results = await _tavily_search(query)
        all_raw.extend(results)

    # 5. Normalize and deduplicate
    normalized = _normalize_results(all_raw, project_id, queries)

    # 6. Store in database
    await _store_results(db, normalized)

    # 7. Return structured data
    return _to_response(normalized)


async def get_research(db: AsyncSession, project_id: str) -> dict[str, Any]:
    """Get research results for a project. Returns cached results or empty structure."""
    cached = await _get_cached_results(db, project_id)
    if cached:
        return _to_response(cached)
    return _empty_response()


async def refresh_research(db: AsyncSession, project_id: str) -> list[dict[str, Any]]:
    """Force-refresh research for a project. Clears cache first."""
    await _clear_cache(db, project_id)
    return await run_research(db, project_id)


# ─── AI Query Generation (Tier 1 — cheap model) ──────────────────────────


async def _generate_queries(idea: str) -> list[str]:
    """Generate search queries from a project idea using the AI Gateway."""
    try:
        prompt = Prompt(
            system=(
                "You are a research assistant. Generate specific search queries "
                "to research competitors, APIs, and open-source projects for a given idea. "
                "Return ONLY a JSON array of strings, max 5 queries."
            ),
            user=f"Project idea: {idea}\n\nGenerate 3-5 research queries as a JSON array.",
        )
        response = await gateway.generate(prompt, model_tier=ModelTier.TIER_1)

        text = response.content.strip()
        # Parse JSON array from response
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        if text.startswith("["):
            queries = json.loads(text)
        else:
            # Try to find JSON array within text
            start = text.find("[")
            end = text.rfind("]")
            if start != -1 and end != -1:
                queries = json.loads(text[start:end + 1])
            else:
                logger.warning("Could not parse AI response as JSON array: %s", text[:100])
                return []

        if isinstance(queries, list) and all(isinstance(q, str) for q in queries):
            return queries[:5]
        return []
    except Exception as e:
        logger.warning("AI query generation failed: %s", e)
        return []


def _default_queries(idea: str) -> list[str]:
    """Fallback queries when AI generation fails."""
    words = idea.split()[:4]
    topic = " ".join(words) if words else "this project"
    return [
        f"competitors for {topic}",
        f"alternatives to {topic}",
        f"open source {topic}",
        f"APIs for {topic}",
        f"{topic} market overview",
    ]


# ─── Search Execution (Deterministic) ────────────────────────────────────


async def _tavily_search(query: str) -> list[dict[str, Any]]:
    """Execute a search query via Tavily API."""
    api_key = settings.TAVILY_API_KEY
    if not api_key:
        logger.warning("TAVILY_API_KEY not set, returning mock results for query: %s", query)
        return _mock_search(query)

    try:
        async with AsyncClient(timeout=HTTP_TIMEOUT) as client:
            response = await client.post(
                TAVILY_API_URL,
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": 5,
                    "include_answer": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
    except Exception as e:
        logger.error("Tavily search failed for query '%s': %s", query, e)
        return []


def _mock_search(query: str) -> list[dict[str, Any]]:
    """Return mock search results when MOCK_RESEARCH is enabled."""
    words = query.split()
    topic = " ".join(words[-3:]) if len(words) > 3 else query

    results = []
    for i, name in enumerate(
        [f"Competitor {j + 1}" for j in range(3)]
    ):
        results.append({
            "title": f"{name} — {topic[:40]}",
            "url": f"https://example.com/{name.lower().replace(' ', '-')}",
            "content": f"This is a mock result for '{query}'. "
                       f"Represents {name} in the {topic[:30]} space. "
                       f"Mock data — replace with real search results.",
            "score": max(0.5, 0.9 - i * 0.15),
        })
    return results


# ─── Result Processing (Deterministic) ───────────────────────────────────


def _classify_result(result: dict[str, Any], query: str) -> str:
    """Classify a result as competitor, api, oss, or insight based on the query and content."""
    query_lower = query.lower()
    title_lower = (result.get("title", "") or "").lower()
    content_lower = (result.get("content", "") or "").lower()
    combined = query_lower + title_lower + content_lower

    if any(w in combined for w in ["api ", "api-", "sdk", "integration", "rest"]):
        return ResearchResultType.API.value
    if any(w in combined for w in ["open source", "github", "gitlab"]):
        return ResearchResultType.OSS.value
    if any(w in combined for w in ["market", "trend", "statistics", "survey"]):
        return ResearchResultType.INSIGHT.value
    return ResearchResultType.COMPETITOR.value


def _normalize_results(
    raw: list[dict[str, Any]],
    project_id: str,
    queries: list[str],
) -> list[ResearchResult]:
    """Normalize raw search results and deduplicate by URL."""
    seen_urls: set[str] = set()
    normalized: list[ResearchResult] = []

    for result in raw:
        url = (result.get("url") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        # Determine which query produced this result
        query = queries[0]  # default to first query
        normalized.append(ResearchResult(
            project_id=project_id,
            query=query,
            source="tavily" if not settings.MOCK_RESEARCH else "mock",
            result_type=_classify_result(result, query),
            title=(result.get("title") or "Untitled").strip(),
            url=url,
            snippet=(result.get("content") or "")[:500],
            relevance_score=result.get("score"),
            extra_data={"query": query},
        ))

    return normalized


# ─── Database (Caching) ────────────────────────────────────────────────────


async def _get_cached_results(
    db: AsyncSession, project_id: str,
) -> list[ResearchResult]:
    """Get cached research results within freshness TTL."""
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.RESEARCH_CACHE_TTL_SECONDS)
    result = await db.execute(
        select(ResearchResult)
        .where(
            and_(
                ResearchResult.project_id == project_id,
                ResearchResult.cached_at >= cutoff,
            )
        )
        .order_by(ResearchResult.relevance_score.desc().nullslast())
    )
    return list(result.scalars().all())


async def _store_results(db: AsyncSession, results: list[ResearchResult]) -> None:
    """Store research results in the database."""
    for result in results:
        db.add(result)
    await db.commit()


async def _clear_cache(db: AsyncSession, project_id: str) -> None:
    """Clear cached research results for a project."""
    cached = await db.execute(
        select(ResearchResult).where(ResearchResult.project_id == project_id)
    )
    for row in cached.scalars().all():
        await db.delete(row)
    await db.commit()


# ─── Response Formatting ─────────────────────────────────────────────────


def _to_response(results: list[ResearchResult]) -> dict[str, Any]:
    """Format research results into a structured API response."""
    grouped: dict[str, list[dict[str, Any]]] = {
        "competitors": [],
        "apis": [],
        "oss_projects": [],
        "insights": [],
    }

    type_map = {
        ResearchResultType.COMPETITOR.value: "competitors",
        ResearchResultType.API.value: "apis",
        ResearchResultType.OSS.value: "oss_projects",
        ResearchResultType.INSIGHT.value: "insights",
    }

    for r in results:
        key = type_map.get(r.result_type, "competitors")
        entry = {
            "title": r.title,
            "url": r.url,
            "snippet": r.snippet,
            "relevance_score": r.relevance_score,
            "result_type": r.result_type,
        }
        grouped[key].append(entry)

    return {
        "summary": {
            "total_results": len(results),
            "competitors_found": len(grouped["competitors"]),
            "apis_found": len(grouped["apis"]),
            "oss_found": len(grouped["oss_projects"]),
            "insights_found": len(grouped["insights"]),
            "cached": True if results and results[0].cached_at else False,
        },
        **grouped,
    }


def _empty_response() -> dict[str, Any]:
    """Return an empty research response."""
    return {
        "summary": {
            "total_results": 0,
            "competitors_found": 0,
            "apis_found": 0,
            "oss_found": 0,
            "insights_found": 0,
            "cached": False,
        },
        "competitors": [],
        "apis": [],
        "oss_projects": [],
        "insights": [],
    }
