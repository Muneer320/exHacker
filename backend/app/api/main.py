from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.projects import router as projects_router
from app.api.v1.workflows import router as workflows_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize database tables on app startup
    from app.db.session import engine
    from app.models.base import Base
    from app.models.project import ProjectModel
    from app.models.workflow import WorkflowStateModel
    from app.models.agent_run import AgentRunModel
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Middleware configurations (essential for Next.js frontend calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
async def health_check():
    """Health check endpoint to verify backend operational status."""
    return {
        "success": True,
        "data": {
            "status": "healthy"
        },
        "message": "Operation successful"
    }

# Register Router Modules
app.include_router(projects_router, prefix=f"{settings.API_V1_STR}/projects", tags=["projects"])
app.include_router(workflows_router, prefix=f"{settings.API_V1_STR}/workflows", tags=["workflows"])
