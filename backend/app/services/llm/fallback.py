import logging
from typing import Any

from app.services.llm.cost_tracker import CostTracker
from app.services.llm.providers.base import LLMProvider
from app.services.llm.providers.gemini_provider import GeminiProvider
from app.services.llm.providers.groq_provider import GroqProvider
from app.services.llm.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class FallbackChain:
    def __init__(self, cost_tracker: CostTracker) -> None:
        self._cost_tracker = cost_tracker

    def create_chain(self, api_keys: dict[str, str | None]) -> list[LLMProvider]:
        from app.services.llm.providers.base import ProviderConfig

        priority: list[type[LLMProvider]] = [
            GroqProvider,
            GeminiProvider,
            OpenAIProvider,
        ]
        providers: list[LLMProvider] = []
        for provider_cls in priority:
            name = provider_cls.name
            key = api_keys.get(name)
            if key:
                providers.append(provider_cls(ProviderConfig(api_key=key)))
        return providers

    async def execute_with_fallback(
        self,
        providers: list[LLMProvider],
        system_prompt: str,
        user_prompt: str,
        agent_name: str = "",
    ) -> dict[str, Any]:
        if not providers:
            logger.error(
                "No LLM providers available for %s. Check API keys.",
                agent_name,
            )
            raise RuntimeError(
                f"No LLM providers available for {agent_name}. "
                "Check API keys are configured correctly in .env file."
            )

        last_error: Exception | None = None
        logger.info(
            "Fallback: trying %d provider(s) for %s: %s",
            len(providers), agent_name, [p.name for p in providers],
        )
        for idx, provider in enumerate(providers, 1):
            try:
                logger.info(
                    "Fallback attempt %d/%d: %s for %s",
                    idx, len(providers), provider.name, agent_name,
                )
                response = await provider.generate(system_prompt, user_prompt)
                self._cost_tracker.record(
                    provider=response.provider,
                    model=response.model,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    total_tokens=response.total_tokens,
                    estimated_cost=response.cost,
                    duration_ms=response.duration_ms,
                )
                logger.info(
                    "Provider %s succeeded for %s (tokens=%d, cost=%.4f)",
                    provider.name, agent_name, response.total_tokens, response.cost,
                )
                return {
                    "content": response.content,
                    "provider": response.provider,
                    "model": response.model,
                    "cost": response.cost,
                    "duration_ms": response.duration_ms,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "total_tokens": response.total_tokens,
                }
            except Exception as e:
                last_error = e
                logger.warning(
                    "Provider %s failed for %s (attempt %d/%d): %s",
                    provider.name, agent_name, idx, len(providers), e,
                )
                continue

        logger.error(
            "All %d provider(s) failed for %s. Last error: %s",
            len(providers), agent_name, last_error,
        )
        raise RuntimeError(
            f"All providers failed for {agent_name}. Last error: {last_error}"
        )

    async def execute_structured_with_fallback(
        self,
        providers: list[LLMProvider],
        system_prompt: str,
        user_prompt: str,
        response_format: type,
        agent_name: str = "",
    ) -> dict[str, Any]:
        result = await self.execute_with_fallback(
            providers, system_prompt, user_prompt, agent_name,
        )
        import json
        try:
            parsed = json.loads(result["content"])
            result["parsed"] = parsed
        except json.JSONDecodeError:
            result["parsed"] = {}
        return result
