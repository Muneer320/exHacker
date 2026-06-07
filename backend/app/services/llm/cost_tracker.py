from dataclasses import dataclass, field
from typing import Any


@dataclass
class CostEntry:
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    duration_ms: int = 0


class CostTracker:
    def __init__(self) -> None:
        self._entries: list[CostEntry] = []

    def record(
        self,
        provider: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
        estimated_cost: float = 0.0,
        duration_ms: int = 0,
    ) -> None:
        self._entries.append(CostEntry(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            duration_ms=duration_ms,
        ))

    @property
    def total_cost(self) -> float:
        return round(sum(e.estimated_cost for e in self._entries), 6)

    @property
    def total_tokens(self) -> int:
        return sum(e.total_tokens for e in self._entries)

    @property
    def entries(self) -> list[CostEntry]:
        return list(self._entries)

    def reset(self) -> None:
        self._entries.clear()

    def summary(self) -> dict[str, Any]:
        return {
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
            "total_calls": len(self._entries),
            "by_provider": self._by_provider(),
        }

    def _by_provider(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for e in self._entries:
            if e.provider not in result:
                result[e.provider] = {"calls": 0, "tokens": 0, "cost": 0.0}
            result[e.provider]["calls"] += 1
            result[e.provider]["tokens"] += e.total_tokens
            result[e.provider]["cost"] += e.estimated_cost
        for v in result.values():
            v["cost"] = round(v["cost"], 6)
        return result
