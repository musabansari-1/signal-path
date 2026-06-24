"""Create jobs and deterministic scores.

Revision ID: 20260624_03
Revises: 20260624_02
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260624_03"
down_revision: str | None = "20260624_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(40), nullable=False),
        sa.Column("source_url", sa.String(2048)),
        sa.Column("company_name", sa.String(240), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(240)),
        sa.Column("work_mode", sa.String(40)),
        sa.Column("employment_type", sa.String(80)),
        sa.Column("experience_level", sa.String(80)),
        sa.Column("minimum_years_experience", sa.Float()),
        sa.Column("salary_min", sa.Integer()),
        sa.Column("salary_max", sa.Integer()),
        sa.Column("currency", sa.String(8)),
        sa.Column("required_skills", sa.JSON(), nullable=False),
        sa.Column("nice_to_have_skills", sa.JSON(), nullable=False),
        sa.Column("responsibilities", sa.JSON(), nullable=False),
        sa.Column("qualifications", sa.JSON(), nullable=False),
        sa.Column("benefits", sa.JSON(), nullable=False),
        sa.Column("red_flags", sa.JSON(), nullable=False),
        sa.Column("missing_information", sa.JSON(), nullable=False),
        sa.Column("application_url", sa.String(2048)),
        sa.Column("parsed_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("latest_score", sa.Integer()),
        sa.Column("id", sa.Uuid(), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])
    op.create_index("ix_jobs_project_id", "jobs", ["project_id"])

    op.create_table(
        "job_scores",
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("skill_match_score", sa.Integer(), nullable=False),
        sa.Column("experience_match_score", sa.Integer(), nullable=False),
        sa.Column("criteria_match_score", sa.Integer(), nullable=False),
        sa.Column("keyword_match_score", sa.Integer(), nullable=False),
        sa.Column("location_fit_score", sa.Integer(), nullable=False),
        sa.Column("growth_potential_score", sa.Integer(), nullable=False),
        sa.Column("difficulty_score", sa.Integer(), nullable=False),
        sa.Column("recommendation", sa.String(40), nullable=False),
        sa.Column("strengths", sa.JSON(), nullable=False),
        sa.Column("gaps", sa.JSON(), nullable=False),
        sa.Column("keywords_to_add", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("application_strategy", sa.Text(), nullable=False),
        sa.Column("scored_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_job_scores_job_id", "job_scores", ["job_id"], unique=True)
    op.create_index("ix_job_scores_user_id", "job_scores", ["user_id"])
    op.create_index("ix_job_scores_project_id", "job_scores", ["project_id"])


def downgrade() -> None:
    op.drop_table("job_scores")
    op.drop_table("jobs")

