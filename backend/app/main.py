from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.challenge_intelligence import ChallengeIntelligenceAgent
from app.agents.idea_generator import IdeaGeneratorAgent
from app.agents.idea_validator import IdeaValidatorAgent
from app.agents.opportunity_planner import OpportunityPlannerAgent
from app.agents.problem_analyst import ProblemAnalystAgent
from app.agents.registry import AgentRegistry
from app.agents.user_profiler import UserProfilerAgent
from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging

logger = structlog.get_logger()


def register_agents() -> None:
    AgentRegistry.register(UserProfilerAgent())
    AgentRegistry.register(ChallengeIntelligenceAgent())
    AgentRegistry.register(ProblemAnalystAgent())
    AgentRegistry.register(OpportunityPlannerAgent())
    AgentRegistry.register(IdeaGeneratorAgent())
    AgentRegistry.register(IdeaValidatorAgent())
    logger.info("agents_registered", count=len(AgentRegistry.get_all()))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    logger.info(
        "application_starting",
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
    register_agents()
    yield
    logger.info("application_shutting_down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-agent hackathon operating system",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.include_router(api_router, prefix=settings.api_prefix)
