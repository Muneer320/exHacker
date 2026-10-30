"""Verify migrations preserve prototype data and match the application schema."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine

from app.studio.models import StudioBase


def test_initial_migration_preserves_existing_data_and_matches_models(tmp_path):
    path = tmp_path / "migration.db"
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE prototype_records (id TEXT PRIMARY KEY, content TEXT)"
        )
        connection.execute(
            "INSERT INTO prototype_records VALUES ('existing', 'keep this data')"
        )
    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite+aiosqlite:///{path.as_posix()}",
        "EXHACKER_DEBUG": "false",
    }
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=Path(__file__).parents[1],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    with sqlite3.connect(path) as connection:
        assert (
            connection.execute("SELECT content FROM prototype_records").fetchone()[0]
            == "keep this data"
        )
        assert (
            connection.execute("SELECT version_num FROM alembic_version").fetchone()[0]
            == "0002_job_inference"
        )
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    with engine.connect() as connection:
        context = MigrationContext.configure(
            connection,
            opts={
                "include_object": lambda _obj, name, _kind, _reflected, _compare_to: (
                    name != "prototype_records"
                )
            },
        )
        assert compare_metadata(context, StudioBase.metadata) == []
    engine.dispose()
