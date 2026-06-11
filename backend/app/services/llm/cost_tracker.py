from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UsageRecord:
    provider: str
    model: str
    tokens: int = 0
    cost: float = 0.0
    duration_seconds: float = 0.0


@dataclass
class CostTracker:
    records: list[UsageRecord] = field(default_factory=list)

    def record(
        self,
        provider: str,
        model: str,
        tokens: int = 0,
        cost: float = 0.0,
        duration_seconds: float = 0.0,
    ) -> None:
        self.records.append(
            UsageRecord(
                provider=provider,
                model=model,
                tokens=tokens,
                cost=cost,
                duration_seconds=duration_seconds,
            )
        )

    def total_cost(self) -> float:
        return sum(r.cost for r in self.records)

    def total_tokens(self) -> int:
        return sum(r.tokens for r in self.records)

    def provider_usage(self) -> dict[str, int]:
        usage: dict[str, int] = {}
        for r in self.records:
            usage[r.provider] = usage.get(r.provider, 0) + 1
        return usage

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_cost": self.total_cost(),
            "total_tokens": self.total_tokens(),
            "provider_usage": self.provider_usage(),
            "records": [
                {
                    "provider": r.provider,
                    "model": r.model,
                    "tokens": r.tokens,
                    "cost": r.cost,
                    "duration_seconds": r.duration_seconds,
                }
                for r in self.records
            ],
        }


_cost_tracker = CostTracker()


def get_cost_tracker() -> CostTracker:
    return _cost_tracker
