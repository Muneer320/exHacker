from __future__ import annotations

from typing import Any

from app.research.base import ResearchSource


class OpenSourceDiscovery(ResearchSource):
    @property
    def name(self) -> str:
        return "open_source"

    def search(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:  # noqa: ARG002
        results: list[dict[str, Any]] = []
        try:
            import httpx

            search_query = query.replace(" ", "+")
            url = f"https://api.github.com/search/repositories?q={search_query}&sort=stars&per_page=5"
            resp = httpx.get(url, timeout=10.0, headers={"Accept": "application/vnd.github.v3+json"})
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("items", [])[:5]:
                    results.append({
                        "name": item.get("full_name", ""),
                        "stars": item.get("stargazers_count", 0),
                        "license": item.get("license", {}).get("spdx_id", "") if item.get("license") else "",
                        "relevance_score": min(item.get("stargazers_count", 0) / 1000, 1.0),
                    })
        except Exception:
            pass

        return results
