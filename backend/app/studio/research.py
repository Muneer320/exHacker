"""Bounded live search with project-local caching and explicit partial failures."""

import asyncio
import hashlib
import ipaddress
from datetime import timedelta
from urllib.parse import urlparse

import httpx
from sqlalchemy import select, update

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.studio.ai import StudioError
from app.studio.inference import reject_secrets
from app.studio.models import Artifact, Project, now


def public_url(value: str) -> bool:
    try:
        url = urlparse(value)
        if (
            url.scheme not in ("http", "https")
            or not url.hostname
            or url.username
            or url.password
        ):
            return False
        host = url.hostname.lower()
        if host in ("localhost", "example.com", "example.org") or host.endswith(
            (".local", ".internal")
        ):
            return False
        try:
            return ipaddress.ip_address(host).is_global
        except ValueError:
            return "." in host
    except ValueError:
        return False


async def search(project_id: str, queries: list[str]) -> dict:
    queries = list(dict.fromkeys(q.strip()[:350] for q in queries if q.strip()))[:6]
    if not settings.TAVILY_API_KEY:
        raise StudioError(
            "Live research requires TAVILY_API_KEY on the backend. No sample research will be substituted.",
            503,
        )
    cache_key = hashlib.sha256("\n".join(sorted(queries)).encode()).hexdigest()
    async with AsyncSessionLocal() as db:
        cached = await db.scalar(
            select(Artifact)
            .where(
                Artifact.project_id == project_id,
                Artifact.kind == "search_cache",
                Artifact.content["key"].as_string() == cache_key,
                Artifact.created_at > now() - timedelta(hours=24),
            )
            .order_by(Artifact.created_at.desc())
        )
        if cached:
            return {**cached.content["report"], "cached": True}
        reservation = await db.execute(
            update(Project)
            .where(
                Project.id == project_id,
                Project.search_count + len(queries) <= settings.STUDIO_SEARCH_LIMIT,
            )
            .values(search_count=Project.search_count + len(queries))
        )
        if reservation.rowcount != 1:
            raise StudioError("This project's search budget is exhausted.", 429)
        await db.commit()

    async with httpx.AsyncClient(timeout=25) as client:

        async def one(query):
            try:
                response = await client.post(
                    "https://api.tavily.com/search",
                    headers={"Authorization": f"Bearer {settings.TAVILY_API_KEY}"},
                    json={
                        "query": query,
                        "search_depth": "advanced",
                        "max_results": 4,
                        "include_answer": False,
                        "include_raw_content": False,
                    },
                )
                response.raise_for_status()
                return query, response.json().get("results", []), None
            except (httpx.HTTPError, ValueError) as exc:
                return (
                    query,
                    [],
                    f"Search failed ({getattr(getattr(exc, 'response', None), 'status_code', 'network error')})",
                )

        responses = await asyncio.gather(*(one(q) for q in queries))
    sources, warnings, seen = [], [], set()
    for query, results, error in responses:
        if error:
            warnings.append(f"{query}: {error}")
        for result in results:
            url = result.get("url", "")
            if not public_url(url) or url in seen:
                continue
            seen.add(url)
            sources.append(
                {
                    "id": "src-" + hashlib.sha256(url.encode()).hexdigest()[:12],
                    "url": url,
                    "title": str(result.get("title", url))[:300],
                    "snippet": str(result.get("content", ""))[:1800],
                    "query": query,
                    "relevance": result.get("score"),
                    "retrieved_at": now().isoformat() + "Z",
                }
            )
    if not sources:
        raise StudioError(
            "Research returned no usable sources. Check Tavily access or try a more specific idea. Existing ideas are preserved.",
            502,
        )
    report = {
        "sources": sources,
        "queries": queries,
        "warnings": warnings,
        "cached": False,
    }
    reject_secrets(report)
    if not warnings:
        async with AsyncSessionLocal() as db:
            db.add(
                Artifact(
                    project_id=project_id,
                    revision=0,
                    kind="search_cache",
                    content={"key": cache_key, "report": report},
                )
            )
            await db.commit()
    return report
