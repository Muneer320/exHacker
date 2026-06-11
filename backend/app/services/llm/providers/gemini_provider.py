from __future__ import annotations

from typing import Any, cast

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from app.core.config import settings
from app.services.llm.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self) -> None:
        self._llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            api_key=settings.gemini_api_key,
            temperature=0.7,
        )

    @property
    def name(self) -> str:
        return "gemini"

    def generate_structured(
        self,
        prompt: str,
        output_schema: type[BaseModel],
        **kwargs: Any,  # noqa: ARG002
    ) -> BaseModel:
        try:
            result = self._llm.with_structured_output(output_schema, method="json_mode").invoke(prompt)
            return cast(BaseModel, result)
        except Exception:
            text = self.generate_text(
                f"{prompt}\n\nRespond ONLY with valid JSON conforming to: {output_schema.model_json_schema()}"
            )
            return output_schema.model_validate_json(text)

    def generate_text(self, prompt: str, **kwargs: Any) -> str:  # noqa: ARG002
        return str(self._llm.invoke(prompt).content)
