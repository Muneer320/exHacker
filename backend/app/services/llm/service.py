import logging
import os
from typing import Any

import httpx

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
        # Always recompute providers to reflect latest environment variables
        self._providers = None

        # Gather API keys — prefer pydantic-settings (reads .env), fall back to
        # os.getenv for cases where the variable is only in the OS environment.
        def _key(name: str) -> str:
            val = getattr(settings, f"{name}_api_key", None) or os.getenv(
                f"{name.upper()}_API_KEY", ""
            )
            return (val or "").strip()

        api_keys = {
            "groq": _key("groq"),
            "gemini": _key("gemini"),
            "openai": _key("openai"),
            "ollama": None,
        }
        logger.info(
            "LLM Provider keys present: %s",
            {k: bool(v) for k, v in api_keys.items()},
        )

        # Determine priority order; Ollama will be included only after health‑check
        priority: list[type[LLMProvider]] = [
            GroqProvider,
            GeminiProvider,
            OpenAIProvider,
        ]

        providers: list[LLMProvider] = []
        # Initialize cloud providers if their keys are set
        for provider_cls in priority:
            name = provider_cls.name
            key = api_keys.get(name)
            if key:
                providers.append(self._create_provider(provider_cls, key))
                logger.info(
                    "Initialized LLM provider %s (model=%s)",
                    name,
                    getattr(settings, f"{name}_model", "default"),
                )
            else:
                logger.warning("No API key configured for %s — skipping", name)

        # Optionally include Ollama after a lightweight health‑check
        enable_ollama = os.getenv("ENABLE_OLLAMA", "false").lower() == "true"
        if enable_ollama:
            try:
                health_url = f"{settings.ollama_base_url}/api/tags"
                logger.debug("Checking Ollama health at %s", health_url)
                resp = httpx.get(health_url, timeout=2.0)
                if resp.status_code == 200:
                    from app.services.llm.providers.base import ProviderConfig
                    providers.append(OllamaProvider(ProviderConfig(
                        api_key="",
                        base_url=settings.ollama_base_url,
                        model=settings.ollama_model,
                    )))
                    logger.info("Ollama provider added after successful health‑check")
                else:
                    logger.warning("Ollama health‑check failed with status %s", resp.status_code)
            except Exception as e:
                logger.error("Error during Ollama health‑check: %s", e)
        else:
            logger.debug("Ollama provider not enabled (ENABLE_OLLAMA=false)")

        self._providers = providers
        if not providers:
            logger.error("No LLM providers were configured. Check API keys and ENABLE_OLLAMA flag.")
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

        provider_name = provider_cls.name
        # Pull model and base_url from settings (e.g. groq_model, groq_base_url)
        model = getattr(settings, f"{provider_name}_model", "") or ""
        base_url = getattr(settings, f"{provider_name}_base_url", None)

        config = ProviderConfig(
            api_key=api_key,
            model=model,
            base_url=base_url,
            temperature=0.7,
            max_tokens=4096,
        )
        logger.info(
            "Provider config for %s: model=%s, base_url=%s",
            provider_name, model or "(default)", base_url or "(default)",
        )
        return provider_cls(config)

    def reset(self) -> None:
        self._cost_tracker.reset()
        self._providers = None

    def summary(self) -> dict[str, Any]:
        return self._cost_tracker.summary()
