"""Persist routing metadata and opaque references, never credentials."""

import sqlalchemy as sa
from alembic import op

revision = "0002_job_inference"
down_revision = "0001_studio"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("studio_jobs", sa.Column("inference", sa.JSON(), nullable=True))


def downgrade():
    op.drop_column("studio_jobs", "inference")
