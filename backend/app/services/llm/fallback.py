import asyncio
import logging
import random
from collections import OrderedDict
from typing import Any

from app.services.llm.cost_tracker import CostTracker
from app.services.llm.providers.base import LLMProvider
from app.services.llm.providers.gemini_provider import GeminiProvider
from app.services.llm.providers.groq_provider import GroqProvider
from app.services.llm.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS_CODES = {429, 503}
_MAX_RETRIES_PER_PROVIDER = 3
_BASE_BACKOFF_S = 2.0
_MAX_CYCLES = 2  # how many full cycles through all providers before giving up


def _is_rate_limited(error: Exception) -> bool:
    msg = str(error).lower()
    return any(kw in msg for kw in ("rate limit", "rate_limit", "429", "too many requests", "503"))


class FallbackChain:
    def __init__(self, cost_tracker: CostTracker) -> None:
        self._cost_tracker = cost_tracker

    @staticmethod
    def _shuffle_providers(providers: list[LLMProvider]) -> list[LLMProvider]:
        """Shuffle providers within each type while maintaining type priority order."""
        groups: OrderedDict[str, list[LLMProvider]] = OrderedDict()
        for p in providers:
            groups.setdefault(p.name, []).append(p)
        result: list[LLMProvider] = []
        for _name, group in groups.items():
            shuffled = list(group)
            random.shuffle(shuffled)
            result.extend(shuffled)
        return result

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
        return self._shuffle_providers(providers)

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
        providers = self._shuffle_providers(providers)

        for cycle in range(_MAX_CYCLES):
            logger.info(
                "Fallback cycle %d/%d: trying %d provider(s) for %s: %s",
                cycle + 1, _MAX_CYCLES, len(providers), agent_name,
                [p.name for p in providers],
            )
            for idx, provider in enumerate(providers, 1):
                retries = 0
                while retries < _MAX_RETRIES_PER_PROVIDER:
                    try:
                        logger.info(
                            "Fallback cycle %d, attempt %d/%d: %s for %s (retry=%d)",
                            cycle + 1, idx, len(providers),
                            provider.name, agent_name, retries,
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
                        retries += 1
                        if _is_rate_limited(e) and retries < _MAX_RETRIES_PER_PROVIDER:
                            backoff = _BASE_BACKOFF_S ** retries
                            logger.warning(
                                "Rate limited on %s for %s, retrying in %.1fs (retry %d/%d)",
                                provider.name, agent_name, backoff, retries, _MAX_RETRIES_PER_PROVIDER,
                            )
                            await asyncio.sleep(backoff)
                            continue
                        logger.warning(
                            "Provider %s failed for %s (attempt %d/%d): %s",
                            provider.name, agent_name, idx, len(providers), e,
                        )
                        break  # move to next provider (or give up)

            if cycle < _MAX_CYCLES - 1:
                # Re-shuffle and wait before next cycle in case rate limits cool down
                providers = self._shuffle_providers(providers)
                wait = _BASE_BACKOFF_S * (cycle + 2)
                logger.info(
                    "All providers exhausted in cycle %d for %s. "
                    "Re-shuffling and retrying after %.1fs wait...",
                    cycle + 1, agent_name, wait,
                )
                await asyncio.sleep(wait)

        logger.error(
            "All %d provider(s) failed after %d cycle(s) for %s. Last error: %s",
            len(providers), _MAX_CYCLES, agent_name, last_error,
        )
        raise RuntimeError(
            f"All providers failed for {agent_name} after {_MAX_CYCLES} cycles. "
            f"Last error: {last_error}"
        )

    def _extract_json(self, text: str) -> dict[str, Any]:
        """Extract JSON from LLM response, finding it anywhere in the text."""
        import json
        import re

        text = text.strip()
        # Remove markdown code fences and any leading/trailing text
        text = re.sub(r"^[\s\S]*?```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```[\s\S]*$", "", text)
        # Try to find a JSON object anywhere
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

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
        result["parsed"] = self._extract_json(result["content"])
        return result
