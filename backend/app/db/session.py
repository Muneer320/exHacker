"""Database lifecycle and isolated request/worker sessions."""

from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.database_url_async, pool_pre_ping=True)

if settings.DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine.sync_engine, "connect")
    def configure_sqlite(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=10000")
        cursor.close()


AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def initialize_database():
    if settings.is_production:
        return
    import asyncio
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    def migrate():
        config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
        config.set_main_option(
            "script_location", str(Path(__file__).resolve().parents[2] / "migrations")
        )
        command.upgrade(config, "head")

    await asyncio.to_thread(migrate)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
