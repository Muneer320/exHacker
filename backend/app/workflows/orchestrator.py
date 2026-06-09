import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any, cast
from uuid import uuid4

import structlog
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.types import Command, interrupt, StreamWriter

from app.agents.registry import AgentRegistry
from app.schemas.architecture import ArchitecturePackage
from app.schemas.challenge import ChallengeIntelligence
from app.schemas.idea import Idea, ValidationReport
from app.schemas.opportunity import OpportunityAnalysis
from app.schemas.pitch import PitchPackage
from app.schemas.presentation import PresentationPackage
from app.schemas.problem import ProblemAnalysis
from app.schemas.prompts import PromptPackage
from app.schemas.state import (
    AgentError,
    AgentErrorSeverity,
    ExHackerState,
    WorkflowStage,
)
from app.schemas.team import TeamProfile
from app.schemas.tech_stack import TechStack

logger = structlog.get_logger()

ProgressCallback = Callable[[str, str, list[str], list[dict[str, Any]], list[dict[str, Any]]], Awaitable[None]]

AGENT_TO_STATE_KEY: dict[str, str] = {
    "user_profiler": "team_profile",
    "challenge_intelligence": "challenge_intelligence",
    "problem_analyst": "problem_analysis",
    "opportunity_planner": "opportunity_analysis",
    "idea_generator": "generated_ideas",
    "idea_validator": "validation_reports",
    "solution_architect": "architecture",
    "tech_stack_advisor": "tech_stack",
    "build_accelerator": "prompts",
    "presentation_agent": "presentation",
    "pitch_coach": "pitch",
}

AGENT_TO_STAGE: dict[str, WorkflowStage] = {
    "user_profiler": WorkflowStage.INPUT,
    "challenge_intelligence": WorkflowStage.CHALLENGE_INTELLIGENCE,
    "problem_analyst": WorkflowStage.PROBLEM_ANALYSIS,
    "opportunity_planner": WorkflowStage.OPPORTUNITY_ANALYSIS,
    "idea_generator": WorkflowStage.IDEA_GENERATION,
    "idea_validator": WorkflowStage.IDEA_VALIDATION,
    "solution_architect": WorkflowStage.ARCHITECTURE,
    "tech_stack_advisor": WorkflowStage.TECH_STACK,
    "build_accelerator": WorkflowStage.BUILD_ACCELERATION,
    "presentation_agent": WorkflowStage.PRESENTATION,
    "pitch_coach": WorkflowStage.PITCH,
}

# Ordered sequence used for progress display
AGENT_SEQUENCE = [
    "user_profiler",
    "challenge_intelligence",
    "problem_analyst",
    "opportunity_planner",
    "idea_generator",
    "idea_validator",
    "solution_architect",
    "tech_stack_advisor",
    "build_accelerator",
    "presentation_agent",
    "pitch_coach",
]

WORKFLOW_EDGES: list[tuple[str, str]] = [
    ("user_profiler", "challenge_intelligence"),
    ("challenge_intelligence", "problem_analyst"),
    ("problem_analyst", "opportunity_planner"),
    ("opportunity_planner", "idea_generator"),
    ("idea_generator", "idea_validator"),
]


class WorkflowOrchestrator:
    def __init__(self) -> None:
        self._checkpointer = MemorySaver()
        self._progress_callback: ProgressCallback | None = None
        self.graph = self._build_graph()

    def set_progress_callback(self, callback: ProgressCallback) -> None:
        """Register a callback invoked after every agent completes to update DB."""
        self._progress_callback = callback

    def _build_graph(self) -> Any:
        workflow = StateGraph(ExHackerState)

        # ── Register every agent node ONCE ───────────────────────────────────
        for agent_name in AGENT_TO_STAGE:
            workflow.add_node(agent_name, self._make_agent_node(agent_name))

        # ── Special nodes ────────────────────────────────────────────────────
        workflow.add_node("human_approval", self._human_approval_node)
        workflow.add_node("export", self._export_node)

        # ── Entry point ──────────────────────────────────────────────────────
        workflow.set_entry_point("user_profiler")

        # ── Linear edges (up to idea_generator → idea_validator) ────────────
        for src, dst in WORKFLOW_EDGES:
            workflow.add_edge(src, dst)

        # ── Conditional routing after validation ─────────────────────────────
        workflow.add_conditional_edges(
            "idea_validator",
            self._route_after_validation,
            {
                "human_approval": "human_approval",
                "idea_generator": "idea_generator",
            },
        )

        workflow.add_conditional_edges(
            "human_approval",
            self._route_after_approval,
            {
                "solution_architect": "solution_architect",
                "idea_generator": "idea_generator",
            },
        )

        # ── Special nodes ────────────────────────────────────────────────────
        workflow.add_node("architecture_approval", self._architecture_approval_node)
        workflow.add_node("tech_stack_approval", self._tech_stack_approval_node)
        workflow.add_node("prompts_approval", self._prompts_approval_node)

        # ── Post-approval chain with checkpoints ──────────────────────────────
        workflow.add_edge("solution_architect", "architecture_approval")
        workflow.add_edge("architecture_approval", "tech_stack_advisor")
        workflow.add_edge("tech_stack_advisor", "tech_stack_approval")
        workflow.add_edge("tech_stack_approval", "build_accelerator")
        workflow.add_edge("build_accelerator", "prompts_approval")
        workflow.add_edge("prompts_approval", "presentation_agent")
        workflow.add_edge("presentation_agent", "pitch_coach")
        workflow.add_edge("pitch_coach", "export")

        workflow.set_finish_point("export")

        return workflow.compile(checkpointer=self._checkpointer)

    # ─────────────────────────────────────────────────────────────────────────
    # Node factories
    # ─────────────────────────────────────────────────────────────────────────

    def _make_agent_node(self, agent_name: str) -> Any:
        async def _run(state: ExHackerState) -> dict[str, Any]:
            agent = AgentRegistry.get(agent_name)
            if not agent:
                err_msg = f"Agent '{agent_name}' not found in registry"
                logger.error("agent_not_found", agent=agent_name)
                return {"errors": [AgentError(
                    agent_name=agent_name,
                    timestamp=datetime.now(UTC).isoformat(),
                    message=err_msg,
                    severity=AgentErrorSeverity.CRITICAL,
                )]}

            ts_start = datetime.now(UTC).isoformat()
            start = time.monotonic()
            logger.info(
                "agent_started",
                agent=agent_name,
                project_id=state.project.id,
                stage=AGENT_TO_STAGE.get(agent_name, "unknown"),
            )

            # Notify DB: this agent is now running
            if self._progress_callback:
                await self._progress_callback(
                    state.project.id,
                    agent_name,
                    state.completed_agents,
                    cast(list[dict[str, Any]], state.agent_metadata.get("logs", [])),
                    [e.model_dump() for e in state.errors],
                )

            # Track idea generation retries to break infinite loop
            update_extras: dict[str, Any] = {}
            if agent_name == "idea_generator":
                update_extras["idea_generation_attempts"] = state.idea_generation_attempts + 1

            # ── Agent output cache: skip if output already exists ─────────────
            _always_run = {"idea_generator", "idea_validator"}
            _state_key = AGENT_TO_STATE_KEY.get(agent_name)
            if agent_name not in _always_run and _state_key:
                _existing = getattr(state, _state_key, None)
                if _existing is not None and _existing:
                    logger.info(
                        "agent_skipped_cached",
                        agent=agent_name,
                        state_key=_state_key,
                        project_id=state.project.id,
                    )
                    cached_log: dict[str, Any] = {
                        "agent": agent_name,
                        "started_at": ts_start,
                        "finished_at": datetime.now(UTC).isoformat(),
                        "duration_ms": 0,
                        "success": True,
                        "provider": "cache",
                        "model": "cached",
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost": 0.0,
                    }
                    existing_logs_cache: list[dict[str, Any]] = cast(
                        list[dict[str, Any]], state.agent_metadata.get("logs", []),
                    )
                    existing_logs_cache.append(cached_log)
                    return {
                        "completed_agents": [*state.completed_agents, agent_name],
                        "current_stage": AGENT_TO_STAGE.get(agent_name, state.current_stage),
                        "agent_metadata": {
                            **state.agent_metadata,
                            "logs": existing_logs_cache,
                        },
                    }

            state_dict = state.model_dump()
            try:
                result = await agent.run(state_dict)
            except Exception as exc:
                logger.exception(
                    "agent_node_crash",
                    agent=agent_name,
                    project_id=state.project.id,
                    error=str(exc),
                )
                elapsed = int((time.monotonic() - start) * 1000)
                crash_update: dict[str, Any] = {
                    "completed_agents": [*state.completed_agents, agent_name],
                    "current_stage": AGENT_TO_STAGE.get(agent_name, state.current_stage),
                    "errors": [*state.errors, AgentError(
                        agent_name=agent_name,
                        timestamp=ts_start,
                        message=f"{type(exc).__name__}: {exc}",
                        severity=AgentErrorSeverity.CRITICAL,
                    )],
                }
                if update_extras:
                    crash_update.update(update_extras)
                return crash_update
            elapsed = int((time.monotonic() - start) * 1000)

            # Build structured log entry
            log_entry: dict[str, Any] = {
                "agent": agent_name,
                "started_at": ts_start,
                "finished_at": datetime.now(UTC).isoformat(),
                "duration_ms": elapsed,
                "success": result.success,
            }
            if result.metadata:
                log_entry["provider"] = result.metadata.get("provider", "")
                log_entry["model"] = result.metadata.get("model", "")
                log_entry["input_tokens"] = result.metadata.get("input_tokens", 0)
                log_entry["output_tokens"] = result.metadata.get("output_tokens", 0)
                log_entry["cost"] = result.metadata.get("cost", 0.0)

            if result.success:
                logger.info(
                    "agent_completed",
                    agent=agent_name,
                    project_id=state.project.id,
                    duration_ms=elapsed,
                    provider=log_entry.get("provider", ""),
                    model=log_entry.get("model", ""),
                    tokens=log_entry.get("input_tokens", 0) + log_entry.get("output_tokens", 0),
                    cost=log_entry.get("cost", 0.0),
                    state_key=AGENT_TO_STATE_KEY.get(agent_name),
                )
            else:
                log_entry["error"] = result.error
                logger.error(
                    "agent_failed",
                    agent=agent_name,
                    project_id=state.project.id,
                    duration_ms=elapsed,
                    error=result.error,
                )

            # Build state update
            update: dict[str, Any] = {
                "completed_agents": [*state.completed_agents, agent_name],
                "current_stage": AGENT_TO_STAGE.get(agent_name, state.current_stage),
            }

            existing_logs: list[dict[str, Any]] = cast(
                list[dict[str, Any]], state.agent_metadata.get("logs", []),
            )
            existing_logs.append(log_entry)

            if result.success and result.output:
                state_key = AGENT_TO_STATE_KEY.get(agent_name)
                if state_key:
                    if state_key == "generated_ideas":
                        update["generated_ideas"] = result.output.get("ideas", [])
                    elif state_key == "validation_reports":
                        update["generated_ideas"] = result.output.get("ideas", state.generated_ideas)
                        update["validation_reports"] = result.output.get("validation_reports", [])
                    else:
                        update[state_key] = result.output
            else:
                error = AgentError(
                    agent_name=agent_name,
                    timestamp=ts_start,
                    message=result.error or "Unknown error",
                    severity=AgentErrorSeverity.CRITICAL if agent.critical else AgentErrorSeverity.WARNING,
                )
                update["errors"] = [*state.errors, error]
                if agent.critical:
                    update["agent_metadata"] = {**state.agent_metadata, "logs": existing_logs}
                    # Notify DB of failure
                    if self._progress_callback:
                        await self._progress_callback(
                            state.project.id,
                            "",  # no current agent (stopped)
                            update["completed_agents"],
                            existing_logs,
                            [e.model_dump() for e in update["errors"]],
                        )
                    return update

            update["agent_metadata"] = {
                **state.agent_metadata,
                "logs": existing_logs,
                agent_name: {"duration_ms": elapsed, **(result.metadata or {})},
            }
            if update_extras:
                update.update(update_extras)

            # Notify DB: agent finished, clear current_agent
            if self._progress_callback:
                await self._progress_callback(
                    state.project.id,
                    "",  # cleared — next agent will set it when it starts
                    update["completed_agents"],
                    existing_logs,
                    [e.model_dump() for e in state.errors],
                )

            return update

        return _run

    async def _human_approval_node(self, state: ExHackerState) -> dict[str, Any]:
        logger.info("waiting_for_human_approval", project_id=state.project.id)
        ideas = [i.model_dump() for i in (state.generated_ideas or [])]
        payload = {
            "stage": "idea_selection",
            "ideas": ideas,
            "attempts": state.idea_generation_attempts,
        }
        selected = interrupt(payload)
        if isinstance(selected, dict) and selected.get("selected_idea_id"):
            sid = selected["selected_idea_id"]
            for idea in (state.generated_ideas or []):
                if idea.id == sid:
                    return {
                        "selected_idea": idea,
                        "current_stage": WorkflowStage.IDEA_SELECTION,
                        "completed_agents": [*state.completed_agents, "human_approval"],
                    }
            logger.warning("selected_idea_id_not_found", idea_id=sid)
        return {
            "current_stage": WorkflowStage.IDEA_SELECTION,
            "completed_agents": [*state.completed_agents, "human_approval"],
        }

    async def _architecture_approval_node(self, state: ExHackerState) -> dict[str, Any]:
        logger.info("awaiting_architecture_review", project_id=state.project.id)
        payload = {
            "stage": "architecture_review",
            "architecture": state.architecture.model_dump() if state.architecture else None,
        }
        interrupt(payload)
        return {"current_stage": WorkflowStage.ARCHITECTURE_REVIEW}

    async def _tech_stack_approval_node(self, state: ExHackerState) -> dict[str, Any]:
        logger.info("awaiting_tech_stack_review", project_id=state.project.id)
        payload = {
            "stage": "tech_stack_review",
            "tech_stack": state.tech_stack.model_dump() if state.tech_stack else None,
        }
        interrupt(payload)
        return {"current_stage": WorkflowStage.TECH_STACK_REVIEW}

    async def _prompts_approval_node(self, state: ExHackerState) -> dict[str, Any]:
        logger.info("awaiting_prompts_review", project_id=state.project.id)
        payload = {
            "stage": "prompts_review",
            "prompts": state.prompts.model_dump() if state.prompts else None,
        }
        interrupt(payload)
        return {"current_stage": WorkflowStage.PROMPTS_REVIEW}

    async def _export_node(self, state: ExHackerState) -> dict[str, Any]:
        logger.info("workflow_completed", project_id=state.project.id)
        return {
            "current_stage": WorkflowStage.COMPLETED,
            "completed_agents": [*state.completed_agents, "export"],
            "export_data": self._generate_export_package(state),
        }

    MAX_IDEA_GENERATION_ATTEMPTS = 3

    def _route_after_validation(self, state: ExHackerState) -> str:
        if not state.validation_reports:
            attempts = state.idea_generation_attempts
            if attempts >= self.MAX_IDEA_GENERATION_ATTEMPTS:
                logger.warning(
                    "max_idea_generation_attempts_reached",
                    project_id=state.project.id,
                    attempts=attempts,
                )
                return "human_approval"
            logger.warning(
                "no_validation_reports_regenerating",
                project_id=state.project.id,
                attempt=attempts + 1,
                max_attempts=self.MAX_IDEA_GENERATION_ATTEMPTS,
            )
            return "idea_generator"
        return "human_approval"

    def _route_after_approval(self, state: ExHackerState) -> str:
        if state.selected_idea is None:
            attempts = state.idea_generation_attempts
            if attempts >= self.MAX_IDEA_GENERATION_ATTEMPTS:
                logger.warning(
                    "max_idea_generation_attempts_reached_approval",
                    project_id=state.project.id,
                    attempts=attempts,
                    ideas_count=len(state.generated_ideas or []),
                )
                return "solution_architect"
            logger.warning(
                "no_idea_selected_regenerating",
                project_id=state.project.id,
                attempt=attempts + 1,
                max_attempts=self.MAX_IDEA_GENERATION_ATTEMPTS,
            )
            return "idea_generator"
        return "solution_architect"

    # ─────────────────────────────────────────────────────────────────────────
    # Export helper
    # ─────────────────────────────────────────────────────────────────────────

    def _generate_export_package(self, state: ExHackerState) -> dict[str, Any]:
        export: dict[str, Any] = {"status": "ready"}
        if state.team_profile:
            export["team_profile"] = state.team_profile.model_dump()
        if state.challenge_intelligence:
            export["challenge_intelligence"] = state.challenge_intelligence.model_dump()
        if state.problem_analysis:
            export["problem_analysis"] = state.problem_analysis.model_dump()
        if state.opportunity_analysis:
            export["opportunity_analysis"] = state.opportunity_analysis.model_dump()
        if state.generated_ideas:
            export["ideas"] = [i.model_dump() for i in state.generated_ideas]
        if state.validation_reports:
            export["validations"] = [r.model_dump() for r in state.validation_reports]
        if state.selected_idea:
            export["selected_idea"] = state.selected_idea.model_dump()
        if state.architecture:
            export["architecture"] = state.architecture.model_dump()
        if state.tech_stack:
            export["tech_stack"] = state.tech_stack.model_dump()
        if state.prompts:
            export["prompts"] = state.prompts.model_dump()
        if state.presentation:
            export["presentation"] = state.presentation.model_dump()
        if state.pitch:
            export["pitch"] = state.pitch.model_dump()
        return export

    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────

    async def run_workflow(self, initial_state: ExHackerState) -> ExHackerState:
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        project_id = initial_state.project.id

        logger.info(
            "workflow_run_started",
            project_id=project_id,
            thread_id=thread_id,
            agents=AGENT_SEQUENCE,
        )

        try:
            async for event in self.graph.astream(initial_state, config=config):
                for node_name, node_output in event.items():
                    if isinstance(node_output, dict):
                        completed = node_output.get("completed_agents", [])
                        stage = node_output.get("current_stage", "")
                        logger.info(
                            "graph_event",
                            project_id=project_id,
                            node=node_name,
                            stage=stage,
                            completed_count=len(completed),
                        )
        except Exception as exc:
            logger.exception(
                "workflow_run_error",
                project_id=project_id,
                thread_id=thread_id,
                error=str(exc),
            )
            raise

        snapshot = await self.graph.aget_state(config)
        final_state = ExHackerState.model_validate(snapshot.values)
        logger.info(
            "workflow_run_finished",
            project_id=project_id,
            thread_id=thread_id,
            completed_agents=final_state.completed_agents,
            errors=[e.agent_name for e in final_state.errors],
        )

        # Attach thread_id and interrupt status for the caller to inspect
        final_state.agent_metadata["thread_id"] = thread_id
        if snapshot.tasks:
            final_state.agent_metadata["interrupted"] = True
        return final_state

    async def resume_workflow(
        self, thread_id: str, state: ExHackerState
    ) -> ExHackerState:
        config = {"configurable": {"thread_id": thread_id}}
        logger.info("workflow_resumed", project_id=state.project.id, thread_id=thread_id)
        async for _ in self.graph.astream(state, config=config):
            pass
        snapshot = await self.graph.aget_state(config)
        return ExHackerState.model_validate(snapshot.values)

    async def run_agent_single(
        self, state: ExHackerState, agent_name: str
    ) -> ExHackerState:
        agent = AgentRegistry.get(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found in registry")

        logger.info("single_agent_run_started", agent=agent_name, project_id=state.project.id)
        start = time.monotonic()
        state_dict = state.model_dump()
        result = await agent.run(state_dict)
        elapsed = int((time.monotonic() - start) * 1000)

        if result.success and result.output:
            state_key = AGENT_TO_STATE_KEY.get(agent_name)
            if state_key:
                if state_key == "generated_ideas":
                    state.generated_ideas = [Idea(**i) for i in result.output.get("ideas", [])]
                elif state_key == "validation_reports":
                    state.validation_reports = [
                        ValidationReport(**r) for r in result.output.get("validation_reports", [])
                    ]
                    state.generated_ideas = [Idea(**i) for i in result.output.get("ideas", [])]
                else:
                    schema = self._state_key_to_schema(state_key)
                    if schema:
                        setattr(state, state_key, schema(**result.output))
                    else:
                        setattr(state, state_key, result.output)
            logger.info(
                "single_agent_run_completed",
                agent=agent_name,
                project_id=state.project.id,
                duration_ms=elapsed,
                success=True,
            )
        else:
            error = AgentError(
                agent_name=agent_name,
                timestamp=datetime.now(UTC).isoformat(),
                message=result.error or "Unknown error",
                severity=AgentErrorSeverity.CRITICAL if agent.critical else AgentErrorSeverity.WARNING,
            )
            state.errors = [*state.errors, error]
            logger.error(
                "single_agent_run_failed",
                agent=agent_name,
                project_id=state.project.id,
                duration_ms=elapsed,
                error=result.error,
            )

        state.completed_agents = [*state.completed_agents, agent_name]
        state.current_stage = AGENT_TO_STAGE.get(agent_name, state.current_stage)
        return state

    def _state_key_to_schema(self, key: str) -> type | None:
        mapping: dict[str, type] = {
            "team_profile": TeamProfile,
            "challenge_intelligence": ChallengeIntelligence,
            "problem_analysis": ProblemAnalysis,
            "opportunity_analysis": OpportunityAnalysis,
            "architecture": ArchitecturePackage,
            "tech_stack": TechStack,
            "prompts": PromptPackage,
            "presentation": PresentationPackage,
            "pitch": PitchPackage,
        }
        return mapping.get(key)


# ─────────────────────────────────────────────────────────────────────────────
# Singleton
# ─────────────────────────────────────────────────────────────────────────────

_orchestrator: WorkflowOrchestrator | None = None


def get_orchestrator() -> WorkflowOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = WorkflowOrchestrator()
    return _orchestrator
