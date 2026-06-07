import structlog

from app.research.base import ResearchProvider, ResearchResult
from app.research.web_search import WebSearchProvider

logger = structlog.get_logger(__name__)


class APISearchProvider:
    def __init__(self, web_provider: ResearchProvider | None = None) -> None:
        self._web = web_provider or WebSearchProvider()

    async def find_apis(self, requirements: list[str]) -> list[dict]:
        logger.debug("api_search_started", requirements=requirements)

        query = " ".join(requirements)
        queries = [
            f"best API for {query}",
            f"{query} API integration",
            f"top {query} APIs",
        ]

        all_results: list[dict] = []
        seen_urls: set[str] = set()

        for q in queries:
            result: ResearchResult = await self._web.search(q, num_results=5)

            if result.error:
                logger.warning("api_search_query_failed", query=q, error=result.error)
                continue

            for title, url in zip(result.results, result.sources):
                if url in seen_urls:
                    continue
                if not url:
                    continue
                seen_urls.add(url)

                name = title.split(" – ")[0].split(" - ")[0].split(" | ")[0].strip()

                all_results.append(
                    {
                        "name": name,
                        "description": title,
                        "url": url,
                        "category": _categorize_api(title, requirements),
                    }
                )

        logger.info(
            "api_search_completed",
            requirements=requirements,
            apis_found=len(all_results),
        )
        return all_results


def _categorize_api(title: str, requirements: list[str]) -> str:
    title_lower = title.lower()
    for req in requirements:
        req_lower = req.lower()
        if req_lower in title_lower:
            return req
    return "general"
