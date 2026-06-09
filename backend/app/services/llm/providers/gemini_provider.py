import json
import time
from typing import Any, cast

from app.services.llm.providers.base import (
    CostRate,
    LLMProvider,
    LLMResponse,
    ProviderConfig,
)


class GeminiProvider(LLMProvider):
    name = "gemini"
    cost_rates = CostRate(input_per_1k=0.0, output_per_1k=0.0)

    DEFAULTS = ProviderConfig(model="gemini-2.0-flash")

    def __init__(self, config: ProviderConfig | None = None) -> None:
        merged = config or ProviderConfig()
        if not merged.model:
            merged.model = self.DEFAULTS.model
        super().__init__(merged)
        self._client: Any = None

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.config.api_key)
            start = time.monotonic()

            response = client.models.generate_content(
                model=self.config.model,
                contents=f"{system_prompt}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens,
                ),
            )

            duration = int((time.monotonic() - start) * 1000)
            text = response.text if hasattr(response, "text") else str(response.candidates[0].content)

            return LLMResponse(
                content=text,
                total_tokens=0,
                cost=0.0,
                model=self.config.model,
                provider=self.name,
                duration_ms=duration,
            )
        except ImportError:
            return LLMResponse(
                content="Gemini SDK not installed",
                provider=self.name,
                duration_ms=0,
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
        return bool(self.config.api_key)
