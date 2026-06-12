import pytest
import pytest_asyncio
from app.db.session import engine
from app.models.base import Base
from app.models.project import ProjectModel
from app.models.workflow import WorkflowStateModel
from app.models.agent_run import AgentRunModel


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_test_db():
    """Autouse fixture to ensure SQLite test database is fully migrated before running tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
