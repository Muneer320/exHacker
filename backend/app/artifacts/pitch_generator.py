from app.artifacts.base import ArtifactGenerator
from app.schemas.architecture import ArchitecturePackage
from app.schemas.idea import Idea
from app.schemas.pitch import PitchPackage
from app.schemas.presentation import PresentationPackage, Slide
from app.schemas.problem import ProblemAnalysis
from app.schemas.team import TeamProfile


class PitchGenerator(ArtifactGenerator):

    name = "pitch"
    filename = "PITCH_DECK.md"

    async def generate(self, state: dict) -> str:
        pitch: PitchPackage | None = state.get("pitch")
        presentation: PresentationPackage | None = state.get("presentation")
        arch: ArchitecturePackage | None = state.get("architecture")
        selected: Idea | None = state.get("selected_idea")
        problem: ProblemAnalysis | None = state.get("problem_analysis")
        team: TeamProfile | None = state.get("team_profile")
        project = state.get("project", {})
        project_name = project.get("name", "Hackathon Project") if isinstance(project, dict) else getattr(project, "name", "Hackathon Project")

        sections = [
            self._header(project_name),
            self._slide_by_slide(presentation, selected, project_name),
            self._elevator_pitches(pitch),
            self._demo_script(pitch, presentation),
            self._qa_preparation(pitch),
            self._key_talking_points(selected, problem, arch, team),
        ]

        return "\n\n".join(sections)

    def _header(self, project_name: str) -> str:
        return (
            f"# Pitch Deck — {project_name}\n\n"
            "> Complete pitch preparation including slide-by-slide content, "
            "elevator pitches, demo script, and Q&A preparation."
        )

    def _slide_by_slide(self, presentation: PresentationPackage | None, selected: Idea | None, project_name: str) -> str:
        lines = ["## Slide-by-Slide Content"]
        slides: list[Slide] = []

        if presentation and presentation.slides:
            slides = presentation.slides

        if slides:
            for i, slide in enumerate(slides, 1):
                lines.append("")
                lines.append(f"### Slide {i}: {slide.title}")
                lines.append(f"**Type:** {slide.type}")
                lines.append("")
                lines.append(slide.content)
        else:
            default_slides = [
                ("Title Slide", f"**{project_name}**\n\nA hackathon project by Team"),
                ("Problem", "Describe the problem in one clear sentence.\n\n**Hook:** Start with a relatable pain point."),
                ("Solution", "What we built and why it's different.\n\n**Key message:** Our solution in one sentence."),
                ("How It Works", "Walk through the core flow.\n- Step 1: User action\n- Step 2: System processes\n- Step 3: Value delivered"),
                ("Architecture", "Show the high-level system diagram.\n- Frontend → API → Database → AI Services\n- Highlight technical wow factor"),
                ("Demo", "Live walkthrough of the working prototype.\n- Start with landing page\n- Show core action\n- Demonstrate result"),
                ("Technical Highlights", "What makes this technically impressive.\n- Novel approach or algorithm\n- Clever optimization\n- Real-time / AI / scale capability"),
                ("Team", "Who we are and why we can execute.\n- Relevant skills\n- Past hackathon experience\n- Roles and responsibilities"),
                ("Call to Action", "What we want judges to remember.\n**Closing line:** Memorable one-liner."),
            ]
            for title, content in default_slides:
                lines.append("")
                lines.append(f"### {title}")
                lines.append(content)

        return "\n".join(lines)

    def _elevator_pitches(self, pitch: PitchPackage | None) -> str:
        lines = ["## Elevator Pitches"]
        if pitch:
            if pitch.pitch_30:
                lines.append("\n### 30-Second Pitch")
                lines.append(pitch.pitch_30)
            if pitch.pitch_120:
                lines.append("\n### 2-Minute Pitch")
                lines.append(pitch.pitch_120)
            if pitch.pitch_300:
                lines.append("\n### 5-Minute Pitch")
                lines.append(pitch.pitch_300)
        else:
            lines.append("")
            lines.append("*Elevator pitches pending generation.*")
        return "\n".join(lines)

    def _demo_script(self, pitch: PitchPackage | None, presentation: PresentationPackage | None) -> str:
        lines = ["## Demo Script"]

        demo_script = ""
        if pitch and pitch.demo_script:
            demo_script = pitch.demo_script
        elif presentation and presentation.demo_story:
            demo_script = presentation.demo_story

        if demo_script:
            lines.append("")
            lines.append(demo_script)
        else:
            lines.append("")
            lines.append("### Setup")
            lines.append("- Ensure demo environment is ready (local or deployed)")
            lines.append("- Reset any test data to a clean state")
            lines.append("- Have backup plan (screenshots / video)")
            lines.append("")
            lines.append("### Walkthrough")
            lines.append("1. **Landing Page** — Show the UI, explain the value prop (30s)")
            lines.append("2. **Core Action** — Perform the primary user flow (60s)")
            lines.append("3. **Result** — Show the output / insight / transformation (30s)")
            lines.append("4. **Technical Wow** — Call out the most impressive part (30s)")
            lines.append("")
            lines.append("### Pro Tips")
            lines.append("- Speak slowly and clearly")
            lines.append("- Narrate *what* you're doing and *why* it matters")
            lines.append("- If something breaks, acknowledge it and move on")
            lines.append("- End by showing the big-picture impact")

        return "\n".join(lines)

    def _qa_preparation(self, pitch: PitchPackage | None) -> str:
        lines = ["## Q&A Preparation"]
        if pitch and pitch.qa:
            for i, qa in enumerate(pitch.qa, 1):
                lines.append("")
                lines.append(f"### Q{i}: {qa.question}")
                lines.append(qa.answer)
        else:
            lines.append("")
            lines.append("### Common Questions to Prepare For")
            qa_defaults = [
                ("What problem does this solve?",
                 "Frame the problem clearly. Reference real pain points. Show you understand the domain deeply."),
                ("What makes this different from existing solutions?",
                 "Highlight your unique angle. Mention technical novelty. Compare with at most 2 alternatives."),
                ("How far along is the implementation?",
                 "Be honest about scope. Emphasize what works today. Discuss what you'd add with more time."),
                ("What were the biggest technical challenges?",
                 "Show depth of thinking. Mention a specific hard problem and how you solved it."),
                ("How would this scale?",
                 "Show you've thought beyond the hackathon. Mention architecture decisions that support scale."),
            ]
            for q, a in qa_defaults:
                lines.append("")
                lines.append(f"### {q}")
                lines.append(a)

        return "\n".join(lines)

    def _key_talking_points(self, selected: Idea | None, problem: ProblemAnalysis | None, arch: ArchitecturePackage | None, team: TeamProfile | None) -> str:
        lines = ["## Key Talking Points"]

        if selected:
            lines.append("\n### Core Message")
            lines.append(f"**{selected.title}** — {selected.description}")

            scores = []
            if selected.innovation_score:
                scores.append(f"Innovation: {selected.innovation_score:.0f}/100")
            if selected.feasibility_score:
                scores.append(f"Feasibility: {selected.feasibility_score:.0f}/100")
            if selected.hackathon_fit_score:
                scores.append(f"Hackathon Fit: {selected.hackathon_fit_score:.0f}/100")
            if selected.technical_wow_score:
                scores.append(f"Technical Wow: {selected.technical_wow_score:.0f}/100")
            if scores:
                lines.append(f"\n**Scores:** {' | '.join(scores)}")

        lines.append("")
        lines.append("### Problem Validation")
        if problem and problem.problem_definition:
            lines.append(f"- **Problem:** {problem.problem_definition}")
        if problem and problem.stakeholders:
            lines.append(f"- **Stakeholders:** {', '.join(problem.stakeholders[:3])}")

        lines.append("")
        lines.append("### Technical Highlights")
        if arch and arch.architecture.components:
            lines.append(f"- **Components:** {len(arch.architecture.components)} modular services")
            lines.append(f"- **APIs:** {len(arch.api_design)} endpoints defined")
        else:
            lines.append("- Clean, modular architecture")
            lines.append("- Modern tech stack with fast iteration in mind")
            lines.append("- Designed for demo reliability")

        lines.append("")
        lines.append("### Team Capabilities")
        if team:
            lines.append(f"- **Size:** {team.team_size} members")
            lines.append(f"- **Skills:** {', '.join(team.skills[:5]) if team.skills else 'Diverse'}")
            lines.append(f"- **Experience:** {team.experience_level.value} level")
        else:
            lines.append("- Small, focused team with complementary skills")
            lines.append("- Strong execution capability for hackathon timeline")

        return "\n".join(lines)
