import logging
from typing import Any

from app.core.config import settings
from app.services.llm.cost_tracker import CostTracker
from app.services.llm.fallback import FallbackChain
from app.services.llm.providers import (
    GeminiProvider,
    GroqProvider,
    OllamaProvider,
    OpenAIProvider,
)
from app.services.llm.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        self._cost_tracker = CostTracker()
        self._fallback = FallbackChain(self._cost_tracker)
        self._providers: list[LLMProvider] | None = None
        self._extras: dict[str, Any] = {}

    def set_extras(self, extras: dict[str, Any]) -> None:
        self._extras = extras

    def get_providers(self) -> list[LLMProvider]:
        if self._providers is not None:
            return self._providers

        api_keys = {
            "groq": settings.GROQ_API_KEY,
            "gemini": settings.GEMINI_API_KEY,
            "ollama": "ollama",
            "openai": settings.OPENAI_API_KEY,
        }

        priority: list[type[LLMProvider]] = [
            GroqProvider,
            GeminiProvider,
            OllamaProvider,
            OpenAIProvider,
        ]

        providers: list[LLMProvider] = []
        for provider_cls in priority:
            name = provider_cls.name
            key = api_keys.get(name)
            if key:
                try:
                    if name == "ollama":
                        from app.services.llm.providers.base import ProviderConfig
                        providers.append(OllamaProvider(ProviderConfig(
                            api_key="",
                            base_url=settings.OLLAMA_BASE_URL,
                            model=settings.OLLAMA_MODEL,
                        )))
                    else:
                        providers.append(self._create_provider(provider_cls, key))
                except Exception as e:
                    logger.warning("Failed to create provider %s: %s", name, e)

        self._providers = providers
        return providers

    def get_cost_tracker(self) -> CostTracker:
        return self._cost_tracker

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        agent_name: str = "unknown",
    ) -> dict[str, Any]:
        providers = self.get_providers()
        return await self._fallback.execute_with_fallback(
            providers, system_prompt, user_prompt, agent_name,
        )

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: type,
        agent_name: str = "unknown",
    ) -> dict[str, Any]:
        providers = self.get_providers()
        return await self._fallback.execute_structured_with_fallback(
            providers, system_prompt, user_prompt, response_format, agent_name,
        )

    def _create_provider(
        self, provider_cls: type[LLMProvider], api_key: str
    ) -> LLMProvider:
        from app.services.llm.providers.base import ProviderConfig
        config = ProviderConfig(api_key=api_key)
        return provider_cls(config)

    def reset(self) -> None:
        self._cost_tracker.reset()
        self._providers = None

    def summary(self) -> dict[str, Any]:
        return self._cost_tracker.summary()
