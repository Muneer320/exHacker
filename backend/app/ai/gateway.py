"""AI Gateway — central module for all LLM interactions.

Every AI call in exHacker goes through this module.
It handles model selection, routing, cost tracking, retries, and fallbacks.

SDPD Model Tiers:
  Tier 0: Deterministic/template — no AI call (raises if called)
  Tier 1: Cheap — deepseek-v4-flash (~$0.15/1M)
  Tier 2: Medium — glm-5.2 (~$2.50/1M)
  Tier 3: Expensive — glm-5.2 (same model until opus available)

Usage::

    gateway = AIGateway()
    response = await gateway.generate(
        prompt=Prompt(system="...", user="..."),
        model_tier=ModelTier.TIER_2,
    )
    print(response.content, response.cost)
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import IntEnum
from typing import Any, AsyncIterator

from app.core.config import settings
from app.core.exceptions import AIProviderError, ExHackerError, RateLimitError

logger = logging.getLogger(__name__)


# ─── Types ───────────────────────────────────────────────────────────────────


class ModelTier(IntEnum):
    """SDPD model tiers — higher = more expensive / more capable."""

    TIER_0 = 0  # Deterministic / template — no AI call
    TIER_1 = 1  # Cheap (deepseek-v4-flash)
    TIER_2 = 2  # Medium (glm-5.2)
    TIER_3 = 3  # Expensive (glm-5.2 for now)


@dataclass
class AIResponse:
    """Structured response from an AI call.

    Attributes:
        content: The generated text.
        model_used: Model name that served the request.
        cost: Estimated cost in USD.
        latency_ms: Wall-clock latency in milliseconds.
        cached: Whether the response came from cache.
        prompt_tokens: Input token count (0 if unavailable).
        completion_tokens: Output token count (0 if unavailable).
    """

    content: str = ""
    model_used: str = ""
    cost: float = 0.0
    latency_ms: int = 0
    cached: bool = False
    prompt_tokens: int = 0
    completion_tokens: int = 0


@dataclass
class Prompt:
    """A structured prompt with system instruction and user message.

    Attributes:
        system: System prompt text.
        user: User prompt text.
        response_schema: Optional Pydantic model for structured output validation.
    """

    system: str = ""
    user: str = ""
    response_schema: type | None = None


# ─── Model Registry & Cost Table ─────────────────────────────────────────────

# Per-1M-token pricing: (input $/1M, output $/1M)
_COST_PER_1M: dict[str, tuple[float, float]] = {
    "deepseek-v4-flash": (0.075, 0.30),
    "deepseek-v4-pro": (0.28, 2.80),
    "glm-5.2": (0.25, 1.25),
    "qwen3.7-max": (0.40, 1.20),
    "qwen3.7-plus": (0.15, 0.60),
    # Fallbacks for litellm standard names
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "o3-mini": (3.00, 12.00),
}


def _estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Estimate USD cost for a call based on token counts and model pricing."""
    rates = _COST_PER_1M.get(model, _COST_PER_1M["glm-5.2"])
    cost_in = (tokens_in / 1_000_000) * rates[0]
    cost_out = (tokens_out / 1_000_000) * rates[1]
    return round(cost_in + cost_out, 6)


# ─── Cost Tracker (thread-safe) ──────────────────────────────────────────────


@dataclass
class _CostRecord:
    """Internal cost-tracking record."""

    id: str
    timestamp: datetime
    model: str
    cost: float
    prompt_tokens: int
    completion_tokens: int
    cached: bool = False


class CostTracker:
    """Thread-safe cost tracking for AI calls.

    Records are kept in memory and reset on process restart.
    For production persistence, write to the database via a periodic flush.
    """

    def __init__(self) -> None:
        self._records: list[_CostRecord] = []
        self._lock = asyncio.Lock()

    async def record(
        self,
        model: str,
        cost: float,
        prompt_tokens: int,
        completion_tokens: int,
        cached: bool = False,
    ) -> None:
        """Append a cost record (thread-safe via asyncio.Lock)."""
        record = _CostRecord(
            id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc),
            model=model,
            cost=cost,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached=cached,
        )
        async with self._lock:
            self._records.append(record)

    async def get_total_cost(self, since: datetime | None = None) -> float:
        """Return total USD spent since ``since`` (or all-time if None)."""
        async with self._lock:
            if since is None:
                return round(sum(r.cost for r in self._records), 6)
            return round(
                sum(r.cost for r in self._records if r.timestamp >= since),
                6,
            )

    async def get_records(
        self,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[_CostRecord]:
        """Return cost records since ``since`` (for auditing / dashboards)."""
        async with self._lock:
            if since is None:
                return list(self._records[-limit:])
            return [r for r in self._records if r.timestamp >= since][-limit:]


# ─── Mock Content ────────────────────────────────────────────────────────────


def _get_mock_content(prompt: Prompt) -> str:
    """Generate a realistic fake response when MOCK_AI is enabled."""
    system_lower = (prompt.system or "").lower()
    user_lower = (prompt.user or "").lower()

    # Research queries → return JSON array
    if "research" in system_lower or "quer" in user_lower or "json" in user_lower:
        return json.dumps([
            "existing solutions and competitors in this space",
            "market size and growth trends for this product",
            "technical architecture approaches for similar systems",
            "user pain points and unmet needs",
            "open source alternatives and APIs available",
        ])

    # Generic response
    return (
        f"[Mock AI Response]\n\n"
        f"Received prompt ({len(prompt.user or '')} chars). "
        f"This is a simulated response generated in mock mode.\n\n"
        f"System context: {prompt.system or 'none provided'}\n\n"
        f"Mock analysis: The request has been processed. In production, "
        f"this would contain real AI-generated content from {settings.AI_MODEL_TIER_2}."
    )


async def _mock_stream(prompt: Prompt) -> AsyncIterator[str]:
    """Yield mock content in chunks for streaming."""
    content = _get_mock_content(prompt)
    words = content.split()
    for word in words:
        yield word + " "
        await asyncio.sleep(0.02)  # Simulate streaming delay


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _build_messages(prompt: Prompt) -> list[dict[str, str]]:
    """Build the litellm/OpenAI messages array from a Prompt."""
    messages: list[dict[str, str]] = []
    if prompt.system:
        messages.append({"role": "system", "content": prompt.system})
    messages.append({"role": "user", "content": prompt.user})
    return messages


def _convert_error(e: Exception) -> ExHackerError:
    """Convert any provider exception into an ExHacker error."""
    error_str = str(e).lower()

    # Rate limiting
    if "rate limit" in error_str or "429" in error_str or "rate_limit" in error_str:
        return RateLimitError(
            message=f"AI provider rate limit exceeded: {e}",
            detail={"original_error": type(e).__name__},
        )

    # Timeout
    if "timeout" in error_str or "timed out" in error_str:
        return AIProviderError(
            message=f"AI provider timed out: {e}",
            detail={"original_error": type(e).__name__},
            suggestion="Increase AI_TIMEOUT_SECONDS or try again.",
        )

    # Authentication
    if "auth" in error_str or "401" in error_str or "api key" in error_str:
        return AIProviderError(
            message=f"AI provider authentication failed: {e}",
            detail={"original_error": type(e).__name__},
            suggestion="Check your API key configuration.",
        )

    # Generic
    return AIProviderError(
        message=f"AI provider error: {e}",
        detail={"original_error": type(e).__name__, "error": str(e)},
    )


# ─── Main Gateway ────────────────────────────────────────────────────────────


class AIGateway:
    """Central AI gateway for all LLM interactions.

    Handles model selection by tier, litellm routing, retry with backoff,
    cost tracking, caching, and mock mode for development.

    Usage::

        gateway = AIGateway()
        response = await gateway.generate(
            prompt=Prompt(system="You are helpful.", user="Summarise this."),
            model_tier=ModelTier.TIER_1,
        )
    """

    def __init__(self) -> None:
        self._model_map: dict[ModelTier, str] = {
            ModelTier.TIER_1: settings.AI_MODEL_TIER_1,
            ModelTier.TIER_2: settings.AI_MODEL_TIER_2,
            ModelTier.TIER_3: settings.AI_MODEL_TIER_3,
        }
        self._cost_tracker = CostTracker()
        self._cache: dict[str, AIResponse] = {}

    @property
    def costs(self) -> CostTracker:
        """Access the cost tracker for monitoring and auditing."""
        return self._cost_tracker

    # ── Public API ──────────────────────────────────────────────────────────

    async def generate(
        self,
        prompt: Prompt,
        model_tier: ModelTier | int = ModelTier.TIER_2,
        cache_key: str | None = None,
    ) -> AIResponse:
        """Generate a completion from the AI provider.

        Args:
            prompt: The prompt to send (system + user).
            model_tier: SDPD tier (0=deterministic, 1=cheap, 2=medium, 3=expensive).
            cache_key: If provided, results are cached under this key.

        Returns:
            :class:`AIResponse` with content, cost, and metadata.

        Raises:
            AIProviderError: If all retries fail or the tier is invalid.
            RateLimitError: If the provider returns a 429.
        """
        tier = ModelTier(int(model_tier))

        # Tier 0 is deterministic — should never hit the LLM.
        if tier == ModelTier.TIER_0:
            raise AIProviderError(
                message=(
                    "Tier 0 requests are deterministic and must not "
                    "call the AI gateway. "
                    "Use template/rule-based logic instead."
                ),
                detail={"tier": 0},
            )

        # Check cache
        if cache_key and cache_key in self._cache:
            cached_resp = self._cache[cache_key]
            logger.info("Cache hit for key='%s'", cache_key)
            return AIResponse(
                content=cached_resp.content,
                model_used=cached_resp.model_used,
                cost=0.0,
                latency_ms=0,
                cached=True,
                prompt_tokens=cached_resp.prompt_tokens,
                completion_tokens=cached_resp.completion_tokens,
            )

        # Mock mode — return fake data without calling any API
        if settings.MOCK_AI:
            return await self._mock_generate(prompt, tier, cache_key)

        model = self._select_model(tier)
        messages = _build_messages(prompt)

        # Retry with exponential backoff
        last_error: Exception | None = None
        for attempt in range(settings.MAX_RETRIES + 1):
            try:
                return await self._call_litellm(prompt, model, messages, cache_key)
            except RateLimitError:
                # Don't retry on rate limits — let the caller handle it.
                raise
            except AIProviderError as e:
                last_error = e
                if attempt < settings.MAX_RETRIES:
                    delay = settings.RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(
                        "AI call failed (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1,
                        settings.MAX_RETRIES + 1,
                        delay,
                        e.message,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "AI call failed after %d attempts: %s",
                        attempt + 1,
                        e.message,
                    )

        raise AIProviderError(
            message=f"AI generation failed after {settings.MAX_RETRIES + 1} attempts.",
            detail={
                "model": model,
                "last_error": str(last_error) if last_error else "unknown",
            },
            suggestion=(
                "Check your API key and try again. "
                "Enable MOCK_AI=true for development."
            ),
        )

    async def generate_stream(
        self,
        prompt: Prompt,
        model_tier: ModelTier | int = ModelTier.TIER_2,
    ) -> AsyncIterator[str]:
        """Stream a completion token-by-token from the AI provider.

        Args:
            prompt: The prompt to send.
            model_tier: SDPD tier.

        Yields:
            Chunks of text as they arrive.

        Raises:
            AIProviderError: If streaming fails or tier is invalid.
        """
        tier = ModelTier(int(model_tier))

        if tier == ModelTier.TIER_0:
            raise AIProviderError(
                message="Tier 0 requests must not call the AI gateway.",
                detail={"tier": 0},
            )

        if settings.MOCK_AI:
            async for chunk in _mock_stream(prompt):
                yield chunk
            return

        model = self._select_model(tier)
        messages = _build_messages(prompt)

        try:
            import litellm

            stream = await litellm.acompletion(
                model=model,
                messages=messages,
                stream=True,
                timeout=settings.AI_TIMEOUT_SECONDS,
            )

            async for chunk in stream:
                content = self._extract_stream_chunk(chunk)
                if content:
                    yield content

        except Exception as e:
            raise _convert_error(e) from e

    async def get_total_cost(self, since: datetime | None = None) -> float:
        """Return total AI cost since ``since`` (UTC). If None, all-time."""
        return await self._cost_tracker.get_total_cost(since)

    # ── Internals ───────────────────────────────────────────────────────────

    def _select_model(self, tier: ModelTier) -> str:
        """Map a tier to a concrete model name from settings."""
        model = self._model_map.get(tier)
        if not model:
            raise AIProviderError(
                message=f"No model configured for tier {tier}",
                detail={"tier": int(tier)},
            )
        return model

    async def _call_litellm(
        self,
        _prompt: Prompt,
        model: str,
        messages: list[dict[str, str]],
        cache_key: str | None,
    ) -> AIResponse:
        """Make a single litellm acompletion call and return an AIResponse."""
        start = time.monotonic()

        try:
            import litellm

            response = await litellm.acompletion(
                model=model,
                messages=messages,
                timeout=settings.AI_TIMEOUT_SECONDS,
            )
        except Exception as e:
            raise _convert_error(e) from e

        latency_ms = int((time.monotonic() - start) * 1000)

        # Extract content — litellm returns a ModelResponse object
        content = ""
        if hasattr(response, "choices") and response.choices:
            msg = response.choices[0].message
            content = getattr(msg, "content", "") or ""
        elif isinstance(response, dict):
            choices = response.get("choices") or []
            if choices:
                content = (choices[0].get("message", {}) or {}).get("content", "")

        # Extract token usage
        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
        completion_tokens = getattr(usage, "completion_tokens", 0) if usage else 0

        # Calculate cost
        cost = (
            _estimate_cost(model, prompt_tokens, completion_tokens)
            if settings.TRACK_COSTS
            else 0.0
        )

        ai_response = AIResponse(
            content=content,
            model_used=model,
            cost=cost,
            latency_ms=latency_ms,
            cached=False,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

        # Cache the response if a key was provided
        if cache_key:
            self._cache[cache_key] = ai_response

        # Record cost
        if settings.TRACK_COSTS and cost > 0:
            await self._cost_tracker.record(
                model=model,
                cost=cost,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )

        logger.info(
            "AI call complete | model=%s cost=$%.4f tokens=%d/%d latency=%dms",
            model,
            cost,
            prompt_tokens,
            completion_tokens,
            latency_ms,
        )

        return ai_response

    @staticmethod
    def _extract_stream_chunk(chunk: Any) -> str:
        """Extract text from a streaming chunk object."""
        try:
            if hasattr(chunk, "choices") and chunk.choices:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    return delta.content
            if isinstance(chunk, dict):
                choices = chunk.get("choices") or []
                if choices:
                    delta = choices[0].get("delta", {}) or {}
                    content = delta.get("content", "")
                    if content:
                        return str(content)
        except (IndexError, KeyError, AttributeError):
            pass
        return ""

    # ── Mock mode ───────────────────────────────────────────────────────────

    async def _mock_generate(
        self,
        prompt: Prompt,
        tier: ModelTier,
        cache_key: str | None,
    ) -> AIResponse:
        """Return a realistic fake response without calling any API."""
        model = self._select_model(tier)
        mock_content = _get_mock_content(prompt)
        mock_tokens_in = len((prompt.system or "").split()) + len(
            (prompt.user or "").split()
        )
        mock_tokens_out = len(mock_content.split())
        cost = (
            _estimate_cost(model, mock_tokens_in, mock_tokens_out)
            if settings.TRACK_COSTS
            else 0.0
        )

        response = AIResponse(
            content=mock_content,
            model_used=f"{model} (mock)",
            cost=cost,
            latency_ms=42,
            cached=False,
            prompt_tokens=mock_tokens_in,
            completion_tokens=mock_tokens_out,
        )

        if cache_key:
            self._cache[cache_key] = response

        # Record cost even in mock mode for testing cost tracking
        if settings.TRACK_COSTS and cost > 0:
            await self._cost_tracker.record(
                model=model,
                cost=cost,
                prompt_tokens=mock_tokens_in,
                completion_tokens=mock_tokens_out,
            )

        logger.info("MOCK AI response | model=%s cost=$%.4f", model, cost)
        return response


# ─── Convenience singleton ───────────────────────────────────────────────────

gateway: AIGateway = AIGateway()
