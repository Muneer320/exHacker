from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ResearchResult:
    query: str
    results: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    duration_ms: int = 0
    error: str | None = None


class ResearchProvider(ABC):
    name: str = ""

    @abstractmethod
    async def search(self, query: str, num_results: int = 5) -> ResearchResult:
        ...
