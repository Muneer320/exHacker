from __future__ import annotations

from typing import Any

from langchain_ollama import ChatOllama
from pydantic import BaseModel

from app.core.config import settings
from app.services.llm.providers.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self) -> None:
        self._llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0.7,
        )

    @property
    def name(self) -> str:
        return "ollama"

    def generate_structured(
        self,
        prompt: str,
        output_schema: type[BaseModel],
        **kwargs: Any,  # noqa: ARG002
    ) -> BaseModel:
        text = self.generate_text(prompt)
        return output_schema.model_validate_json(text)

    def generate_text(self, prompt: str, **kwargs: Any) -> str:  # noqa: ARG002
        return str(self._llm.invoke(prompt).content)
