import time

import httpx
import structlog

from app.research.base import ResearchProvider, ResearchResult

logger = structlog.get_logger(__name__)


class GitHubSearchProvider(ResearchProvider):
    name = "github_search"

    def __init__(
        self,
        token: str | None = None,
        timeout: float = 15.0,
    ) -> None:
        self.token = token
        self.timeout = timeout

    async def search(self, query: str, num_results: int = 5) -> ResearchResult:
        start = time.monotonic()
        logger.debug("github_search_started", query=query, num_results=num_results)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers: dict[str, str] = {
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "exHacker/0.1.0",
                }
                if self.token:
                    headers["Authorization"] = f"Bearer {self.token}"

                params: dict[str, str | int] = {
                    "q": query,
                    "per_page": min(num_results, 100),
                    "sort": "stars",
                    "order": "desc",
                }

                response = await client.get(
                    "https://api.github.com/search/repositories",
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

            items = (data.get("items") or [])[:num_results]
            results = []
            sources = []

            for repo in items:
                full_name = repo.get("full_name", "")
                description = repo.get("description") or ""
                stars = repo.get("stargazers_count", 0)
                language = repo.get("language") or "Unknown"
                url = repo.get("html_url", "")

                results.append(
                    f"{full_name} - {description} [{language}, {stars} stars]"
                )
                sources.append(url)

            elapsed = int((time.monotonic() - start) * 1000)
            logger.info(
                "github_search_completed",
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
            logger.warning("github_search_timeout", query=query, duration_ms=elapsed)
            return ResearchResult(
                query=query,
                duration_ms=elapsed,
                error="GitHub API request timed out",
            )
        except httpx.HTTPStatusError as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            logger.error(
                "github_search_http_error",
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
            logger.exception("github_search_failed", query=query, duration_ms=elapsed)
            return ResearchResult(
                query=query,
                duration_ms=elapsed,
                error=str(exc),
            )

    async def search_repos(self, query: str) -> list[dict]:
        result = await self.search(query, num_results=10)
        repos = []

        for title, url in zip(result.results, result.sources):
            parts = title.split(" - ", 1)
            full_name = parts[0] if parts else ""
            description = parts[1] if len(parts) > 1 else ""
            lang_stars = ""
            if "[" in description and description.endswith("]"):
                description, lang_stars = description.rsplit(" [", 1)
                lang_stars = lang_stars.rstrip("]")

            repos.append(
                {
                    "full_name": full_name,
                    "description": description.strip(),
                    "url": url,
                    "language": lang_stars.split(",")[0].strip() if lang_stars else "Unknown",
                    "stars": int(lang_stars.split(",")[-1].replace("stars", "").strip())
                    if lang_stars and "stars" in lang_stars
                    else 0,
                }
            )

        return repos
