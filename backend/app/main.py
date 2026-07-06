"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import exhacker_error_handler, generic_error_handler, ExHackerError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle."""
    setup_logging()
    # Auto-create database tables on startup
    from app.db.session import engine
    from app.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

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


# API routers will be registered here as they are built
# from app.api.v1 import projects, research, blueprint, export
