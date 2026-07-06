"""Test configuration and fixtures."""

import pytest_asyncio

from app.db.session import engine
from app.models.base import Base


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """Ensure clean tables before running tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
