import pytest
import httpx
from httpx import AsyncClient
from app.api.main import app


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
