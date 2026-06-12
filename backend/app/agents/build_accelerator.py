"""
Build Accelerator Agent

Purpose: Convert architecture into actionable execution tasks and AI prompts.
Reads:   architecture, tech_stack, selected_idea
Writes:  build_package, prompt_package
"""

from typing import Type, Dict, Any

from pydantic import BaseModel

from app.agents.base import BaseAgent
from app.schemas.state import WorkflowStage, BuildPackage, PromptPackage


class BuildAcceleratorOutput(BaseModel):
    """Combined output of build_package + prompt_package."""
    build_package: BuildPackage
    prompt_package: PromptPackage


class BuildAcceleratorAgent(BaseAgent):
    agent_name = "BuildAcceleratorAgent"
    stage = WorkflowStage.BUILD_ACCELERATOR

    @property
    def response_schema(self) -> Type[BuildAcceleratorOutput]:
        return BuildAcceleratorOutput

    def build_system_prompt(self, state: Dict[str, Any]) -> str:
        return (
            "You are a specialized AI agent.\n\n"
            "ROLE: Hackathon Build Acceleration Coach\n\n"
            "OBJECTIVE:\n"
            "Convert an architecture document into two deliverables:\n"
            "1. build_package: Specific, ordered implementation tasks per domain.\n"
            "2. prompt_package: Ready-to-paste AI coding prompts for each task.\n\n"
            "RULES FOR build_package:\n"
            "- Tasks must be specific — not generic (e.g., 'Build auth form' not 'Build frontend').\n"
            "- Each domain must have at least 4 tasks.\n"
            "- Tasks should be ordered logically — dependencies first.\n\n"
            "RULES FOR prompt_package:\n"
            "- Prompts must be self-contained and immediately usable.\n"
            "- Each prompt should produce working, production-quality code.\n"
            "- Be specific about file paths, function names, and schemas.\n"
            "- Return valid JSON only. No markdown. No explanations.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "build_package": {\n'
            '    "frontend_tasks": ["string"],\n'
            '    "backend_tasks": ["string"],\n'
            '    "database_tasks": ["string"],\n'
            '    "testing_tasks": ["string"],\n'
            '    "deployment_tasks": ["string"]\n'
            "  },\n"
            '  "prompt_package": {\n'
            '    "frontend_prompts": ["string"],\n'
            '    "backend_prompts": ["string"],\n'
            '    "database_prompts": ["string"],\n'
            '    "testing_prompts": ["string"],\n'
            '    "deployment_prompts": ["string"]\n'
            "  }\n"
            "}"
        )

    def build_user_prompt(self, state: Dict[str, Any]) -> str:
        arch = state.get("architecture") or {}
        ts = state.get("tech_stack") or {}
        idea = state.get("selected_idea") or {}

        components = "\n".join(
            f"- {c.get('name', '')}: {c.get('description', '')}"
            for c in arch.get("components", [])
        )
        api_endpoints = "\n".join(
            f"- {e.get('method', 'GET')} {e.get('endpoint', '')}: {e.get('description', '')}"
            for e in arch.get("api_design", [])
        )
        mvp_scope = "\n".join(f"- {s}" for s in arch.get("mvp_scope", []))

        return (
            f"IDEA: {idea.get('title', 'Unknown')}\n\n"
            f"STACK:\n"
            f"  Frontend: {ts.get('frontend', 'Next.js')}\n"
            f"  Backend: {ts.get('backend', 'FastAPI')}\n"
            f"  Database: {ts.get('database', 'SQLite')}\n\n"
            f"COMPONENTS:\n{components}\n\n"
            f"API ENDPOINTS:\n{api_endpoints}\n\n"
            f"MVP SCOPE:\n{mvp_scope}\n\n"
            "Generate the build_package and prompt_package. "
            "Return the JSON object following the schema exactly."
        )

    def apply_result(self, state: Dict[str, Any], result: BuildAcceleratorOutput) -> Dict[str, Any]:
        state["build_package"] = result.build_package.model_dump()
        state["prompt_package"] = result.prompt_package.model_dump()
        return state

    def mock_result(self, state: Dict[str, Any]) -> BuildAcceleratorOutput:
        idea = state.get("selected_idea") or {}
        title = idea.get("title", "the project")
        ts = state.get("tech_stack") or {}
        frontend = ts.get("frontend", "Next.js")
        backend = ts.get("backend", "FastAPI")

        return BuildAcceleratorOutput(
            build_package=BuildPackage(
                frontend_tasks=[
                    f"Initialize {frontend} project with Tailwind CSS and TypeScript",
                    "Create global design system: colors, typography, spacing tokens in globals.css",
                    "Build ProjectCard component with status indicators and hover animations",
                    "Implement WorkflowProgressBar showing current agent stage",
                    "Build IdeaSelectionModal for human-in-the-loop checkpoint",
                    "Create OutputViewer accordion showing each agent's structured output",
                    "Add ExportButton that downloads final artifacts as ZIP",
                ],
                backend_tasks=[
                    f"Initialize {backend} entrypoint with CORS, health check, and v1 router",
                    "Implement SQLAlchemy models: Project, WorkflowState, AgentRun",
                    "Create async DB session manager with lifespan context",
                    "Wire LangGraph workflow engine with all 10 agent nodes",
                    "Implement POST /projects endpoint with project + workflow initialization",
                    "Implement POST /projects/{id}/workflow/run with async task runner",
                    "Implement GET /projects/{id}/workflow/state for polling endpoint",
                    "Implement POST /projects/{id}/ideas/select for human checkpoint",
                ],
                database_tasks=[
                    "Create SQLite database initialization script (create_all tables)",
                    "Write seed data fixture for development testing",
                    "Validate async write performance under concurrent agent execution",
                ],
                testing_tasks=[
                    "Write pytest fixtures for in-memory SQLite test database",
                    "Write unit tests for all 10 agent mock_result() methods",
                    "Write integration test for full workflow run with mock LLM",
                    "Write API endpoint tests for project creation and idea selection",
                ],
                deployment_tasks=[
                    "Create Dockerfile for FastAPI backend with uv package manager",
                    "Create Vercel project config (vercel.json) for Next.js frontend",
                    "Write docker-compose.yml for local full-stack development",
                    "Add GitHub Actions CI workflow running pytest on every push",
                ],
            ),
            prompt_package=PromptPackage(
                frontend_prompts=[
                    f"Build a React component called WorkflowProgressStepper using Next.js and Tailwind CSS. "
                    f"It should display a horizontal stepper with 10 stages matching the exHacker workflow: "
                    f"Challenge Intelligence, Problem Analysis, Opportunity Discovery, Idea Generation, "
                    f"Idea Validation, Human Selection, Tech Stack, Architecture, Build Accelerator, "
                    f"Presentation, Pitch. Each step should show active/completed/pending states with "
                    f"animated transitions. Use deep purple (#7C3AED) as the active color.",
                ],
                backend_prompts=[
                    f"Write a FastAPI POST endpoint at /api/v1/projects that accepts a JSON body with "
                    f"'name' (str), 'challenge_statements' (list[str]), and 'duration_hours' (int). "
                    f"It should create a new Project record in SQLite using SQLAlchemy async session, "
                    f"initialize a WorkflowState record with status='created', and return the project ID "
                    f"and initial state. Use Pydantic v2 for request validation.",
                ],
                database_prompts=[
                    "Write a SQLAlchemy async model for a 'workflow_states' table with columns: "
                    "id (String UUID PK), project_id (String FK), status (String), "
                    "current_stage (String), state_json (JSON), created_at (DateTime), updated_at (DateTime). "
                    "Include a relationship back to the Project model. Use declarative_base.",
                ],
                testing_prompts=[
                    "Write a pytest fixture that creates an in-memory SQLite database using SQLAlchemy "
                    "async engine (aiosqlite driver), runs create_all on all models, and yields an "
                    "AsyncSession. The fixture should be scoped to 'function' level for test isolation.",
                ],
                deployment_prompts=[
                    "Write a production Dockerfile for a FastAPI application using the official Python 3.12 "
                    "slim image and uv for package management. Copy pyproject.toml first, install "
                    "dependencies, then copy the application source. Expose port 8000. "
                    "The CMD should run: uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000",
                ],
            ),
        )


# Singleton instance
build_accelerator_agent = BuildAcceleratorAgent()
