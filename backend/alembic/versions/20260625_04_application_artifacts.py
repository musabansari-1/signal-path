"""Create grounded resumes and messages.

Revision ID: 20260625_04
Revises: 20260624_03
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260625_04"
down_revision: str | None = "20260624_03"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "generated_resumes",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid()),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("content_json", sa.JSON(), nullable=False),
        sa.Column("markdown_content", sa.Text(), nullable=False),
        sa.Column("export_pdf_path", sa.String(1024)),
        sa.Column("export_docx_path", sa.String(1024)),
        sa.Column("truthfulness_check_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_generated_resumes_user_id", "generated_resumes", ["user_id"])
    op.create_index(
        "ix_generated_resumes_project_id", "generated_resumes", ["project_id"]
    )
    op.create_index("ix_generated_resumes_job_id", "generated_resumes", ["job_id"])

    op.create_table(
        "generated_messages",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid()),
        sa.Column("application_id", sa.Uuid()),
        sa.Column("message_type", sa.String(60), nullable=False),
        sa.Column("tone", sa.String(40), nullable=False),
        sa.Column("subject_line", sa.String(300)),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("claims_used_json", sa.JSON(), nullable=False),
        sa.Column("review_warnings_json", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_generated_messages_user_id", "generated_messages", ["user_id"])
    op.create_index(
        "ix_generated_messages_project_id", "generated_messages", ["project_id"]
    )
    op.create_index("ix_generated_messages_job_id", "generated_messages", ["job_id"])


def downgrade() -> None:
    op.drop_table("generated_messages")
    op.drop_table("generated_resumes")

