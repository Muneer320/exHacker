from __future__ import annotations

import json
from contextlib import suppress
from typing import Any

from pydantic import BaseModel

from app.core.config import settings
from app.services.llm.providers.base import LLMProvider
from app.services.llm.providers.gemini_provider import GeminiProvider
from app.services.llm.providers.groq_provider import GroqProvider
from app.services.llm.providers.ollama_provider import OllamaProvider
from app.services.llm.providers.openai_provider import OpenAIProvider


def _enrich_prompt(prompt: str, output_schema: type[BaseModel]) -> str:
    return (
        f"{prompt}\n\n"
        f"You MUST respond ONLY with valid JSON matching this exact structure:\n"
        f"{json.dumps(output_schema.model_json_schema(), indent=2)}"
    )


class LLMService:
    _instance: LLMService | None = None

    def __init__(self) -> None:
        self._chain: list[LLMProvider] = self._build_chain()

    @classmethod
    def get_instance(cls) -> LLMService:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _build_chain(self) -> list[LLMProvider]:
        provider_mode = settings.llm_provider.lower()

        configs: list[tuple[str, type[LLMProvider], str]] = [
            ("groq", GroqProvider, settings.groq_api_key),
            ("gemini", GeminiProvider, settings.gemini_api_key),
            ("openai", OpenAIProvider, settings.openai_api_key),
        ]

        if provider_mode == "ollama":
            try:
                return [OllamaProvider()]
            except Exception:
                return []

        if provider_mode != "auto":
            configs = [(n, c, k) for n, c, k in configs if n == provider_mode]

        providers: list[LLMProvider] = []
        for _name, provider_cls, api_key in configs:
            if not api_key:
                continue
            try:
                providers.append(provider_cls())
            except Exception:
                continue

        if provider_mode in ("auto",):
            with suppress(Exception):
                providers.append(OllamaProvider())

        return providers

    def generate_structured(
        self,
        prompt: str,
        output_schema: type[BaseModel],
        **kwargs: Any,
    ) -> BaseModel:
        enriched = _enrich_prompt(prompt, output_schema)
        errors: list[str] = []
        for provider in self._chain:
            try:
                text = provider.generate_text(enriched, **kwargs)
                return output_schema.model_validate_json(text)
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")
                continue
        msg = f"All providers failed. Errors: {'; '.join(errors)}"
        raise RuntimeError(msg)

    def generate_text(self, prompt: str, **kwargs: Any) -> str:
        errors: list[str] = []
        for provider in self._chain:
            try:
                return provider.generate_text(prompt, **kwargs)
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")
                continue
        msg = f"All providers failed. Errors: {'; '.join(errors)}"
        raise RuntimeError(msg)

    def get_active_chain(self) -> list[str]:
        return [p.name for p in self._chain]
