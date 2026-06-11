from __future__ import annotations

from typing import Any, cast

from langchain_groq import ChatGroq
from pydantic import BaseModel, SecretStr

from app.core.config import settings
from app.services.llm.providers.base import LLMProvider


class GroqProvider(LLMProvider):
    def __init__(self) -> None:
        self._llm = ChatGroq(
            model=settings.groq_model,
            api_key=SecretStr(settings.groq_api_key) if settings.groq_api_key else None,
            temperature=0.7,
            max_tokens=4096,
        )

    @property
    def name(self) -> str:
        return "groq"

    def generate_structured(
        self,
        prompt: str,
        output_schema: type[BaseModel],
        **kwargs: Any,  # noqa: ARG002
    ) -> BaseModel:
        result = self._llm.with_structured_output(output_schema).invoke(prompt)
        return cast(BaseModel, result)

    def generate_text(self, prompt: str, **kwargs: Any) -> str:  # noqa: ARG002
        return str(self._llm.invoke(prompt).content)
