"""exHacker API and durable workflow worker lifecycle."""

import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestBodyLimit
from app.db.session import engine, initialize_database
from app.studio.ai import StudioError, configuration
from app.studio.credential_routes import router as credential_router
from app.studio.credentials import cleanup_loop, leases
from app.studio.jobs import worker
from app.studio.models import Job, Project
from app.studio.routes import router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app):
    if settings.is_production and settings.STUDIO_DEMO_MODE:
        raise RuntimeError("Demonstration mode cannot run with ENV=production.")
    if settings.is_production and (
        (settings.AI_ACCESS_MODE == "operator" and not configuration()["ai_configured"])
        or not configuration()["research_configured"]
    ):
        raise RuntimeError(
            "Production requires Tavily and, in operator mode, configured AI credentials."
        )
    leases.ttl = settings.AI_LEASE_SECONDS
    cleanup = asyncio.create_task(cleanup_loop())
    await initialize_database()
    task = asyncio.create_task(worker()) if settings.STUDIO_WORKER_ENABLED else None
    try:
        yield
    finally:
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        leases.clear()
        cleanup.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await cleanup
        await engine.dispose()


app = FastAPI(
    title="exHacker",
    version="0.2.0",
    lifespan=lifespan,
    openapi_url="/api/v1/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-AI-Lease"],
    expose_headers=["Content-Disposition", "ETag"],
)
app.add_middleware(RequestBodyLimit)


@app.exception_handler(StudioError)
async def studio_error(_request, exc):
    return JSONResponse(
        status_code=exc.status,
        content={"success": False, "error": {"message": str(exc)}},
    )


@app.exception_handler(RequestValidationError)
async def validation_error(_request, exc):
    if _request.url.path.startswith("/api/v1/ai/leases"):
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {"message": "Check the provider, model, and API key fields."},
            },
        )
    errors = [
        {
            "field": ".".join(str(v) for v in error["loc"] if v != "body"),
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "message": "Please check the highlighted input values.",
                "fields": errors,
            },
        },
    )


@app.exception_handler(Exception)
async def unexpected_error(_request, _exc):
    logger.error("Unexpected API error (%s)", type(_exc).__name__)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "message": "An unexpected server error occurred. Saved project data was preserved."
            },
        },
    )


@app.middleware("http")
async def private_responses(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/health")
@app.get("/api/v1/health")
async def health():
    return {
        "success": True,
        "data": {"status": "healthy", "version": "0.2.0", "environment": settings.ENV},
    }


@app.get("/ready")
async def readiness():
    async with engine.connect() as connection:
        await connection.execute(select(Project.id).limit(1))
        await connection.execute(select(Job.inference).limit(1))
    return {
        "success": True,
        "data": {"database": "ready", "worker_enabled": settings.STUDIO_WORKER_ENABLED},
    }


app.include_router(router, prefix="/api/v1")

app.include_router(credential_router, prefix="/api/v1")
