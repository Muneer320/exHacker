from __future__ import annotations

from typing import Any

from app.research.api_discovery import ApiDiscovery
from app.research.base import ResearchSource
from app.research.competitor_search import CompetitorSearch
from app.research.open_source_discovery import OpenSourceDiscovery


class ResearchCoordinator:
    def __init__(self) -> None:
        self._sources: list[ResearchSource] = [
            CompetitorSearch(),
            ApiDiscovery(),
            OpenSourceDiscovery(),
        ]

    def research(self, query: str) -> dict[str, Any]:
        results: dict[str, list[dict[str, Any]]] = {}
        for source in self._sources:
            try:
                results[source.name] = source.search(query)
            except Exception:
                results[source.name] = []
        return results

    def score_novelty(self, research_results: dict[str, list[dict[str, Any]]]) -> int:
        competitor_density = len(research_results.get("competitor", []))
        open_source_density = len(research_results.get("open_source", []))

        score = 100
        score -= competitor_density * 15
        score -= open_source_density * 10
        return max(0, min(100, score))

    def score_feasibility(self, research_results: dict[str, list[dict[str, Any]]]) -> int:
        apis_found = len(research_results.get("api_discovery", []))
        open_source_found = len(research_results.get("open_source", []))

        score = 50
        score += apis_found * 10
        score += open_source_found * 5
        return max(0, min(100, score))


_research_coordinator = ResearchCoordinator()


def get_research_coordinator() -> ResearchCoordinator:
    return _research_coordinator
