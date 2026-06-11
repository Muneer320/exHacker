from __future__ import annotations

from typing import Any

from app.research.base import ResearchSource


class CompetitorSearch(ResearchSource):
    @property
    def name(self) -> str:
        return "competitor"

    def search(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:  # noqa: ARG002
        results: list[dict[str, Any]] = []
        try:
            import httpx

            search_url = f"https://api.duckduckgo.com/?q={query}+competitor+startup&format=json"
            resp = httpx.get(search_url, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                for topic in data.get("RelatedTopics", [])[:5]:
                    text = topic.get("Text", "") if isinstance(topic, dict) else ""
                    if text:
                        results.append({
                            "name": text.split(" - ")[0] if " - " in text else text[:50],
                            "description": text,
                            "website": topic.get("FirstURL", "") if isinstance(topic, dict) else "",
                            "similarity_score": 0.5,
                        })
        except Exception:
            pass

        return results
