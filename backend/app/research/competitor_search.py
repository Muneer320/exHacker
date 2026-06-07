import structlog

from app.research.base import ResearchProvider, ResearchResult
from app.research.web_search import WebSearchProvider

logger = structlog.get_logger(__name__)


class CompetitorSearchProvider:
    def __init__(self, web_provider: ResearchProvider | None = None) -> None:
        self._web = web_provider or WebSearchProvider()

    async def find_competitors(self, idea_description: str) -> list[dict]:
        logger.debug("competitor_search_started", idea=idea_description)

        queries = [
            f"competitors {idea_description}",
            f"alternatives to {idea_description}",
            f"companies building {idea_description}",
            f"{idea_description} market landscape",
        ]

        all_results: list[dict] = []
        seen: set[str] = set()

        for query in queries:
            result: ResearchResult = await self._web.search(query, num_results=5)

            if result.error:
                logger.warning(
                    "competitor_search_query_failed",
                    query=query,
                    error=result.error,
                )
                continue

            for i, (title, url) in enumerate(zip(result.results, result.sources)):
                if not title or title in seen:
                    continue
                seen.add(title)
                all_results.append(
                    {
                        "name": title.split(" - ")[0].split(" | ")[0].strip(),
                        "description": title,
                        "source": url or f"Result {i + 1}",
                        "relevance": max(10 - i * 2, 1),
                    }
                )

        logger.info(
            "competitor_search_completed",
            idea=idea_description,
            competitors_found=len(all_results),
        )
        return all_results
