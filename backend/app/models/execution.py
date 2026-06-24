import uuid
from datetime import date, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import JSON, Date, DateTime, ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ApplicationStatus(StrEnum):
    SAVED = "saved"
    SHORTLISTED = "shortlisted"
    APPLIED = "applied"
    OUTREACH_SENT = "outreach_sent"
    FOLLOW_UP_DUE = "follow_up_due"
    RECRUITER_REPLIED = "recruiter_replied"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    TECHNICAL_INTERVIEW = "technical_interview"
    FINAL_INTERVIEW = "final_interview"
    OFFER = "offer"
    REJECTED = "rejected"
    NO_RESPONSE = "no_response"
    WITHDRAWN = "withdrawn"


class Application(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_application_user_job"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    company_name: Mapped[str] = mapped_column(String(240), nullable=False)
    role_title: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[str] = mapped_column(
        String(60), default=ApplicationStatus.SAVED, nullable=False
    )
    date_applied: Mapped[date | None] = mapped_column(Date)
    contact_name: Mapped[str | None] = mapped_column(String(240))
    contact_email: Mapped[str | None] = mapped_column(String(320))
    contact_linkedin_url: Mapped[str | None] = mapped_column(String(2048))
    follow_up_date: Mapped[date | None] = mapped_column(Date)
    resume_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("generated_resumes.id", ondelete="SET NULL")
    )
    notes: Mapped[str | None] = mapped_column(Text)
    interview_stage: Mapped[str | None] = mapped_column(String(120))
    interview_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class InterviewPrepPlan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "interview_prep_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("applications.id", ondelete="SET NULL"), index=True
    )
    interview_stage: Mapped[str] = mapped_column(String(120), nullable=False)
    interview_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    technical_questions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    behavioral_questions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    company_research: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    mock_interview_plan: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    questions_to_ask: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    focus_areas: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    practice_answers: Mapped[dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)


class PortfolioProject(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "portfolio_projects"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="SET NULL"), index=True
    )
    name: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    github_url: Mapped[str | None] = mapped_column(String(2048))
    live_url: Mapped[str | None] = mapped_column(String(2048))
    tech_stack: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    role_alignment: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    audit_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    improvement_tasks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    codex_prompt: Mapped[str | None] = mapped_column(Text)


class WeeklyTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "weekly_tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    task_date: Mapped[date] = mapped_column(Date, nullable=False)
    day_label: Mapped[str] = mapped_column(String(20), nullable=False)
    task_type: Mapped[str] = mapped_column(String(60), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    related_job_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="SET NULL")
    )
    related_application_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("applications.id", ondelete="SET NULL")
    )

