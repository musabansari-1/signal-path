"""Create candidate profiles, career assets, and role criteria.

Revision ID: 20260624_02
Revises: 20260624_01
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260624_02"
down_revision: str | None = "20260624_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _identity_columns() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def _owner_columns() -> list[sa.Column]:
    return [
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
    ]


def _owner_constraints() -> list[sa.ForeignKeyConstraint]:
    return [
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["project_id"], ["job_search_projects.id"], ondelete="CASCADE"
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "candidate_profiles",
        *_owner_columns(),
        sa.Column("headline", sa.String(240)),
        sa.Column("summary", sa.Text()),
        sa.Column("years_experience", sa.Float()),
        sa.Column("location", sa.String(160)),
        sa.Column("work_authorization", sa.String(240)),
        sa.Column("skills_json", sa.JSON(), nullable=False),
        sa.Column("experience_json", sa.JSON(), nullable=False),
        sa.Column("projects_json", sa.JSON(), nullable=False),
        sa.Column("education_json", sa.JSON(), nullable=False),
        sa.Column("certifications_json", sa.JSON(), nullable=False),
        sa.Column("achievements_json", sa.JSON(), nullable=False),
        sa.Column("strengths_json", sa.JSON(), nullable=False),
        sa.Column("gaps_json", sa.JSON(), nullable=False),
        sa.Column("best_fit_roles_json", sa.JSON(), nullable=False),
        sa.Column("verified_facts_json", sa.JSON(), nullable=False),
        sa.Column("suggestions_json", sa.JSON(), nullable=False),
        sa.Column("reviewed_at", sa.String(40)),
        *_identity_columns(),
        *_owner_constraints(),
        sa.UniqueConstraint("user_id", "project_id", name="uq_profile_user_project"),
    )
    op.create_index("ix_candidate_profiles_user_id", "candidate_profiles", ["user_id"])
    op.create_index("ix_candidate_profiles_project_id", "candidate_profiles", ["project_id"])

    op.create_table(
        "career_assets",
        *_owner_columns(),
        sa.Column("asset_type", sa.String(40), nullable=False),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("url", sa.String(2048)),
        sa.Column("file_path", sa.String(1024)),
        sa.Column("file_name", sa.String(255)),
        sa.Column("mime_type", sa.String(120)),
        sa.Column("extracted_text", sa.Text()),
        sa.Column("parsed_json", sa.JSON(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        *_identity_columns(),
        *_owner_constraints(),
    )
    op.create_index("ix_career_assets_user_id", "career_assets", ["user_id"])
    op.create_index("ix_career_assets_project_id", "career_assets", ["project_id"])

    op.create_table(
        "role_criteria",
        *_owner_columns(),
        sa.Column("job_titles", sa.JSON(), nullable=False),
        sa.Column("industries", sa.JSON(), nullable=False),
        sa.Column("salary_min", sa.Integer()),
        sa.Column("salary_max", sa.Integer()),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("locations", sa.JSON(), nullable=False),
        sa.Column("work_modes", sa.JSON(), nullable=False),
        sa.Column("experience_levels", sa.JSON(), nullable=False),
        sa.Column("required_skills", sa.JSON(), nullable=False),
        sa.Column("nice_to_have_skills", sa.JSON(), nullable=False),
        sa.Column("company_sizes", sa.JSON(), nullable=False),
        sa.Column("roles_to_avoid", sa.JSON(), nullable=False),
        sa.Column("industries_to_avoid", sa.JSON(), nullable=False),
        sa.Column("visa_preference", sa.String(160)),
        sa.Column("company_stage_preference", sa.String(160)),
        sa.Column("notes", sa.Text()),
        *_identity_columns(),
        *_owner_constraints(),
        sa.UniqueConstraint("user_id", "project_id", name="uq_criteria_user_project"),
    )
    op.create_index("ix_role_criteria_user_id", "role_criteria", ["user_id"])
    op.create_index("ix_role_criteria_project_id", "role_criteria", ["project_id"])


def downgrade() -> None:
    op.drop_table("role_criteria")
    op.drop_table("career_assets")
    op.drop_table("candidate_profiles")

