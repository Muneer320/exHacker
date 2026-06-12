"""
Base Agent: Abstract foundation for all exHacker agents.

All agents inherit from BaseAgent to get:
- Structured LLM call with schema validation
- Automatic retry (max 3 attempts)
- Execution timing and token tracking
- Contextual error logging
- Mock fallback when LLM is unavailable
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Any, Dict

from pydantic import BaseModel

from app.services.llm.service import llm_service
from app.schemas.state import ExHackerStateSchema, WorkflowStage

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

AGENT_VERSION = "v1"
MAX_RETRIES = 3


class BaseAgent(ABC):
    """
    Abstract base class for all exHacker agents.

    Each concrete agent must implement:
    - agent_name: human-readable identifier
    - stage: WorkflowStage enum value
    - build_system_prompt(state): build ROLE/OBJECTIVE prompt
    - build_user_prompt(state): build INPUT DATA prompt
    - response_schema: Pydantic model class for structured output
    - apply_result(state, result): write result back into the state dict
    - mock_result(state): fallback data if LLM is unavailable
    """

    # Subclass must set these
    agent_name: str = "BaseAgent"
    stage: WorkflowStage = None

    @property
    @abstractmethod
    def response_schema(self) -> Type[T]:
        """Return the Pydantic model class that validates LLM output."""
        ...

    @abstractmethod
    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        """Return the system prompt for this agent."""
        ...

    @abstractmethod
    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        """Return the user prompt for this agent."""
        ...

    @abstractmethod
    def apply_result(self, state: Dict[str, Any], result: T) -> Dict[str, Any]:
        """Write the validated Pydantic result back into the workflow state dict."""
        ...

    @abstractmethod
    def mock_result(self, state: Dict[str, Any]) -> T:
        """Return a high-quality mock result for testing or LLM-unavailable scenarios."""
        ...

    # -------------------------------------------------------------------------
    # Core execution: called by the LangGraph node wrapper
    # -------------------------------------------------------------------------

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution entry point.

        1. Builds prompts
        2. Calls LLM with retry logic
        3. Applies validated result to state
        4. Records timing & token metrics
        5. Falls back to mock on full failure
        """
        start = time.monotonic()
        logger.info(f"[{self.agent_name}] Starting execution (version={AGENT_VERSION})")

        system_prompt = self.build_system_prompt(state)
        user_prompt = self.build_user_prompt(state)

        result = None
        last_error = None
        attempts = 0

        for attempt in range(1, MAX_RETRIES + 1):
            attempts = attempt
            try:
                logger.info(f"[{self.agent_name}] LLM call attempt {attempt}/{MAX_RETRIES}")
                result = await llm_service.generate_with_fallback(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    response_model=self.response_schema,
                )
                logger.info(f"[{self.agent_name}] LLM call succeeded on attempt {attempt}")
                break
            except Exception as exc:
                last_error = exc
                logger.warning(
                    f"[{self.agent_name}] Attempt {attempt} failed: {exc}. "
                    f"{'Retrying...' if attempt < MAX_RETRIES else 'Switching to mock.'}"
                )

        # Fall back to mock if all LLM attempts failed
        used_mock = False
        if result is None:
            logger.error(
                f"[{self.agent_name}] All {MAX_RETRIES} LLM attempts failed. "
                f"Using mock fallback. Last error: {last_error}"
            )
            result = self.mock_result(state)
            used_mock = True

        # Write result into state
        state = self.apply_result(state, result)

        # Record stage metrics
        duration = time.monotonic() - start
        estimated_tokens = 600  # conservative default
        estimated_cost = round(estimated_tokens * 0.000002, 6)

        if "execution" not in state or state["execution"] is None:
            state["execution"] = {
                "total_duration_seconds": 0.0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "provider_usage": [],
                "stage_metrics": [],
            }

        state["execution"]["total_duration_seconds"] += duration
        state["execution"]["total_tokens"] += estimated_tokens
        state["execution"]["total_cost"] += estimated_cost
        state["execution"]["stage_metrics"].append(
            {
                "stage": self.stage.value if self.stage else self.agent_name,
                "duration_seconds": round(duration, 4),
                "tokens": estimated_tokens,
                "cost": estimated_cost,
                "used_mock": used_mock,
                "attempts": attempts,
            }
        )

        logger.info(
            f"[{self.agent_name}] Completed in {duration:.3f}s "
            f"(mock={used_mock}, attempts={attempts})"
        )
        return state
