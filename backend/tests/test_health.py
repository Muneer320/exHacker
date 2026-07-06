import httpx
import pytest
from app.main import app
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check():
    """Verify that health check endpoints return successful operation signals."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_api_v1_health_check():
    """Verify that versioned API health check returns identical signals."""
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "healthy"
