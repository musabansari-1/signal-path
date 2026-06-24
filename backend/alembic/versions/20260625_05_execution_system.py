"""Create application tracking and execution system.

Revision ID: 20260625_05
Revises: 20260625_04
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260625_05"
down_revision: str | None = "20260625_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "applications",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("company_name", sa.String(240), nullable=False),
        sa.Column("role_title", sa.String(240), nullable=False),
        sa.Column("status", sa.String(60), nullable=False),
        sa.Column("date_applied", sa.Date()),
        sa.Column("contact_name", sa.String(240)),
        sa.Column("contact_email", sa.String(320)),
        sa.Column("contact_linkedin_url", sa.String(2048)),
        sa.Column("follow_up_date", sa.Date()),
        sa.Column("resume_id", sa.Uuid()),
        sa.Column("notes", sa.Text()),
        sa.Column("interview_stage", sa.String(120)),
        sa.Column("interview_date", sa.DateTime(timezone=True)),
        sa.Column("id", sa.Uuid(), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["resume_id"], ["generated_resumes.id"], ondelete="SET NULL"
        ),
        sa.UniqueConstraint("user_id", "job_id", name="uq_application_user_job"),
    )
    op.create_index("ix_applications_user_id", "applications", ["user_id"])
    op.create_index("ix_applications_project_id", "applications", ["project_id"])
    op.create_index("ix_applications_job_id", "applications", ["job_id"])

    op.create_table(
        "interview_prep_plans",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("application_id", sa.Uuid()),
        sa.Column("interview_stage", sa.String(120), nullable=False),
        sa.Column("interview_date", sa.DateTime(timezone=True)),
        sa.Column("technical_questions", sa.JSON(), nullable=False),
        sa.Column("behavioral_questions", sa.JSON(), nullable=False),
        sa.Column("company_research", sa.JSON(), nullable=False),
        sa.Column("mock_interview_plan", sa.JSON(), nullable=False),
        sa.Column("questions_to_ask", sa.JSON(), nullable=False),
        sa.Column("focus_areas", sa.JSON(), nullable=False),
        sa.Column("practice_answers", sa.JSON(), nullable=False),
        sa.Column("id", sa.Uuid(), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["application_id"], ["applications.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_interview_prep_plans_user_id", "interview_prep_plans", ["user_id"])
    op.create_index(
        "ix_interview_prep_plans_project_id", "interview_prep_plans", ["project_id"]
    )
    op.create_index("ix_interview_prep_plans_job_id", "interview_prep_plans", ["job_id"])
    op.create_index(
        "ix_interview_prep_plans_application_id",
        "interview_prep_plans",
        ["application_id"],
    )

    op.create_table(
        "portfolio_projects",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid()),
        sa.Column("name", sa.String(240), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("github_url", sa.String(2048)),
        sa.Column("live_url", sa.String(2048)),
        sa.Column("tech_stack", sa.JSON(), nullable=False),
        sa.Column("role_alignment", sa.JSON(), nullable=False),
        sa.Column("audit_json", sa.JSON(), nullable=False),
        sa.Column("improvement_tasks", sa.JSON(), nullable=False),
        sa.Column("codex_prompt", sa.Text()),
        sa.Column("id", sa.Uuid(), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_portfolio_projects_user_id", "portfolio_projects", ["user_id"])
    op.create_index(
        "ix_portfolio_projects_project_id", "portfolio_projects", ["project_id"]
    )

    op.create_table(
        "weekly_tasks",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("task_date", sa.Date(), nullable=False),
        sa.Column("day_label", sa.String(20), nullable=False),
        sa.Column("task_type", sa.String(60), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("related_job_id", sa.Uuid()),
        sa.Column("related_application_id", sa.Uuid()),
        sa.Column("id", sa.Uuid(), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["related_job_id"], ["jobs.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["related_application_id"], ["applications.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_weekly_tasks_user_id", "weekly_tasks", ["user_id"])
    op.create_index("ix_weekly_tasks_project_id", "weekly_tasks", ["project_id"])


def downgrade() -> None:
    op.drop_table("weekly_tasks")
    op.drop_table("portfolio_projects")
    op.drop_table("interview_prep_plans")
    op.drop_table("applications")

