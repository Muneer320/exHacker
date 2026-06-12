"""
Solution Architect Agent

Purpose: Design the MVP architecture for the selected idea.
Reads:   selected_idea, tech_stack, team_profile
Writes:  architecture
"""

from typing import Type, Dict, Any

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, ArchitecturePackage


class SolutionArchitectAgent(BaseAgent):
    agent_name = "SolutionArchitectAgent"
    stage = WorkflowStage.ARCHITECTURE

    @property
    def response_schema(self) -> Type[ArchitecturePackage]:
        return ArchitecturePackage

    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "You are a specialized AI agent.\n\n"
            "ROLE: MVP Solution Architect\n\n"
            "OBJECTIVE:\n"
            "Design a complete implementation architecture for a hackathon MVP.\n"
            "The architecture must be:\n"
            "- Implementable within 48 hours by a small team\n"
            "- Clear enough that developers can immediately begin work\n"
            "- Scoped to an impressive but achievable MVP\n\n"
            "RULES:\n"
            "- Optimize for 48-hour implementation, NOT enterprise scalability.\n"
            "- Components should have single, clear responsibilities.\n"
            "- mvp_scope should have exactly 5-7 specific deliverables.\n"
            "- future_scope should have 3-5 post-hackathon enhancements.\n"
            "- Return valid JSON only. No markdown. No explanations.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "system_design": "string (2-3 sentences overview)",\n'
            '  "components": [{"name":"string","description":"string","responsibilities":["string"]}],\n'
            '  "modules": [{"name":"string","description":"string","dependencies":["string"]}],\n'
            '  "api_design": [{"endpoint":"string","method":"string","description":"string"}],\n'
            '  "database_design": {"tables":[{"table_name":"string","columns":[{"name":"string","type":"string"}]}],"relationships":["string"]},\n'
            '  "integrations": [{"service_name":"string","purpose":"string","type":"string"}],\n'
            '  "mvp_scope": ["string"],\n'
            '  "future_scope": ["string"]\n'
            "}"
        )

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        idea = state.get("selected_idea") or {}
        ts = state.get("tech_stack") or {}
        team = state.get("team_profile") or {}

        return (
            f"SELECTED IDEA: {idea.get('title', 'Unknown')}\n"
            f"DESCRIPTION: {idea.get('description', 'No description.')}\n"
            f"KEY FEATURES: {', '.join(idea.get('key_features', []))}\n"
            f"TARGET USERS: {', '.join(idea.get('target_users', []))}\n\n"
            f"TECHNOLOGY STACK:\n"
            f"  Frontend: {ts.get('frontend', 'Next.js')}\n"
            f"  Backend: {ts.get('backend', 'FastAPI')}\n"
            f"  Database: {ts.get('database', 'SQLite')}\n"
            f"  AI Stack: {', '.join(ts.get('ai_stack', []))}\n\n"
            f"TEAM SIZE: {team.get('team_size', 'Unknown') if team else 'Unknown'}\n\n"
            "Design a complete MVP architecture. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: ArchitecturePackage) -> Dict[str, Any]:
        state["architecture"] = result.model_dump()
        return state

    def mock_result(self, state: Dict[str, Any]) -> ArchitecturePackage:
        idea = state.get("selected_idea") or {}
        idea_title = idea.get("title", "Selected Solution")
        ts = state.get("tech_stack") or {}

        return ArchitecturePackage(
            system_design=(
                f"The {idea_title} architecture follows a clean separation of concerns: "
                f"a Next.js frontend communicates with a FastAPI backend via RESTful JSON APIs. "
                f"Background agent workflows run as LangGraph state machines persisted to SQLite."
            ),
            components=[
                {
                    "name": "Workflow State Engine",
                    "description": "LangGraph-orchestrated multi-agent workflow manager",
                    "responsibilities": [
                        "Execute agent nodes in defined order",
                        "Persist state to SQLite after each stage",
                        "Route conditionally based on human selection",
                        "Handle retries and error logging",
                    ],
                },
                {
                    "name": "API Gateway",
                    "description": "FastAPI router handling all client requests",
                    "responsibilities": [
                        "Validate incoming request schemas",
                        "Trigger workflow execution asynchronously",
                        "Serve current workflow state on demand",
                    ],
                },
                {
                    "name": "Frontend Dashboard",
                    "description": "Next.js App Router application with real-time UI",
                    "responsibilities": [
                        "Display workflow progress and agent outputs",
                        "Provide idea selection interface at human checkpoint",
                        "Export final artifacts as downloadable packages",
                    ],
                },
            ],
            modules=[
                {
                    "name": "llm_service",
                    "description": "Multi-provider LLM orchestration with fallback",
                    "dependencies": ["groq", "google-generativeai", "openai"],
                },
                {
                    "name": "workflow_engine",
                    "description": "LangGraph state graph compiler and runner",
                    "dependencies": ["langgraph", "sqlalchemy", "aiosqlite"],
                },
                {
                    "name": "agent_framework",
                    "description": "Base agent class and all concrete agent implementations",
                    "dependencies": ["llm_service", "pydantic"],
                },
            ],
            api_design=[
                {
                    "endpoint": "/api/v1/projects",
                    "method": "POST",
                    "description": "Create a new project and initialize workflow state",
                },
                {
                    "endpoint": "/api/v1/projects/{id}/workflow/run",
                    "method": "POST",
                    "description": "Start or resume workflow execution for a project",
                },
                {
                    "endpoint": "/api/v1/projects/{id}/workflow/state",
                    "method": "GET",
                    "description": "Retrieve current workflow state and agent outputs",
                },
                {
                    "endpoint": "/api/v1/projects/{id}/ideas/select",
                    "method": "POST",
                    "description": "Submit human idea selection to resume workflow",
                },
            ],
            database_design={
                "tables": [
                    {
                        "table_name": "projects",
                        "columns": [
                            {"name": "id", "type": "String (UUID)"},
                            {"name": "name", "type": "String"},
                            {"name": "challenge_statements", "type": "JSON"},
                            {"name": "duration_hours", "type": "Integer"},
                            {"name": "created_at", "type": "DateTime"},
                        ],
                    },
                    {
                        "table_name": "workflow_states",
                        "columns": [
                            {"name": "id", "type": "String (UUID)"},
                            {"name": "project_id", "type": "String (FK→projects)"},
                            {"name": "status", "type": "String (Enum)"},
                            {"name": "current_stage", "type": "String (Enum)"},
                            {"name": "state_json", "type": "JSON"},
                            {"name": "updated_at", "type": "DateTime"},
                        ],
                    },
                ],
                "relationships": [
                    "projects.id → workflow_states.project_id (one-to-one)",
                ],
            },
            integrations=[
                {
                    "service_name": "Groq Cloud API",
                    "purpose": "Primary ultra-fast LLM inference",
                    "type": "REST API (groq-python SDK)",
                },
                {
                    "service_name": "Google Gemini API",
                    "purpose": "Secondary fallback LLM inference",
                    "type": "REST API (google-generativeai SDK)",
                },
            ],
            mvp_scope=[
                "Project creation and persistent state management",
                "Full 10-stage automated agent workflow execution",
                "Human-in-the-loop idea selection dashboard",
                "Real-time workflow status and agent output viewer",
                "One-click export of pitch, architecture, and build artifacts",
                "Live LLM provider fallback with zero downtime",
            ],
            future_scope=[
                "WebSocket real-time streaming of agent outputs to frontend",
                "Custom agent plugin system for domain-specific workflows",
                "Multi-user collaboration with shared project workspaces",
                "Persistent history across multiple workflow runs",
            ],
        )


# Singleton instance
solution_architect_agent = SolutionArchitectAgent()
