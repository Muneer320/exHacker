from typing import Any

from app.artifacts.base import ArtifactGenerator
from app.schemas.architecture import ApiDefinition, ArchitecturePackage
from app.schemas.idea import Idea
from app.schemas.tech_stack import TechStack


class ArchitectureGenerator(ArtifactGenerator):

    name = "architecture"
    filename = "ARCHITECTURE.md"

    async def generate(self, state: dict[str, Any]) -> str:
        arch: ArchitecturePackage | None = state.get("architecture")
        tech_stack: TechStack | None = state.get("tech_stack")
        selected: Idea | None = state.get("selected_idea")
        project = state.get("project", {})
        project_name = project.get("name", "Hackathon Project") if isinstance(project, dict) else getattr(project, "name", "Hackathon Project")

        sections = [
            self._header(project_name),
            self._system_overview(arch, selected),
            self._component_diagram(arch),
            self._data_flow(arch),
            self._api_endpoints(arch),
            self._database_schema(arch),
            self._technology_decisions(tech_stack, arch),
        ]

        return "\n\n".join(sections)

    def _header(self, project_name: str) -> str:
        return (
            f"# Architecture Document — {project_name}\n\n"
            "> This document describes the system architecture, component interactions, "
            "data flow, API surface, and technology decisions for the project."
        )

    def _system_overview(self, arch: ArchitecturePackage | None, selected: Idea | None) -> str:
        parts = ["## System Overview"]
        if arch and arch.vision:
            parts.append(f"**Vision:** {arch.vision}")
        if selected:
            parts.append(f"**Project:** {selected.title} — {selected.description}")
        if arch and arch.product_scope:
            parts.append(f"\n**Scope:** {arch.product_scope}")
        if not arch and not selected:
            parts.append("System architecture is being defined.")
        return "\n\n".join(parts)

    def _component_diagram(self, arch: ArchitecturePackage | None) -> str:
        lines = ["## Component Diagram\n"]
        lines.append("```")

        if arch and arch.architecture.components:
            comps = arch.architecture.components
            conns = arch.architecture.connections if arch.architecture.connections else []

            lines.append("┌─────────────────────────────────────────────────────┐")
            lines.append("│                  Presentation Layer                  │")
            lines.append("│          (Frontend / Client Application)             │")
            lines.append("└───────────────────────┬─────────────────────────────┘")
            lines.append("                        │")
            lines.append("                        ▼")
            lines.append("┌─────────────────────────────────────────────────────┐")
            lines.append("│                   API Gateway                       │")
            lines.append("│             (Authentication / Routing)              │")
            lines.append("└───────────────────────┬─────────────────────────────┘")
            lines.append("                        │")
            lines.append("          ┌─────────────┴──────────────┐")
            lines.append("          ▼                            ▼")
            lines.append("┌──────────────────┐     ┌──────────────────────────┐")
            lines.append("│  Business Logic  │     │  AI / ML Service Layer   │")
            lines.append("│   (Core APIs)    │     │  (LLM / Vector Search)   │")
            lines.append("└──────┬───────────┘     └──────────┬───────────────┘")
            lines.append("       │                             │")
            lines.append("       ▼                             ▼")
            lines.append("┌─────────────────────────────────────────────────────┐")
            lines.append("│                   Data Layer                       │")
            lines.append("│    (SQL Database / Cache / Object Storage)          │")
            lines.append("└─────────────────────────────────────────────────────┘")
            lines.append("       │")
            lines.append("       ▼")
            lines.append("┌─────────────────────────────────────────────────────┐")
            lines.append("│            External Integrations / APIs             │")
            lines.append("└─────────────────────────────────────────────────────┘")
            lines.append("```")

            lines.append("\n### Component Descriptions")
            for c in comps:
                name = c.get("name", c.get("title", "Component"))
                desc = c.get("description", "")
                tech = c.get("technology", "")
                if desc and tech:
                    lines.append(f"- **{name}** — {desc} (_{tech}_)")
                elif desc:
                    lines.append(f"- **{name}** — {desc}")
                else:
                    lines.append(f"- **{name}**")

            if conns:
                lines.append("\n### Connections")
                for conn in conns:
                    source = conn.get("source", conn.get("from", "?"))
                    target = conn.get("target", conn.get("to", "?"))
                    protocol = conn.get("protocol", conn.get("type", ""))
                    label = f" via {protocol}" if protocol else ""
                    lines.append(f"- **{source}** → **{target}**{label}")
        else:
            lines.append("┌───────────┐     ┌──────────────┐     ┌───────────┐")
            lines.append("│  Client   │────▶│  API Server  │────▶│ Database  │")
            lines.append("└───────────┘     └──────┬─────────┘     └───────────┘")
            lines.append("                        │")
            lines.append("                        ▼")
            lines.append("                  ┌──────────────┐")
            lines.append("                  │  AI Service  │")
            lines.append("                  └──────────────┘")
            lines.append("```")
            lines.append("\n> Detailed component diagram pending architecture definition.")

        return "\n".join(lines)

    def _data_flow(self, arch: ArchitecturePackage | None) -> str:
        lines = ["## Data Flow"]
        if arch and arch.architecture.description:
            lines.append("")
            lines.append(arch.architecture.description)

        lines.append("")
        lines.append("```")
        lines.append("User Action")
        lines.append("    │")
        lines.append("    ▼")
        lines.append("Client sends request  ──────▶  API Gateway validates & routes")
        lines.append("                                        │")
        lines.append("                                        ▼")
        lines.append("                              Business Logic processes")
        lines.append("                                        │")
        lines.append("                         ┌──────────────┼──────────────┐")
        lines.append("                         ▼              ▼              ▼")
        lines.append("                    Read/Write     AI Inference    External API")
        lines.append("                    Database       (LLM / Vector)  Call")
        lines.append("                         │              │              │")
        lines.append("                         └──────────────┼──────────────┘")
        lines.append("                                        ▼")
        lines.append("                              Response formatted & returned")
        lines.append("                                        │")
        lines.append("                                        ▼")
        lines.append("Client receives response  ◄─────────  API Gateway")
        lines.append("```")
        return "\n".join(lines)

    def _api_endpoints(self, arch: ArchitecturePackage | None) -> str:
        lines = ["## API Endpoints"]
        endpoints: list[ApiDefinition] = []

        if arch and arch.api_design:
            endpoints = arch.api_design

        if endpoints:
            lines.append("")
            lines.append("| Method | Path | Description |")
            lines.append("|--------|------|-------------|")
            for ep in endpoints:
                method = ep.method.upper()
                path = ep.path
                desc = ep.description or ""
                lines.append(f"| {method} | {path} | {desc} |")
        else:
            lines.append("")
            lines.append("| Method | Path | Description |")
            lines.append("|--------|------|-------------|")
            lines.append("| GET | /api/health | Health check |")
            lines.append("| POST | /api/v1/resource | Create resource |")
            lines.append("| GET | /api/v1/resource/{id} | Get resource |")
            lines.append("| PUT | /api/v1/resource/{id} | Update resource |")
            lines.append("| DELETE | /api/v1/resource/{id} | Delete resource |")

        return "\n".join(lines)

    def _database_schema(self, arch: ArchitecturePackage | None) -> str:
        lines = ["## Database Schema"]
        db = arch.database_schema if arch else None

        if db and db.tables:
            for table in db.tables:
                table_name = table.get("name", table.get("table", "unknown"))
                lines.append("")
                lines.append(f"### {table_name}")
                columns = table.get("columns", table.get("fields", []))
                if columns and isinstance(columns, list):
                    lines.append("| Column | Type | Constraints | Description |")
                    lines.append("|--------|------|-------------|-------------|")
                    for col in columns:
                        if isinstance(col, dict):
                            name = col.get("name", "?")
                            col_type = col.get("type", "?")
                            constraints = col.get("constraints", col.get("nullable", ""))
                            desc = col.get("description", "")
                            lines.append(f"| {name} | {col_type} | {constraints} | {desc} |")
                        else:
                            lines.append(f"| {col} |  |  |  |")

            if db.relationships:
                lines.append("\n### Relationships")
                for rel in db.relationships:
                    if isinstance(rel, dict):
                        from_table = rel.get("from", rel.get("source", "?"))
                        to_table = rel.get("to", rel.get("target", "?"))
                        rel_type = rel.get("type", rel.get("relation", "references"))
                        lines.append(f"- **{from_table}** {rel_type} **{to_table}**")
                    else:
                        lines.append(f"- {rel}")
        else:
            lines.append("")
            lines.append("| Table | Purpose |")
            lines.append("|-------|---------|")
            lines.append("| users | User accounts and profiles |")
            lines.append("| projects | Project records and metadata |")
            lines.append("| sessions | User sessions and auth tokens |")

            lines.append("\n### Relationships")
            lines.append("- **users** 1──N **projects**")
            lines.append("- **users** 1──N **sessions**")

        return "\n".join(lines)

    def _technology_decisions(self, tech_stack: TechStack | None, arch: ArchitecturePackage | None) -> str:
        lines = ["## Technology Decisions"]

        if tech_stack:
            lines.append("")
            lines.append("| Layer | Choice |")
            lines.append("|-------|--------|")
            stack_items = [
                ("Frontend", getattr(tech_stack, "frontend", None) or (tech_stack.get("frontend") if isinstance(tech_stack, dict) else None)),
                ("Backend", getattr(tech_stack, "backend", None) or (tech_stack.get("backend") if isinstance(tech_stack, dict) else None)),
                ("Database", getattr(tech_stack, "database", None) or (tech_stack.get("database") if isinstance(tech_stack, dict) else None)),
                ("Hosting", getattr(tech_stack, "hosting", None) or (tech_stack.get("hosting") if isinstance(tech_stack, dict) else None)),
            ]
            for label, val in stack_items:
                if val:
                    lines.append(f"| {label} | {val} |")
        else:
            lines.append("")
            lines.append("- Technology decisions pending finalization.")

        if arch and arch.integrations:
            lines.append("\n### Integrations")
            for integ in arch.integrations:
                lines.append(f"- **{integ.name}** — {integ.description} (type: {integ.type})")

        return "\n".join(lines)
