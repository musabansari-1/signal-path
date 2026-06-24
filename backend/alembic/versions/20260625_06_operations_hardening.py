"""Create operations tables for jobs and AI logs.

Revision ID: 20260625_06
Revises: 20260625_05
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260625_06"
down_revision: str | None = "20260625_05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "background_jobs",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid()),
        sa.Column("job_type", sa.String(80), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("result_json", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column("id", sa.Uuid(), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_background_jobs_user_id", "background_jobs", ["user_id"])
    op.create_index("ix_background_jobs_project_id", "background_jobs", ["project_id"])

    op.create_table(
        "ai_generation_logs",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid()),
        sa.Column("feature_name", sa.String(120), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
        sa.Column("model", sa.String(160)),
        sa.Column("tokens_input", sa.Integer()),
        sa.Column("tokens_output", sa.Integer()),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column("id", sa.Uuid(), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_ai_generation_logs_user_id", "ai_generation_logs", ["user_id"])
    op.create_index(
        "ix_ai_generation_logs_project_id", "ai_generation_logs", ["project_id"]
    )


def downgrade() -> None:
    op.drop_table("ai_generation_logs")
    op.drop_table("background_jobs")

