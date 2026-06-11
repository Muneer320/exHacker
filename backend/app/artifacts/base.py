from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ArtifactGenerator(ABC):
    @abstractmethod
    def generate(self, state: dict[str, Any]) -> str:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...
