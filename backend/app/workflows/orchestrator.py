import time
from typing import Any
from uuid import uuid4

import structlog
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

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

WORKFLOW_EDGES: list[tuple[str, str]] = [
    ("user_profiler", "challenge_intelligence"),
    ("challenge_intelligence", "problem_analyst"),
    ("problem_analyst", "opportunity_planner"),
    ("opportunity_planner", "idea_generator"),
    ("idea_generator", "idea_validator"),
]

HUMAN_APPROVAL_AGENTS = {"idea_validator"}


class WorkflowOrchestrator:
    def __init__(self) -> None:
        self._checkpointer = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> Any:
        workflow = StateGraph(ExHackerState)

        for agent_name in AGENT_TO_STAGE:
            workflow.add_node(agent_name, self._make_agent_node(agent_name))

        workflow.add_node("human_approval", self._human_approval_node)
        workflow.add_node("solution_architect", self._make_agent_node("solution_architect"))
        workflow.add_node("tech_stack_advisor", self._make_agent_node("tech_stack_advisor"))
        workflow.add_node("build_accelerator", self._make_agent_node("build_accelerator"))
        workflow.add_node("presentation_agent", self._make_agent_node("presentation_agent"))
        workflow.add_node("pitch_coach", self._make_agent_node("pitch_coach"))
        workflow.add_node("export", self._export_node)

        workflow.set_entry_point("user_profiler")

        for src, dst in WORKFLOW_EDGES:
            workflow.add_edge(src, dst)

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

        workflow.add_edge("solution_architect", "tech_stack_advisor")
        workflow.add_edge("tech_stack_advisor", "build_accelerator")
        workflow.add_edge("build_accelerator", "presentation_agent")
        workflow.add_edge("presentation_agent", "pitch_coach")
        workflow.add_edge("pitch_coach", "export")

        workflow.set_finish_point("export")

        return workflow.compile(checkpointer=self._checkpointer)

    def _make_agent_node(self, agent_name: str) -> Any:
        async def _run(state: ExHackerState) -> dict[str, Any]:
            agent = AgentRegistry.get(agent_name)
            if not agent:
                return {"errors": [AgentError(
                    agent_name=agent_name,
                    timestamp="",
                    message=f"Agent {agent_name} not found",
                    severity=AgentErrorSeverity.CRITICAL,
                )]}

            start = time.monotonic()
            logger.info("agent_started", agent=agent_name)
            state_dict = state.model_dump()
            result = await agent.run(state_dict)
            elapsed = int((time.monotonic() - start) * 1000)
            logger.info("agent_completed", agent=agent_name, duration_ms=elapsed, success=result.success)

            update: dict[str, Any] = {
                "completed_agents": [*state.completed_agents, agent_name],
                "current_stage": AGENT_TO_STAGE.get(agent_name, state.current_stage),
            }

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
                    timestamp="",
                    message=result.error or "Unknown error",
                    severity=AgentErrorSeverity.CRITICAL if agent.critical else AgentErrorSeverity.WARNING,
                )
                update["errors"] = [*state.errors, error]
                if agent.critical:
                    return update

            if result.metadata:
                update["agent_metadata"] = {
                    **state.agent_metadata,
                    agent_name: {"duration_ms": elapsed, **result.metadata},
                }

            return update

        return _run

    async def _human_approval_node(self, state: ExHackerState) -> dict[str, Any]:
        logger.info("waiting_for_human_approval", project_id=state.project.id)
        return {
            "current_stage": WorkflowStage.IDEA_SELECTION,
            "completed_agents": [*state.completed_agents, "human_approval"],
        }

    async def _export_node(self, state: ExHackerState) -> dict[str, Any]:
        logger.info("workflow_completed", project_id=state.project.id)
        return {
            "current_stage": WorkflowStage.COMPLETED,
            "completed_agents": [*state.completed_agents, "export"],
            "export_data": self._generate_export_package(state),
        }

    def _route_after_validation(self, state: ExHackerState) -> str:
        if not state.validation_reports:
            return "idea_generator"
        return "human_approval"

    def _route_after_approval(self, state: ExHackerState) -> str:
        if state.selected_idea is None:
            return "idea_generator"
        return "solution_architect"

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

    async def run_workflow(self, initial_state: ExHackerState) -> ExHackerState:
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        logger.info("workflow_started", project_id=initial_state.project.id, thread_id=thread_id)
        events: list[dict[str, Any]] = []
        async for event in self.graph.astream(initial_state, config=config):
            events.append(event)
        snapshot = await self.graph.aget_state(config)
        final_state = ExHackerState.model_validate(snapshot.values)
        logger.info("workflow_completed", project_id=initial_state.project.id, thread_id=thread_id)
        return final_state

    async def resume_workflow(
        self, thread_id: str, state: ExHackerState
    ) -> ExHackerState:
        config = {"configurable": {"thread_id": thread_id}}
        logger.info("workflow_resumed", project_id=state.project.id, thread_id=thread_id)
        events: list[dict[str, Any]] = []
        async for event in self.graph.astream(state, config=config):
            events.append(event)
        snapshot = await self.graph.aget_state(config)
        return ExHackerState.model_validate(snapshot.values)

    async def run_agent_single(
        self, state: ExHackerState, agent_name: str
    ) -> ExHackerState:
        agent = AgentRegistry.get(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")

        state_dict = state.model_dump()
        result = await agent.run(state_dict)

        if result.success and result.output:
            state_key = AGENT_TO_STATE_KEY.get(agent_name)
            if state_key:
                if state_key == "generated_ideas":
                    state.generated_ideas = [Idea(**i) for i in result.output.get("ideas", [])]
                elif state_key == "validation_reports":
                    state.validation_reports = [ValidationReport(**r) for r in result.output.get("validation_reports", [])]
                    state.generated_ideas = [Idea(**i) for i in result.output.get("ideas", [])]
                else:
                    schema = self._state_key_to_schema(state_key)
                    if schema:
                        setattr(state, state_key, schema(**result.output))
                    else:
                        setattr(state, state_key, result.output)
        else:
            error = AgentError(
                agent_name=agent_name,
                timestamp="",
                message=result.error or "Unknown error",
                severity=AgentErrorSeverity.CRITICAL if agent.critical else AgentErrorSeverity.WARNING,
            )
            state.errors = [*state.errors, error]

        state.completed_agents = [*state.completed_agents, agent_name]
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


_orchestrator: WorkflowOrchestrator | None = None


def get_orchestrator() -> WorkflowOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = WorkflowOrchestrator()
    return _orchestrator
