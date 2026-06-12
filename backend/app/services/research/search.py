import logging
from typing import List, Dict, Any
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class TavilySearchClient:
    """
    Search Client for Tavily API.
    Provides real web search queries or realistic mock results if MOCK_RESEARCH is enabled.
    """

    def __init__(self):
        self.api_url = "https://api.tavily.com/search"
        self.api_key = settings.SEARCH_API_KEY

    async def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Executes a search query.
        Returns a list of dicts: {"title": str, "url": str, "content": str}
        """
        # Use mock search if configured or if API key is missing
        if settings.MOCK_RESEARCH or not self.api_key:
            logger.info(f"[TavilySearchClient] Running MOCK search for query: '{query}'")
            return self._generate_mock_results(query, max_results)

        logger.info(f"[TavilySearchClient] Executing LIVE search for query: '{query}'")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                payload = {
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": False,
                }
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])

                # Map Tavily fields to our standard format
                standard_results = []
                for r in results:
                    standard_results.append({
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content") or r.get("snippet") or "",
                    })
                return standard_results
        except Exception as e:
            logger.error(f"[TavilySearchClient] Live search failed: {e}. Falling back to mock.")
            return self._generate_mock_results(query, max_results)

    def _generate_mock_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Generates realistic mock search results based on query keywords."""
        query_lower = query.lower()

        # Competitor/SaaS mock search results
        if "competitor" in query_lower or "startup" in query_lower or "alternative" in query_lower:
            return [
                {
                    "title": "V0 by Vercel - Generative UI and Frontend Scaffolder",
                    "url": "https://v0.dev",
                    "content": "v0 is a generative UI system by Vercel that creates production-ready React and Tailwind CSS components based on text prompts. Useful for rapid prototyping.",
                },
                {
                    "title": "Bolt.new - Fullstack Web Development in the Browser",
                    "url": "https://bolt.new",
                    "content": "Bolt.new is an AI-powered fullstack development environment running entirely in the browser. It allows users to prompt, run, edit, and deploy fullstack web apps.",
                },
                {
                    "title": "Lovable.dev - Fullstack GPT Engineer",
                    "url": "https://lovable.dev",
                    "content": "Lovable is an AI co-pilot for web development that writes code, manages state, and deploys SaaS MVPs directly from design specifications and description requirements.",
                },
            ][:max_results]

        # GitHub/Open Source mock search results
        if "github" in query_lower or "open source" in query_lower or "library" in query_lower:
            return [
                {
                    "title": "GitHub - langchain-ai/langgraph: Orchestrate agentic workflows",
                    "url": "https://github.com/langchain-ai/langgraph",
                    "content": "LangGraph is a library for building stateful, multi-actor applications with LLMs, used to create agentic graphs, loops, and human-in-the-loop checkpoints. Stars: 3,400.",
                },
                {
                    "title": "GitHub - tiangolo/fastapi: FastAPI framework, high performance",
                    "url": "https://github.com/fastapi/fastapi",
                    "content": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints. Stars: 68,000.",
                },
                {
                    "title": "GitHub - crewAIInc/crewAI: Framework for orchestrating role-playing autonomous agents",
                    "url": "https://github.com/crewAIInc/crewAI",
                    "content": "CrewAI is a framework for orchestrating role-playing autonomous AI agents. By fostering collaborative intelligence, it empowers agents to work together. Stars: 12,500.",
                },
            ][:max_results]

        # APIs / SDKs mock search results
        if "api" in query_lower or "sdk" in query_lower or "sponsor" in query_lower:
            return [
                {
                    "title": "Groq Cloud Developer Portal - Ultra low-latency LLM Inference",
                    "url": "https://console.groq.com",
                    "content": "Groq LPU Inference Engine delivers sub-100ms response times for Llama 3 models. Free and paid developer tiers are available via a standard OpenAI-compatible API.",
                },
                {
                    "title": "Google Gemini Developer Suite - Multimodal AI API",
                    "url": "https://ai.google.dev",
                    "content": "Google Gemini offers a developer API for Gemini 1.5 Flash and Pro models, providing robust, high-context window processing and cost-effective fallback capabilities.",
                },
                {
                    "title": "Tavily Search API - Built for AI Agents and RAG Pipelines",
                    "url": "https://tavily.com",
                    "content": "Tavily Search API is search optimized for LLMs and RAG. It returns structured, clean text snippets without HTML clutter, ideal for grounding agent execution.",
                },
            ][:max_results]

        # Default fallback
        return [
            {
                "title": f"Search results for: {query}",
                "url": "https://example.com/search",
                "content": f"Structured search results snippet discussing relevance, market trends, and technical stack details relating to the query: '{query}' in a hackathon development context.",
            }
        ][:max_results]


# Singleton instance
search_client = TavilySearchClient()
