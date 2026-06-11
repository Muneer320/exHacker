from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ResearchSource(ABC):
    @abstractmethod
    def search(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...
