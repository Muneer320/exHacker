import time

import httpx
import structlog

from app.research.base import ResearchProvider, ResearchResult

logger = structlog.get_logger(__name__)


class WebSearchProvider(ResearchProvider):
    name = "web_search"

    def __init__(
        self,
        api_url: str = "https://api.duckduckgo.com",
        api_key: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    async def search(self, query: str, num_results: int = 5) -> ResearchResult:
        start = time.monotonic()
        logger.debug("web_search_started", query=query, num_results=num_results)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params: dict[str, str | int] = {
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                    "skip_disambig": 1,
                }
                headers: dict[str, str] = {}
                if self.api_key:
                    headers["Ocp-Apim-Subscription-Key"] = self.api_key

                response = await client.get(
                    f"{self.api_url}/",
                    params=params,
                    headers=headers or None,
                )
                response.raise_for_status()
                data = response.json()

            results: list[str] = []
            sources: list[str] = []

            for item in (data.get("RelatedTopics") or [])[:num_results]:
                if "Text" in item:
                    results.append(item["Text"])
                    sources.append(item.get("FirstURL", ""))

            if not results:
                for item in (data.get("Results") or [])[:num_results]:
                    if "Text" in item:
                        results.append(item["Text"])
                        sources.append(item.get("FirstURL", ""))

            elapsed = int((time.monotonic() - start) * 1000)
            logger.info(
                "web_search_completed",
                query=query,
                result_count=len(results),
                duration_ms=elapsed,
            )
            return ResearchResult(
                query=query,
                results=results,
                sources=sources,
                duration_ms=elapsed,
            )

        except httpx.TimeoutException:
            elapsed = int((time.monotonic() - start) * 1000)
            logger.warning("web_search_timeout", query=query, duration_ms=elapsed)
            return ResearchResult(
                query=query,
                duration_ms=elapsed,
                error="Search request timed out",
            )
        except httpx.HTTPStatusError as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            logger.error(
                "web_search_http_error",
                query=query,
                status_code=exc.response.status_code,
                duration_ms=elapsed,
            )
            return ResearchResult(
                query=query,
                duration_ms=elapsed,
                error=f"HTTP {exc.response.status_code}: {exc.response.text[:200]}",
            )
        except Exception as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            logger.exception("web_search_failed", query=query, duration_ms=elapsed)
            return ResearchResult(
                query=query,
                duration_ms=elapsed,
                error=str(exc),
            )
