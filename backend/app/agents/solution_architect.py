import json
from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.prompts.solution_architect import ARCHITECTURE_TEMPLATE, SYSTEM_PROMPT
from app.services.llm import LLMService, llm_service


class SolutionArchitectAgent(BaseAgent):
    name = "solution_architect"
    description = "Designs complete project blueprint from selected idea"
    critical = True

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__()
        self._llm = llm or llm_service

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        selected = state.get("selected_idea", {})
        profiler = state.get("user_profiler", {})

        if not selected or not selected.get("id"):
            # Try to find selected idea from generated ideas
            ideas = state.get("idea_generator", {}).get("ideas", [])
            validated = state.get("idea_validator", {}).get("ideas", [])
            selected = validated[0] if validated else (ideas[0] if ideas else {})
            if not selected:
                return AgentResult(
                    success=False,
                    error="No selected idea available",
                )

        team_data = state.get("project", {}).get("team_data", {})

        user_prompt = ARCHITECTURE_TEMPLATE.format(
            idea_title=selected.get("title", "Untitled"),
            idea_description=selected.get("description", ""),
            target_users=", ".join(selected.get("target_users", [])),
            key_features=", ".join(selected.get("key_features", [])),
            innovation=selected.get("innovation_score", 0),
            feasibility=selected.get("feasibility_score", 0),
            team_size=team_data.get("team_size", 4),
            duration_hours=team_data.get("duration_hours", 24),
            skills=", ".join(profiler.get("skills", team_data.get("skills", []))),
            complexity_budget=profiler.get("complexity_budget", "medium"),
            recommended_scope=profiler.get("recommended_scope", "mvp"),
        )

        result_text = await self._llm.generate(SYSTEM_PROMPT, user_prompt)

        try:
            arch = json.loads(result_text)
        except json.JSONDecodeError:
            arch = {}

        return AgentResult(
            success=True,
            output={
                "vision": arch.get("vision", selected.get("description", "")),
                "product_scope": arch.get("product_scope", "MVP"),
                "features": [
                    {
                        "title": f.get("title", ""),
                        "description": f.get("description", ""),
                        "priority": f.get("priority", "medium"),
                    }
                    for f in arch.get("features", [])
                ],
                "user_stories": [
                    {
                        "actor": u.get("actor", ""),
                        "goal": u.get("goal", ""),
                        "benefit": u.get("benefit", ""),
                    }
                    for u in arch.get("user_stories", [])
                ],
                "architecture": {
                    "description": arch.get("architecture", {}).get("description", ""),
                    "components": arch.get("architecture", {}).get("components", []),
                    "connections": arch.get("architecture", {}).get("connections", []),
                },
                "api_design": [
                    {
                        "path": a.get("path", ""),
                        "method": a.get("method", "GET"),
                        "description": a.get("description", ""),
                        "request_body": a.get("request_body"),
                        "response_body": a.get("response_body"),
                    }
                    for a in arch.get("api_design", [])
                ],
                "database_schema": {
                    "tables": arch.get("database_schema", {}).get("tables", []),
                    "relationships": arch.get("database_schema", {}).get("relationships", []),
                },
                "integrations": [
                    {
                        "name": i.get("name", ""),
                        "description": i.get("description", ""),
                        "type": i.get("type", "api"),
                    }
                    for i in arch.get("integrations", [])
                ],
            },
        )
