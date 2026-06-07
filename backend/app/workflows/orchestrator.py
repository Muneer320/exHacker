from typing import Any

import structlog
from langgraph.graph import StateGraph

from app.agents.registry import AgentRegistry
from app.schemas.state import AgentError, AgentErrorSeverity, ExHackerState

logger = structlog.get_logger()


class WorkflowOrchestrator:
    def __init__(self) -> None:
        self.graph = self._build_graph()

    def _build_graph(self) -> Any:
        workflow = StateGraph(ExHackerState)

        workflow.add_node("user_profiler", self._run_agent("user_profiler"))
        workflow.add_node("challenge_intelligence", self._run_agent("challenge_intelligence"))
        workflow.add_node("problem_analyst", self._run_agent("problem_analyst"))
        workflow.add_node("opportunity_planner", self._run_agent("opportunity_planner"))
        workflow.add_node("idea_generator", self._run_agent("idea_generator"))
        workflow.add_node("idea_validator", self._run_agent("idea_validator"))
        workflow.add_node("solution_architect", self._run_agent("solution_architect"))
        workflow.add_node("tech_stack_advisor", self._run_agent("tech_stack_advisor"))
        workflow.add_node("build_accelerator", self._run_agent("build_accelerator"))
        workflow.add_node("presentation_agent", self._run_agent("presentation_agent"))
        workflow.add_node("pitch_coach", self._run_agent("pitch_coach"))

        workflow.set_entry_point("user_profiler")

        workflow.add_edge("user_profiler", "challenge_intelligence")
        workflow.add_edge("challenge_intelligence", "problem_analyst")
        workflow.add_edge("problem_analyst", "opportunity_planner")
        workflow.add_edge("opportunity_planner", "idea_generator")
        workflow.add_edge("idea_generator", "idea_validator")
        workflow.add_edge("idea_validator", "solution_architect")
        workflow.add_edge("solution_architect", "tech_stack_advisor")
        workflow.add_edge("tech_stack_advisor", "build_accelerator")
        workflow.add_edge("build_accelerator", "presentation_agent")
        workflow.add_edge("presentation_agent", "pitch_coach")

        graph = workflow.compile()
        return graph

    def _run_agent(self, agent_name: str) -> Any:
        async def _run(state: ExHackerState) -> dict[str, Any]:
            agent = AgentRegistry.get(agent_name)
            if not agent:
                return {"errors": [AgentError(
                    agent_name=agent_name,
                    timestamp="",
                    message=f"Agent {agent_name} not found in registry",
                    severity=AgentErrorSeverity.CRITICAL,
                )]}

            state_dict = state.model_dump()
            result = await agent.run(state_dict)

            update: dict[str, Any] = {}
            update["completed_agents"] = [*state.completed_agents, agent_name]

            if result.success and result.output:
                update[agent_name] = result.output
            else:
                error = AgentError(
                    agent_name=agent_name,
                    timestamp="",
                    message=result.error or "Unknown error",
                    severity=(
                        AgentErrorSeverity.CRITICAL
                        if agent.critical
                        else AgentErrorSeverity.WARNING
                    ),
                )
                update["errors"] = [*state.errors, error]
                if agent.critical:
                    return update

            return update

        return _run

    async def run_workflow(self, initial_state: ExHackerState) -> ExHackerState:
        logger.info("workflow_started", project_id=initial_state.project.id)
        events: list[ExHackerState] = []
        async for event in self.graph.astream(initial_state):
            events.append(event)
        final_state = events[-1] if events else initial_state
        logger.info("workflow_completed", project_id=initial_state.project.id)
        return final_state

    async def run_agent_single(
        self, state: ExHackerState, agent_name: str
    ) -> ExHackerState:
        agent = AgentRegistry.get(agent_name)
        if not agent:
            raise ValueError(f"Agent {agent_name} not found")

        state_dict = state.model_dump()
        result = await agent.run(state_dict)

        if result.success and result.output:
            setattr(state, agent_name, result.output)
        else:
            error = AgentError(
                agent_name=agent_name,
                timestamp="",
                message=result.error or "Unknown error",
                severity=(
                    AgentErrorSeverity.CRITICAL
                    if agent.critical
                    else AgentErrorSeverity.WARNING
                ),
            )
            state.errors = [*state.errors, error]

        state.completed_agents = [*state.completed_agents, agent_name]
        return state
