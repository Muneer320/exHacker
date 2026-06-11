from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.core.config import settings
from app.services.llm.providers.base import LLMProvider
from app.services.llm.providers.gemini_provider import GeminiProvider
from app.services.llm.providers.groq_provider import GroqProvider
from app.services.llm.providers.ollama_provider import OllamaProvider
from app.services.llm.providers.openai_provider import OpenAIProvider


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
        providers: list[LLMProvider] = []

        provider_mode = settings.llm_provider.lower()

        if provider_mode == "groq":
            providers = [GroqProvider()]
        elif provider_mode == "gemini":
            providers = [GeminiProvider()]
        elif provider_mode == "ollama":
            providers = [OllamaProvider()]
        elif provider_mode == "openai":
            providers = [OpenAIProvider()]
        else:
            providers = [
                GroqProvider(),
                GeminiProvider(),
                OllamaProvider(),
                OpenAIProvider(),
            ]

        return [p for p in providers if self._is_configured(p)]

    def _is_configured(self, provider: LLMProvider) -> bool:
        name = provider.name
        if name == "groq":
            return bool(settings.groq_api_key)
        if name == "gemini":
            return bool(settings.gemini_api_key)
        if name == "ollama":
            return True
        if name == "openai":
            return bool(settings.openai_api_key)
        return False

    def generate_structured(
        self,
        prompt: str,
        output_schema: type[BaseModel],
        **kwargs: Any,
    ) -> BaseModel:
        errors: list[str] = []
        for provider in self._chain:
            try:
                return provider.generate_structured(prompt, output_schema, **kwargs)
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
