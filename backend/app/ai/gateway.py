"""AI Gateway — central module for all LLM interactions.

Every AI call in exHacker goes through this module.
It handles model selection, routing, cost tracking, retries, and fallbacks.

SDPD Model Tiers:
  Tier 0: Deterministic/template — no AI call (raises if called)
  Tier 1: Cheap — deepseek-v4-flash (~$0.15/1M)
  Tier 2: Medium — glm-5.2 (~$2.50/1M)
  Tier 3: Expensive — glm-5.2 (same model until opus available)

Usage:
    gateway = AIGateway()
    response = await gateway.generate(
        prompt=Prompt(system="...", user="..."),
        model_tier=2,
    )
    print(response.content, response.cost)
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Optional

from app.core.config import settings
from app.core.exceptions import AIProviderError

logger = logging.getLogger(__name__)

# ─── Types ───────────────────────────────────────────────────────────────────


class ModelTier:
    """SDPD model tiers — higher = more expensive / more capable."""
    TIER_0 = 0  # Deterministic / template — no AI call
    TIER_1 = 1  # Cheap (deepseek-v4-flash)
    TIER_2 = 2  # Medium (glm-5.2)
    TIER_3 = 3  # Expensive (glm-5.2 for now)


@dataclass
class AIResponse:
    """Structured response from an AI call."""
    content: str = ""
    model_used: str = ""
    cost: float = 0.0
    latency_ms: int = 0
    cached: bool = False
    prompt_tokens: int = 0
    completion_tokens: int = 0


@dataclass
class Prompt:
    """A structured prompt with system instruction and user message."""
    system: str = ""
    user: str = ""
    response_schema: Optional[type] = None


# ─── Model Registry ──────────────────────────────────────────────────────────

MODEL_TIER_MAP: dict[int, str] = {
    ModelTier.TIER_1: settings.AI_MODEL_TIER_1,
    ModelTier.TIER_2: settings.AI_MODEL_TIER_2,
    ModelTier.TIER_3: settings.AI_MODEL_TIER_3,
}

MODEL_COST_PER_1K_TOKENS: dict[str, float] = {
    "deepseek-v4-flash": 0.00015,
    "deepseek-v4-pro": 0.001,
    "glm-5.2": 0.0025,
    "qwen3.7-max": 0.002,
    "qwen3.7-plus": 0.0015,
}

# ─── Mock Responses ─────────────────────────────────────────────────────────


def _get_mock_content(prompt: Prompt) -> str:
    """Generate a realistic fake response when MOCK_AI is enabled."""
    system_lower = (prompt.system or "").lower()
    if "research" in system_lower or "query" in system_lower:
        return '[\n  "competitors for this space",\n  "relevant APIs and integrations",\n  "open source alternatives"\n]'
    return (
        f"This is a simulated AI response (MOCK_AI mode enabled). "
        f"Prompt received: {len(prompt.user or '')} chars."
    )


async def _mock_stream(prompt: Prompt) -> AsyncIterator[str]:
    """Yield mock content in chunks for streaming."""
    content = _get_mock_content(prompt)
    words = content.split()
    for word in words:
        yield word + " "
        await asyncio.sleep(0.02)  # Simulate streaming delay


# ─── Cost Tracker ───────────────────────────────────────────────────────────


class CostTracker:
    """Thread-safe cost tracking for AI calls. Resets on process restart."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def record(
        self,
        model: str,
        cost: float,
        prompt_tokens: int,
        completion_tokens: int,
        cached: bool = False,
    ) -> None:
        async with self._lock:
            self._entries.append({
                "id": str(uuid.uuid4())[:8],
                "model": model,
                "cost": cost,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cached": cached,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    async def get_total_cost(self, since: Optional[datetime] = None) -> float:
        async with self._lock:
            if since is None:
                return sum(e["cost"] for e in self._entries)
            return sum(e["cost"] for e in self._entries if e["timestamp"] >= since.isoformat())

    async def get_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        async with self._lock:
            return self._entries[-limit:]


# ─── API Endpoint ────────────────────────────────────────────────────────────


def _build_messages(prompt: Prompt) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    if prompt.system:
        messages.append({"role": "system", "content": prompt.system})
    messages.append({"role": "user", "content": prompt.user})
    return messages


class AIGateway:
    """Central AI gateway for all LLM interactions.

    Handles model selection by tier, litellm routing, retry with backoff,
    cost tracking, and mock mode for development.
    """

    def __init__(self) -> None:
        self._cost_tracker = CostTracker()

    @property
    def costs(self) -> CostTracker:
        return self._cost_tracker

    async def generate(
        self,
        prompt: Prompt,
        model_tier: int = ModelTier.TIER_2,
        cache_key: Optional[str] = None,
    ) -> AIResponse:
        """Generate a response from an AI model.

        Args:
            prompt: The prompt to send.
            model_tier: SDPD tier (0=deterministic, 1=cheap, 2=medium, 3=expensive).
            cache_key: Optional key for future caching.

        Returns:
            AIResponse with content, model info, cost, and latency.

        Raises:
            AIProviderError: If all retries and fallbacks fail.
        """
        if settings.MOCK_AI:
            return AIResponse(
                content=_get_mock_content(prompt),
                model_used="mock",
                cost=0.0,
                latency_ms=0,
            )

        model = MODEL_TIER_MAP.get(model_tier, settings.AI_MODEL_TIER_2)
        if not model:
            raise AIProviderError(message=f"No model configured for tier {model_tier}.")

        last_error: Exception | None = None
        max_retries = settings.MAX_RETRIES
        base_delay = settings.RETRY_BASE_DELAY

        for attempt in range(max_retries + 1):
            try:
                return await self._call_llm(prompt, model)
            except AIProviderError:
                raise
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    logger.warning("AI call failed (attempt %d/%d): %s. Retrying in %.1fs...",
                                   attempt + 1, max_retries + 1, e, delay)
                    await asyncio.sleep(delay)

        raise AIProviderError(
            message=f"AI generation failed after {max_retries + 1} attempts.",
            detail={"model": model, "last_error": str(last_error)},
            suggestion="Check your API key and try again. Enable MOCK_AI=true for development.",
        )

    async def generate_stream(
        self,
        prompt: Prompt,
        model_tier: int = ModelTier.TIER_2,
    ) -> AsyncIterator[str]:
        """Stream a response from an AI model token by token."""
        if settings.MOCK_AI:
            async for chunk in _mock_stream(prompt):
                yield chunk
            return

        model = MODEL_TIER_MAP.get(model_tier, settings.AI_MODEL_TIER_2)
        if not model:
            return

        messages = _build_messages(prompt)
        try:
            import litellm
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                api_base="https://opencode.ai/zen/go/v1",
                stream=True,
                timeout=settings.AI_TIMEOUT_SECONDS,
            )
            async for chunk in response:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            logger.error("Streaming AI call failed: %s", e)
            raise AIProviderError(
                message="Streaming generation failed.",
                detail={"error": str(e)},
            ) from e

    async def get_total_cost(self, since: Optional[datetime] = None) -> float:
        return await self._cost_tracker.get_total_cost(since)

    async def _call_llm(self, prompt: Prompt, model: str) -> AIResponse:
        """Execute a single LLM call with timing and cost tracking."""
        start = time.monotonic()
        messages = _build_messages(prompt)

        try:
            import litellm
            response = await litellm.acompletion(
                model=model,
                messages=messages,
                api_base="https://opencode.ai/zen/go/v1",
                timeout=settings.AI_TIMEOUT_SECONDS,
            )
        except Exception as e:
            error_msg = str(e)
            if "rate" in error_msg.lower():
                logger.warning("Rate limited on model %s", model)
            raise

        latency_ms = int((time.monotonic() - start) * 1000)
        content = response.choices[0].message.content or ""

        usage = getattr(response, "usage", None)
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0

        cost_per_1k = MODEL_COST_PER_1K_TOKENS.get(model, 0.001)
        cost = (prompt_tokens + completion_tokens) * cost_per_1k / 1000

        if settings.TRACK_COSTS:
            await self._cost_tracker.record(
                model=model, cost=cost,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )

        return AIResponse(
            content=content,
            model_used=model,
            cost=cost,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )


# Singleton
gateway = AIGateway()
