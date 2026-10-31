"""Verify migrations preserve prototype data and match the application schema."""

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine

from app.studio.models import StudioBase


@pytest.mark.parametrize("unversioned", [False, True])
def test_existing_studio_rows_survive_byok_upgrade(tmp_path, unversioned):
    path = tmp_path / "legacy-studio.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{path.as_posix()}"}

    def migrate(target):
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", target],
            cwd=Path(__file__).parents[1],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stderr

    migrate("0001_studio")
    with sqlite3.connect(path) as connection:
        connection.execute(
            "INSERT INTO studio_projects VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "legacy-project",
                "a" * 64,
                "Keep this plan",
                "{}",
                7,
                "ready",
                '{"documents":{"files":[]}}',
                "legacy-job",
                0.01,
                2,
                "2026-10-31 00:00:00",
                "2026-10-31 00:00:00",
            ),
        )
        connection.execute(
            "INSERT INTO studio_jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                "legacy-job",
                "legacy-project",
                "chat",
                "queued",
                '{"message":"Saved question"}',
                7,
                "[]",
                None,
                None,
                0,
                "2026-10-31 00:00:00",
                "2026-10-31 00:00:00",
            ),
        )
        connection.execute(
            "INSERT INTO studio_artifacts VALUES (?, ?, ?, ?, ?, ?)",
            (
                "legacy-artifact",
                "legacy-project",
                7,
                "documents",
                '{"saved":"original"}',
                "2026-10-31 00:00:00",
            ),
        )
        connection.execute(
            "INSERT INTO studio_messages VALUES (?, ?, ?, ?, ?, ?)",
            (
                "legacy-message",
                "legacy-project",
                "assistant",
                "Saved answer",
                6,
                "2026-10-31 00:00:00",
            ),
        )
        snapshots = {
            table: connection.execute(f"SELECT * FROM {table}").fetchall()
            for table in (
                "studio_projects",
                "studio_jobs",
                "studio_artifacts",
                "studio_messages",
            )
        }
        if unversioned:
            # The previous development startup used create_all without Alembic.
            connection.execute("DROP TABLE alembic_version")
    migrate("head")
    with sqlite3.connect(path) as connection:
        for table, before in snapshots.items():
            rows = connection.execute(f"SELECT * FROM {table}").fetchall()
            assert [row[: len(before[0])] for row in rows] == before
        assert connection.execute("SELECT inference FROM studio_jobs").fetchone() == (
            None,
        )
        assert connection.execute(
            "SELECT version_num FROM alembic_version"
        ).fetchone() == ("0002_job_inference",)


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
