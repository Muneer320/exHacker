from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
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
