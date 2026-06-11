from __future__ import annotations

from typing import Any, cast

from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.config import settings
from app.services.llm.providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,  # type: ignore[arg-type]
            temperature=settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,  # type: ignore[call-arg]
        )

    @property
    def name(self) -> str:
        return "openai"

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
