import json
import time
from typing import Any, cast

from openai import AsyncOpenAI

from app.services.llm.providers.base import (
    CostRate,
    LLMProvider,
    LLMResponse,
    ProviderConfig,
)


class GroqProvider(LLMProvider):
    name = "groq"
    cost_rates = CostRate(input_per_1k=0.0, output_per_1k=0.0)

    DEFAULTS = ProviderConfig(
        model="llama-3.3-70b-versatile",
        base_url="https://api.groq.com/openai/v1",
    )

    def __init__(self, config: ProviderConfig | None = None) -> None:
        merged = config or ProviderConfig()
        if not merged.model:
            merged.model = self.DEFAULTS.model
        if not merged.base_url:
            merged.base_url = self.DEFAULTS.base_url
        super().__init__(merged)
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=120.0,
            )
        return self._client

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        client = self._get_client()
        start = time.monotonic()

        response = await client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        duration = int((time.monotonic() - start) * 1000)
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        return LLMResponse(
            content=response.choices[0].message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost=0.0,
            model=self.config.model,
            provider=self.name,
            duration_ms=duration,
        )

    async def generate_structured(
        self, system_prompt: str, user_prompt: str, response_format: type
    ) -> dict[str, Any]:
        result = await self.generate(system_prompt, user_prompt)
        try:
            return cast(dict[str, Any], json.loads(result.content))
        except json.JSONDecodeError:
            return {}

    async def validate(self) -> bool:
        try:
            client = self._get_client()
            await client.models.list()
            return True
        except Exception:
            return False
