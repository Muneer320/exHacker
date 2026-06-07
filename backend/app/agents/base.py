from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class AgentResult:
    success: bool
    output: dict[str, Any] | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    name: str = "base_agent"
    description: str = ""
    critical: bool = False

    def __init__(self) -> None:
        self.logger = logger.bind(agent=self.name)

    @abstractmethod
    async def execute(self, state: dict[str, Any]) -> AgentResult:
        ...

    def validate_inputs(self, state: dict[str, Any]) -> list[str]:
        return []

    def validate_output(self, output: dict[str, Any]) -> list[str]:
        return []

    async def run(self, state: dict[str, Any]) -> AgentResult:
        self.logger.info("agent_execution_started")
        input_errors = self.validate_inputs(state)
        if input_errors:
            return AgentResult(
                success=False,
                error=f"Input validation failed: {', '.join(input_errors)}",
            )
        result = await self.execute(state)
        if result.success and result.output:
            output_errors = self.validate_output(result.output)
            if output_errors:
                return AgentResult(
                    success=False,
                    error=f"Output validation failed: {', '.join(output_errors)}",
                )
        self.logger.info(
            "agent_execution_completed",
            success=result.success,
            error=result.error,
        )
        return result
