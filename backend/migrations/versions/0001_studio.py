"""Create the additive studio schema. Prototype tables are left untouched."""

import sqlalchemy as sa
from alembic import context, op

revision = "0001_studio"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Development bootstraps the same schema. A first migration against that
    # database adopts it; existing tables must have all expected columns.
    inspector = None if context.is_offline_mode() else sa.inspect(op.get_bind())
    expected = {
        "studio_projects": {
            "id",
            "owner",
            "name",
            "intake",
            "revision",
            "state",
            "context",
            "active_job",
            "ai_cost",
            "search_count",
            "created_at",
            "updated_at",
        },
        "studio_jobs": {
            "id",
            "project_id",
            "kind",
            "status",
            "payload",
            "input_revision",
            "events",
            "error",
            "lease_until",
            "attempts",
            "created_at",
            "updated_at",
        },
        "studio_artifacts": {
            "id",
            "project_id",
            "revision",
            "kind",
            "content",
            "created_at",
        },
        "studio_messages": {
            "id",
            "project_id",
            "role",
            "content",
            "context_revision",
            "created_at",
        },
    }
    existing = (
        (set(inspector.get_table_names()) & set(expected)) if inspector else set()
    )
    if existing:
        if existing != set(expected) or any(
            {column["name"] for column in inspector.get_columns(table)}
            != expected[table]
            for table in existing
        ):
            raise RuntimeError(
                "Existing studio schema does not match this migration. Back up the database and inspect the mismatch before upgrading."
            )
        return
    op.create_table(
        "studio_projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner", sa.String(64), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("intake", sa.JSON(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(40), nullable=False),
        sa.Column("context", sa.JSON(), nullable=False),
        sa.Column("active_job", sa.String(36), nullable=True),
        sa.Column("ai_cost", sa.Float(), nullable=False),
        sa.Column("search_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_studio_projects_owner", "studio_projects", ["owner"])
    op.create_table(
        "studio_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(36),
            sa.ForeignKey("studio_projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("input_revision", sa.Integer(), nullable=False),
        sa.Column("events", sa.JSON(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("lease_until", sa.DateTime(), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_studio_jobs_project_id", "studio_jobs", ["project_id"])
    op.create_index("ix_studio_jobs_status", "studio_jobs", ["status"])
    op.create_table(
        "studio_artifacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(36),
            sa.ForeignKey("studio_projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(40), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_studio_artifacts_project_id", "studio_artifacts", ["project_id"]
    )
    op.create_table(
        "studio_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "project_id",
            sa.String(36),
            sa.ForeignKey("studio_projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("context_revision", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_studio_messages_project_id", "studio_messages", ["project_id"])


def downgrade():
    for table in (
        "studio_messages",
        "studio_artifacts",
        "studio_jobs",
        "studio_projects",
    ):
        op.drop_table(table)
