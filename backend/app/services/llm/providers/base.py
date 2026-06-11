from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class LLMProvider(ABC):
    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        output_schema: type[BaseModel],
        **kwargs: Any,
    ) -> BaseModel:
        ...

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...
