"""FastAPI application entry point."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import exhacker_error_handler, generic_error_handler, ExHackerError

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=None,
)

setup_logging()
logger.info("Starting exHacker in %s environment", settings.ENV)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
app.add_exception_handler(ExHackerError, exhacker_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, generic_error_handler)  # type: ignore[arg-type]


@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
async def health_check():
    """Health check endpoint."""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "version": "0.1.0",
            "environment": settings.ENV,
        },
        "message": "Operation successful",
    }


# API routers
from app.api.v1 import projects, research, directions, blueprint, export, challenge, competitor, shared, ideas, architecture, documentation

app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(research.router, prefix=settings.API_V1_STR)
app.include_router(directions.router, prefix=settings.API_V1_STR)
app.include_router(blueprint.router, prefix=settings.API_V1_STR)
app.include_router(export.router, prefix=settings.API_V1_STR)
app.include_router(challenge.router, prefix=settings.API_V1_STR)
app.include_router(competitor.router, prefix=settings.API_V1_STR)
app.include_router(shared.router, prefix=settings.API_V1_STR)
app.include_router(ideas.router, prefix=settings.API_V1_STR)
app.include_router(architecture.router, prefix=settings.API_V1_STR)
app.include_router(documentation.router, prefix=settings.API_V1_STR)
