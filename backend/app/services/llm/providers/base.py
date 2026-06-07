from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, cast


@dataclass
class ProviderConfig:
    api_key: str | None = None
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 4096
    base_url: str | None = None


@dataclass
class LLMResponse:
    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    model: str = ""
    provider: str = ""
    duration_ms: int = 0


@dataclass
class CostRate:
    input_per_1k: float
    output_per_1k: float


class LLMProvider(ABC):
    name: str = ""
    cost_rates: CostRate = CostRate(input_per_1k=0.0, output_per_1k=0.0)

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        ...

    async def generate_structured(
        self, system_prompt: str, user_prompt: str, response_format: type
    ) -> dict[str, Any]:
        raw = await self.generate(system_prompt, user_prompt)
        try:
            import json
            return cast(dict[str, Any], json.loads(raw.content))
        except json.JSONDecodeError:
            return {}

    @abstractmethod
    async def validate(self) -> bool:
        ...
