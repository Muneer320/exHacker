from typing import Any

from app.artifacts.base import ArtifactGenerator
from app.schemas.architecture import ArchitecturePackage
from app.schemas.idea import Idea
from app.schemas.team import TeamProfile


class ReadmeGenerator(ArtifactGenerator):

    name = "readme"
    filename = "README.md"

    async def generate(self, state: dict[str, Any]) -> str:
        team: TeamProfile | None = state.get("team_profile")
        selected: Idea | None = state.get("selected_idea")
        arch: ArchitecturePackage | None = state.get("architecture")
        project = state.get("project", {})
        project_name = project.get("name", "Hackathon Project") if isinstance(project, dict) else getattr(project, "name", "Hackathon Project")

        sections = [
            self._header(project_name),
            self._overview(arch, selected),
            self._features(selected, arch),
            self._tech_stack(state),
            self._setup_instructions(),
            self._architecture_diagram(arch),
            self._team_info(team),
        ]

        return "\n\n".join(sections)

    def _header(self, project_name: str) -> str:
        return (
            f"# {project_name}\n\n"
            f"Built for a hackathon — {project_name} aims to solve a real-world challenge "
            "with a focused, innovative approach."
        )

    def _overview(self, arch: ArchitecturePackage | None, selected: Idea | None) -> str:
        parts = ["## Project Overview"]
        if selected:
            parts.append(f"**Idea:** {selected.title}")
            parts.append(selected.description)
        if arch and arch.vision:
            parts.append(f"\n**Vision:** {arch.vision}")
        if arch and arch.product_scope:
            parts.append(f"\n**Scope:** {arch.product_scope}")
        return "\n\n".join(parts)

    def _features(self, selected: Idea | None, arch: ArchitecturePackage | None) -> str:
        lines = ["## Features"]
        seen: set[str] = set()
        if selected:
            for f in selected.key_features:
                key = f.lower().strip()
                if key not in seen:
                    lines.append(f"- {f}")
                    seen.add(key)
        if arch:
            for feature in arch.features:
                key = feature.title.lower().strip()
                if key not in seen:
                    lines.append(f"- **{feature.title}**: {feature.description}")
                    seen.add(key)
        if len(lines) == 1:
            lines.append("- Feature planning in progress")
        return "\n".join(lines)

    def _tech_stack(self, state: dict[str, Any]) -> str:
        ts = state.get("tech_stack")
        lines = ["## Tech Stack"]
        if ts:
            stack_map = {
                "Frontend": getattr(ts, "frontend", None) or ts.get("frontend") if isinstance(ts, dict) else ts.frontend,
                "Backend": getattr(ts, "backend", None) or ts.get("backend") if isinstance(ts, dict) else ts.backend,
                "Database": getattr(ts, "database", None) or ts.get("database") if isinstance(ts, dict) else ts.database,
                "Hosting": getattr(ts, "hosting", None) or ts.get("hosting") if isinstance(ts, dict) else ts.hosting,
            }
            for label, val in stack_map.items():
                if val:
                    lines.append(f"- **{label}:** {val}")

            ai_models = getattr(ts, "ai_models", None) or ts.get("ai_models", []) if isinstance(ts, dict) else ts.ai_models
            if ai_models:
                lines.append(f"- **AI Models:** {', '.join(ai_models)}")

            for attr, label in [("vector_db", "Vector DB"), ("auth_provider", "Auth")]:
                val = getattr(ts, attr, None) or (ts.get(attr) if isinstance(ts, dict) else None)
                if val:
                    lines.append(f"- **{label}:** {val}")
        else:
            lines.append("- Tech stack to be determined")
        return "\n".join(lines)

    def _setup_instructions(self) -> str:
        return (
            "## Setup Instructions\n\n"
            "### Prerequisites\n"
            "- Node.js 18+ / Python 3.11+\n"
            "- Package manager (npm / pip / uv)\n\n"
            "### Installation\n"
            "```bash\n"
            "# Clone the repository\n"
            "git clone <repo-url>\n"
            "cd <project-directory>\n\n"
            "# Install dependencies\n"
            "# Backend\n"
            "cd backend && pip install -r requirements.txt\n\n"
            "# Frontend\n"
            "cd frontend && npm install\n"
            "```\n\n"
            "### Running the Project\n"
            "```bash\n"
            "# Start backend\n"
            "cd backend && python -m uvicorn app.main:app --reload\n\n"
            "# Start frontend (separate terminal)\n"
            "cd frontend && npm run dev\n"
            "```"
        )

    def _architecture_diagram(self, arch: ArchitecturePackage | None) -> str:
        lines = ["## Architecture Diagram\n"]
        if arch and arch.architecture.components:
            lines.append("```")
            lines.append("┌─────────────────────────────────────────────┐")
            lines.append("│              Client Application             │")
            lines.append("│        (Web / Mobile / Desktop)             │")
            lines.append("└──────────────────┬──────────────────────────┘")
            lines.append("                   │")
            lines.append("                   ▼")
            lines.append("┌─────────────────────────────────────────────┐")
            lines.append("│           API Gateway / Load Balancer       │")
            lines.append("└──────────────────┬──────────────────────────┘")
            lines.append("                   │")
            lines.append("          ┌────────┴────────┐")
            lines.append("          ▼                  ▼")
            lines.append("┌──────────────────┐  ┌──────────────────┐")
            lines.append("│   Service Layer  │  │   Service Layer  │")
            lines.append("│   (REST / gRPC)  │  │   (REST / gRPC)  │")
            lines.append("└──────┬───────────┘  └──────┬───────────┘")
            lines.append("       │                      │")
            lines.append("       ▼                      ▼")
            lines.append("┌─────────────────────────────────────────────┐")
            lines.append("│              Database Layer                  │")
            lines.append("│     (PostgreSQL / MongoDB / Vector DB)      │")
            lines.append("└─────────────────────────────────────────────┘")
            lines.append("       │")
            lines.append("       ▼")
            lines.append("┌─────────────────────────────────────────────┐")
            lines.append("│         External APIs / AI Services         │")
            lines.append("└─────────────────────────────────────────────┘")
            lines.append("```")

            if arch.architecture.components:
                lines.append("\n### Components")
                for c in arch.architecture.components:
                    name = c.get("name", c.get("title", "Component"))
                    desc = c.get("description", "")
                    lines.append(f"- **{name}** — {desc}" if desc else f"- **{name}**")
        else:
            lines.append("```")
            lines.append("┌───────────┐     ┌──────────────┐     ┌───────────┐")
            lines.append("│  Client   │────▶│  API Server  │────▶│ Database  │")
            lines.append("└───────────┘     └──────────────┘     └───────────┘")
            lines.append("```")
        return "\n".join(lines)

    def _team_info(self, team: TeamProfile | None) -> str:
        lines = ["## Team"]
        if team:
            lines.append(f"- **Team Size:** {team.team_size}")
            lines.append(f"- **Experience Level:** {team.experience_level.value}")
            lines.append(f"- **Skills:** {', '.join(team.skills) if team.skills else 'TBD'}")
            lines.append(f"- **Complexity Budget:** {team.complexity_budget.value}")
        else:
            lines.append("- Team information pending")
        return "\n".join(lines)
