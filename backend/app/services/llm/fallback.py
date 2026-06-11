from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.services.llm.service import LLMService


def generate_with_fallback(
    prompt: str,
    output_schema: type[BaseModel],
    **kwargs: Any,
) -> BaseModel:
    service = LLMService.get_instance()
    return service.generate_structured(prompt, output_schema, **kwargs)


def generate_text_with_fallback(prompt: str, **kwargs: Any) -> str:
    service = LLMService.get_instance()
    return service.generate_text(prompt, **kwargs)
