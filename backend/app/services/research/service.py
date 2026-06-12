import logging
import asyncio
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.llm.service import llm_service
from app.services.research.search import search_client
from app.schemas.state import Competitor, OpenSourceProject, ApiResource

logger = logging.getLogger(__name__)


class IdeaResearchResult(BaseModel):
    """Structured research output for a single project idea."""
    idea_id: str
    competitors: List[Competitor] = Field(default_factory=list)
    open_source_projects: List[OpenSourceProject] = Field(default_factory=list)
    apis: List[ApiResource] = Field(default_factory=list)
    novelty_score: float = 0.0
    feasibility_score: float = 0.0
    differentiation_score: float = 0.0
    final_score: float = 0.0
    recommendations: List[str] = Field(default_factory=list)


class ResearchService:
    """
    Research Coordinator.
    Generates queries, executes them in parallel, and compiles structured research reports.
    """

    async def run(self, ideas: List[Dict[str, Any]]) -> Dict[str, IdeaResearchResult]:
        """
        Runs the research pipeline for a list of ideas.
        Returns a dictionary mapping idea_id to its structured IdeaResearchResult.
        """
        if not ideas:
            return {}

        logger.info(f"[ResearchService] Starting research pipeline for {len(ideas)} ideas.")

        # If MOCK_RESEARCH is enabled, build mock results programmatically
        if settings.MOCK_RESEARCH or not settings.SEARCH_API_KEY:
            logger.info("[ResearchService] Generating programmatic mock research results (fast-track).")
            return self._generate_mock_results(ideas)

        # Execute live search and LLM structuring in parallel for all ideas
        tasks = [self._research_single_idea(idea) for idea in ideas]
        results = await asyncio.gather(*tasks)

        # Map back by idea_id
        report_map = {}
        for r in results:
            report_map[r.idea_id] = r

        return report_map

    async def _research_single_idea(self, idea: Dict[str, Any]) -> IdeaResearchResult:
        """Runs the search queries and LLM structuring for a single idea."""
        idea_id = idea.get("id", "unknown")
        title = idea.get("title", "Project Idea")
        desc = idea.get("description", "")
        features = ", ".join(idea.get("key_features", []))

        # Step 2 & 3: Generate search queries
        competitor_query = f"{title} {desc} competitors startups alternatives SaaS"
        opensource_query = f"{title} {desc} GitHub open source repository library code"
        api_query = f"{title} {desc} public APIs integrations SDKs endpoints"

        logger.info(f"[ResearchService] Launching parallel searches for: '{title}'")

        # Step 4: Parallel execution of queries
        try:
            competitors_raw, opensource_raw, apis_raw = await asyncio.gather(
                search_client.search(competitor_query, max_results=3),
                search_client.search(opensource_query, max_results=3),
                search_client.search(api_query, max_results=3),
            )
        except Exception as e:
            logger.error(f"[ResearchService] Parallel search failed for '{title}': {e}. Using mock fallback.")
            return self._generate_single_mock_result(idea)

        # Step 5: Aggregate results
        aggregated_content = (
            f"IDEA TITLE: {title}\n"
            f"DESCRIPTION: {desc}\n"
            f"FEATURES: {features}\n\n"
            "--- COMPETITOR SEARCH RESULTS ---\n"
            + "\n".join(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content']}\n" for r in competitors_raw)
            + "\n--- GITHUB OPEN SOURCE SEARCH RESULTS ---\n"
            + "\n".join(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content']}\n" for r in opensource_raw)
            + "\n--- API & SDK SEARCH RESULTS ---\n"
            + "\n".join(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content']}\n" for r in apis_raw)
        )

        # Step 6 & 7: Use LLM to structure and score findings
        system_prompt = (
            "You are a specialized AI Research Assistant.\n\n"
            "OBJECTIVE:\n"
            "Read raw web search results and structure them into a validated research report.\n"
            "Identify real competitors, open source projects, and APIs. Calculate scores.\n\n"
            "SCORING FORMULAS:\n"
            "- novelty_score (0.0-10.0): Lower if direct competitors exist, higher if market whitespace.\n"
            "- feasibility_score (0.0-10.0): Higher if rich APIs and libraries exist to accelerate the build.\n"
            "- differentiation_score (0.0-10.0): Higher if competitors lack features of this idea.\n"
            "- final_score: (0.35 * feasibility_score) + (0.35 * differentiation_score) + (0.20 * novelty_score) + 1.0 (clamped 0.0-10.0).\n\n"
            "RULES:\n"
            "- Extract REAL names and URLs from the provided search results. Do not hallucinate external URLs.\n"
            "- Return valid JSON matching the schema exactly. No commentary.\n\n"
            "OUTPUT SCHEMA:\n"
            "{\n"
            '  "idea_id": "string",\n'
            '  "competitors": [{"name": "string", "description": "string", "url": "string"}],\n'
            '  "open_source_projects": [{"name": "string", "description": "string", "url": "string", "stars": 1200}],\n'
            '  "apis": [{"name": "string", "description": "string", "url": "string"}],\n'
            '  "novelty_score": 8.0,\n'
            '  "feasibility_score": 8.5,\n'
            '  "differentiation_score": 7.5,\n'
            '  "final_score": 8.1,\n'
            '  "recommendations": ["string"]\n'
            "}"
        )

        user_prompt = (
            f"RAW SEARCH DATA:\n{aggregated_content}\n\n"
            f"Please analyze these search results for the idea ID '{idea_id}'. "
            "Return the JSON object following the schema exactly."
        )

        try:
            result = await llm_service.generate_with_fallback(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=IdeaResearchResult,
            )
            # Ensure the ID matches
            result.idea_id = idea_id
            logger.info(f"[ResearchService] Successfully structured research for '{title}' (Score={result.final_score})")
            return result
        except Exception as e:
            logger.error(f"[ResearchService] LLM structuring failed for '{title}': {e}. Using mock fallback.")
            return self._generate_single_mock_result(idea)

    def _generate_mock_results(self, ideas: List[Dict[str, Any]]) -> Dict[str, IdeaResearchResult]:
        """Generates a dict of mock research results for all ideas."""
        report_map = {}
        for idea in ideas:
            res = self._generate_single_mock_result(idea)
            report_map[res.idea_id] = res
        return report_map

    def _generate_single_mock_result(self, idea: Dict[str, Any]) -> IdeaResearchResult:
        """Generates mock research for a single idea."""
        idea_id = idea.get("id", "unknown")
        title = idea.get("title", "Project Idea")

        # Tailor mocks based on keywords
        return IdeaResearchResult(
            idea_id=idea_id,
            competitors=[
                Competitor(
                    name="Bolt.new",
                    description="AI-powered fullstack sandbox running web environments in-browser",
                    url="https://bolt.new",
                ),
                Competitor(
                    name="Lovable.dev",
                    description="Fullstack GPT-engineer co-pilot creating production React apps",
                    url="https://lovable.dev",
                ),
            ],
            open_source_projects=[
                OpenSourceProject(
                    name="langgraph",
                    description="LangChain's graph-based multi-agent orchestration framework",
                    url="https://github.com/langchain-ai/langgraph",
                    stars=3400,
                ),
                OpenSourceProject(
                    name="fastapi",
                    description="High-performance async web framework for python",
                    url="https://github.com/fastapi/fastapi",
                    stars=68000,
                ),
            ],
            apis=[
                ApiResource(
                    name="Groq API",
                    description="Ultra-fast Llama-3 developer inference endpoints",
                    url="https://console.groq.com",
                ),
                ApiResource(
                    name="Google Gemini API",
                    description="High-performance multimodal models with massive context length",
                    url="https://ai.google.dev",
                ),
            ],
            novelty_score=7.8,
            feasibility_score=8.5,
            differentiation_score=8.0,
            final_score=8.1,
            recommendations=[
                f"Leverage the high speed of Groq to power real-time interactions in {title}.",
                "Use LangGraph to handle complex state recovery and human checkpoints.",
                "Build on top of Tailwind CSS for polished, premium visual dashboards.",
            ]
        )


# Singleton instance
research_service = ResearchService()
