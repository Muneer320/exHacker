from typing import Any

from app.agents.base import AgentResult, BaseAgent


class UserProfilerAgent(BaseAgent):
    name = "user_profiler"
    description = "Analyzes team constraints and establishes project scope boundaries"
    critical = False

    async def execute(self, state: dict[str, Any]) -> AgentResult:
        team = state.get("project", {}).get("team_data", {})
        team_size = team.get("team_size", 4)
        duration = team.get("duration_hours", 24)
        skills = team.get("skills", [])
        experience = team.get("experience_level", "intermediate")

        if not skills:
            return AgentResult(
                success=False,
                error="Team skills list is empty",
            )

        # Capacity scoring logic
        capacity = min(100.0, (team_size / 5.0) * 40 + (duration / 48.0) * 30 + len(skills) * 5)
        if experience == "advanced":
            capacity += 20
        elif experience == "beginner":
            capacity -= 10

        complexity_budget = "medium"
        if capacity >= 80:
            complexity_budget = "high"
        elif capacity <= 50:
            complexity_budget = "low"

        recommended_scope = "advanced_mvp" if capacity >= 70 else "mvp"

        return AgentResult(
            success=True,
            output={
                "complexity_budget": complexity_budget,
                "recommended_scope": recommended_scope,
                "risk_tolerance": (
                    "high" if capacity >= 80 else "medium" if capacity >= 50 else "low"
                ),
                "execution_capacity_score": round(capacity, 1),
                "team_size": team_size,
                "duration_hours": duration,
                "skills": skills,
                "experience_level": experience,
            },
        )
