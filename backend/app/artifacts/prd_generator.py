from app.artifacts.base import ArtifactGenerator
from app.schemas.architecture import ArchitecturePackage
from app.schemas.challenge import ChallengeIntelligence
from app.schemas.idea import Idea
from app.schemas.problem import ProblemAnalysis


class PRDGenerator(ArtifactGenerator):

    name = "prd"
    filename = "PRD.md"

    async def generate(self, state: dict) -> str:
        selected: Idea | None = state.get("selected_idea")
        problem: ProblemAnalysis | None = state.get("problem_analysis")
        challenge: ChallengeIntelligence | None = state.get("challenge_intelligence")
        state.get("opportunity_analysis")
        arch: ArchitecturePackage | None = state.get("architecture")
        project = state.get("project", {})
        project_name = project.get("name", "Hackathon Project") if isinstance(project, dict) else getattr(project, "name", "Hackathon Project")

        sections = [
            self._header(project_name),
            self._problem_statement(problem, challenge),
            self._target_users(selected, problem),
            self._user_stories(arch),
            self._success_metrics(problem, challenge),
            self._scope(arch, selected),
            self._feature_prioritization(selected, arch),
        ]

        return "\n\n".join(sections)

    def _header(self, project_name: str) -> str:
        return (
            f"# Product Requirements Document — {project_name}\n\n"
            "> This PRD defines the product vision, target users, functional requirements, "
            "and success criteria for the hackathon project."
        )

    def _problem_statement(self, problem: ProblemAnalysis | None, challenge: ChallengeIntelligence | None) -> str:
        parts = ["## Problem Statement"]
        if problem and problem.problem_definition:
            parts.append(problem.problem_definition)
        elif challenge:
            themes = challenge.themes or []
            parts.append(
                "The challenge revolves around "
                + (themes[0].lower() if themes else "an identified problem")
                + " requiring an innovative technology-driven solution."
            )
        else:
            parts.append("Problem definition pending further research.")

        if problem and problem.pain_points:
            parts.append("\n### Pain Points")
            for p in problem.pain_points:
                parts.append(f"- {p}")

        if problem and problem.assumptions:
            parts.append("\n### Key Assumptions")
            for a in problem.assumptions:
                parts.append(f"- {a}")

        return "\n".join(parts)

    def _target_users(self, selected: Idea | None, problem: ProblemAnalysis | None) -> str:
        parts = ["## Target Users"]
        if selected and selected.target_users:
            for u in selected.target_users:
                parts.append(f"- {u}")
        elif problem and problem.stakeholders:
            parts.append("Primary stakeholders identified:")
            for s in problem.stakeholders:
                parts.append(f"- {s}")
        else:
            parts.append("- Target user personas to be defined")
        return "\n".join(parts)

    def _user_stories(self, arch: ArchitecturePackage | None) -> str:
        parts = ["## User Stories"]
        if arch and arch.user_stories:
            for i, story in enumerate(arch.user_stories, 1):
                parts.append(
                    f"- **As a** {story.actor}, **I want** {story.goal}, "
                    f"**so that** {story.benefit}"
                )
        else:
            parts.append("- User stories to be drafted during implementation")
        return "\n".join(parts)

    def _success_metrics(self, problem: ProblemAnalysis | None, challenge: ChallengeIntelligence | None) -> str:
        parts = ["## Success Metrics"]
        metrics: list[str] = []

        if problem and problem.success_metrics:
            metrics.extend(problem.success_metrics)
        if challenge and challenge.evaluation_focus:
            metrics.extend(challenge.evaluation_focus)

        if metrics:
            for m in metrics:
                parts.append(f"- {m}")
        else:
            parts.append("- Core functionality working end-to-end")
            parts.append("- Smooth user experience with <2s response times")
            parts.append("- Handles demo scenarios reliably")
            parts.append("- Judges can interact with the live prototype")

        return "\n".join(parts)

    def _scope(self, arch: ArchitecturePackage | None, selected: Idea | None) -> str:
        lines = ["## Scope"]
        lines.append("")
        lines.append("### MVP (Must-Have)")
        if arch and arch.features:
            for f in arch.features:
                if f.priority.lower() in ("high", "critical", "p0", "p1"):
                    lines.append(f"- **{f.title}:** {f.description}")
        elif selected and selected.key_features:
            for f in selected.key_features:
                lines.append(f"- {f}")
        else:
            lines.append("- Core functional flow")
            lines.append("- Basic UI for primary actions")
            lines.append("- Essential API endpoints")

        lines.append("")
        lines.append("### Advanced / Stretch Goals")
        if arch and arch.features:
            for f in arch.features:
                if f.priority.lower() in ("low", "medium", "p2", "p3", "nice-to-have"):
                    lines.append(f"- **{f.title}:** {f.description}")
        else:
            lines.append("- Real-time collaboration features")
            lines.append("- Advanced analytics dashboard")
            lines.append("- Third-party integrations")
            lines.append("- Performance optimizations")

        return "\n".join(lines)

    def _feature_prioritization(self, selected: Idea | None, arch: ArchitecturePackage | None) -> str:
        lines = ["## Feature Prioritization"]
        features: list[tuple[str, str, str]] = []

        if arch and arch.features:
            for f in arch.features:
                features.append((f.title, f.description, f.priority))
        elif selected and selected.key_features:
            for f in selected.key_features:
                features.append((f, "", "medium"))

        if features:
            lines.append("")
            lines.append("| Feature | Description | Priority |")
            lines.append("|---------|-------------|----------|")
            for title, desc, priority in features:
                desc_short = (desc[:60] + "...") if len(desc) > 60 else desc
                lines.append(f"| {title} | {desc_short} | {priority} |")
        else:
            lines.append("- Feature prioritization pending")

        return "\n".join(lines)
