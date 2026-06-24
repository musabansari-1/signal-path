import uuid
from typing import Any

from sqlalchemy import JSON, Boolean, Float, ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class CandidateProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "candidate_profiles"
    __table_args__ = (UniqueConstraint("user_id", "project_id", name="uq_profile_user_project"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    headline: Mapped[str | None] = mapped_column(String(240))
    summary: Mapped[str | None] = mapped_column(Text)
    years_experience: Mapped[float | None] = mapped_column(Float)
    location: Mapped[str | None] = mapped_column(String(160))
    work_authorization: Mapped[str | None] = mapped_column(String(240))
    skills_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    experience_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    projects_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    education_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    certifications_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    achievements_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    strengths_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    gaps_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    best_fit_roles_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    verified_facts_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    suggestions_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    reviewed_at: Mapped[str | None] = mapped_column(String(40))


class CareerAsset(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "career_assets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    asset_type: Mapped[str] = mapped_column(String(40), default="resume", nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    url: Mapped[str | None] = mapped_column(String(2048))
    file_path: Mapped[str | None] = mapped_column(String(1024))
    file_name: Mapped[str | None] = mapped_column(String(255))
    mime_type: Mapped[str | None] = mapped_column(String(120))
    extracted_text: Mapped[str | None] = mapped_column(Text)
    parsed_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class RoleCriteria(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "role_criteria"
    __table_args__ = (UniqueConstraint("user_id", "project_id", name="uq_criteria_user_project"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_titles: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    industries: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    salary_min: Mapped[int | None]
    salary_max: Mapped[int | None]
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    locations: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    work_modes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    experience_levels: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    required_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    nice_to_have_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    company_sizes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    roles_to_avoid: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    industries_to_avoid: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    visa_preference: Mapped[str | None] = mapped_column(String(160))
    company_stage_preference: Mapped[str | None] = mapped_column(String(160))
    notes: Mapped[str | None] = mapped_column(Text)
