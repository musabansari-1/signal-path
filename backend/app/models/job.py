import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class JobStatus(StrEnum):
    SAVED = "saved"
    SHORTLISTED = "shortlisted"
    SKIPPED = "skipped"
    APPLIED = "applied"


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source_type: Mapped[str] = mapped_column(String(40), default="manual", nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    company_name: Mapped[str] = mapped_column(String(240), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(240))
    work_mode: Mapped[str | None] = mapped_column(String(40))
    employment_type: Mapped[str | None] = mapped_column(String(80))
    experience_level: Mapped[str | None] = mapped_column(String(80))
    minimum_years_experience: Mapped[float | None] = mapped_column(Float)
    salary_min: Mapped[int | None]
    salary_max: Mapped[int | None]
    currency: Mapped[str | None] = mapped_column(String(8))
    required_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    nice_to_have_skills: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    responsibilities: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    qualifications: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    benefits: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    red_flags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    missing_information: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    application_url: Mapped[str | None] = mapped_column(String(2048))
    parsed_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[JobStatus] = mapped_column(String(40), default=JobStatus.SAVED, nullable=False)
    latest_score: Mapped[int | None] = mapped_column(Integer)


class JobScore(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_scores"

    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    experience_match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    criteria_match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    keyword_match_score: Mapped[int] = mapped_column(Integer, nullable=False)
    location_fit_score: Mapped[int] = mapped_column(Integer, nullable=False)
    growth_potential_score: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty_score: Mapped[int] = mapped_column(Integer, nullable=False)
    recommendation: Mapped[str] = mapped_column(String(40), nullable=False)
    strengths: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    gaps: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    keywords_to_add: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    application_strategy: Mapped[str] = mapped_column(Text, nullable=False)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

