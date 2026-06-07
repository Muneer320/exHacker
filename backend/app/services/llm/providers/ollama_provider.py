import json
import time
from typing import Any

import httpx

from app.services.llm.providers.base import (
    CostRate,
    LLMProvider,
    LLMResponse,
    ProviderConfig,
)


class OllamaProvider(LLMProvider):
    name = "ollama"
    cost_rates = CostRate(input_per_1k=0.0, output_per_1k=0.0)

    def __init__(self, config: ProviderConfig | None = None) -> None:
        super().__init__(config or ProviderConfig(
            model="llama3.2",
            base_url="http://localhost:11434",
        ))
        self._base_url = self.config.base_url or "http://localhost:11434"

    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        start = time.monotonic()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self.config.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens,
                    },
                    "stream": False,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()

        duration = int((time.monotonic() - start) * 1000)

        return LLMResponse(
            content=data.get("message", {}).get("content", ""),
            provider=self.name,
            model=self.config.model,
            duration_ms=duration,
        )

    async def generate_structured(
        self, system_prompt: str, user_prompt: str, response_format: type
    ) -> dict[str, Any]:
        result = await self.generate(system_prompt, user_prompt)
        try:
            return json.loads(result.content)
        except json.JSONDecodeError:
            return {}

    async def validate(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self._base_url}/api/tags",
                    timeout=5.0,
                )
                return response.status_code == 200
        except Exception:
            return False
