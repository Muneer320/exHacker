import json
import time
from typing import Any

from openai import AsyncOpenAI

from app.services.llm.providers.base import (
    CostRate,
    LLMProvider,
    LLMResponse,
    ProviderConfig,
)


class OpenAIProvider(LLMProvider):
    name = "openai"
    cost_rates = CostRate(input_per_1k=0.01, output_per_1k=0.03)

    def __init__(self, config: ProviderConfig | None = None) -> None:
        super().__init__(config or ProviderConfig(model="gpt-4o"))
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=self.config.api_key)
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
        total_tokens = input_tokens + output_tokens
        cost = (input_tokens / 1000 * self.cost_rates.input_per_1k +
                output_tokens / 1000 * self.cost_rates.output_per_1k)

        return LLMResponse(
            content=response.choices[0].message.content or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=round(cost, 6),
            model=self.config.model,
            provider=self.name,
            duration_ms=duration,
        )

    async def generate_structured(
        self, system_prompt: str, user_prompt: str, response_format: type
    ) -> dict[str, Any]:
        client = self._get_client()
        start = time.monotonic()

        self._model_to_json_schema(response_format)

        response = await client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        int((time.monotonic() - start) * 1000)
        content = response.choices[0].message.content or "{}"

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    async def validate(self) -> bool:
        try:
            client = self._get_client()
            await client.models.list()
            return True
        except Exception:
            return False

    def _model_to_json_schema(self, model: type) -> dict[str, Any]:
        try:
            from pydantic import BaseModel
            if issubclass(model, BaseModel):
                return model.model_json_schema()
        except (TypeError, AttributeError):
            pass
        return {}
