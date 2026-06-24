import uuid
from datetime import date, datetime
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, EmailStr, Field


class ApplicationCreate(BaseModel):
    job_id: uuid.UUID
    status: str = "saved"
    date_applied: date | None = None
    contact_name: str | None = Field(default=None, max_length=240)
    contact_email: EmailStr | None = None
    contact_linkedin_url: AnyHttpUrl | None = None
    follow_up_date: date | None = None
    resume_id: uuid.UUID | None = None
    notes: str | None = Field(default=None, max_length=10_000)


class ApplicationUpdate(BaseModel):
    status: str | None = None
    date_applied: date | None = None
    contact_name: str | None = Field(default=None, max_length=240)
    contact_email: EmailStr | None = None
    contact_linkedin_url: AnyHttpUrl | None = None
    follow_up_date: date | None = None
    resume_id: uuid.UUID | None = None
    notes: str | None = Field(default=None, max_length=10_000)
    interview_stage: str | None = Field(default=None, max_length=120)
    interview_date: datetime | None = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    job_id: uuid.UUID
    company_name: str
    role_title: str
    status: str
    date_applied: date | None
    contact_name: str | None
    contact_email: str | None
    contact_linkedin_url: str | None
    follow_up_date: date | None
    resume_id: uuid.UUID | None
    notes: str | None
    interview_stage: str | None
    interview_date: datetime | None
    created_at: datetime
    updated_at: datetime


class ApplicationAnalytics(BaseModel):
    total_applications: int
    applied_this_week: int
    interviews: int
    offers: int
    rejections: int
    response_rate: float
    interview_rate: float
    average_match_score: float | None
    follow_ups_due: int


class InterviewPrepGenerate(BaseModel):
    job_id: uuid.UUID
    application_id: uuid.UUID | None = None
    interview_stage: str = Field(default="screening", max_length=120)
    interview_date: datetime | None = None


class InterviewPrepUpdate(BaseModel):
    interview_stage: str | None = Field(default=None, max_length=120)
    interview_date: datetime | None = None
    practice_answers: dict[str, str] | None = None


class InterviewPrepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    job_id: uuid.UUID
    application_id: uuid.UUID | None
    interview_stage: str
    interview_date: datetime | None
    technical_questions: list[dict[str, Any]]
    behavioral_questions: list[dict[str, Any]]
    company_research: list[str]
    mock_interview_plan: list[str]
    questions_to_ask: list[str]
    focus_areas: list[str]
    practice_answers: dict[str, str]
    created_at: datetime
    updated_at: datetime


class PortfolioCreate(BaseModel):
    project_id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=10, max_length=10_000)
    github_url: AnyHttpUrl | None = None
    live_url: AnyHttpUrl | None = None
    tech_stack: list[str] = []


class PortfolioUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = Field(default=None, min_length=10, max_length=10_000)
    github_url: AnyHttpUrl | None = None
    live_url: AnyHttpUrl | None = None
    tech_stack: list[str] | None = None
    improvement_tasks: list[dict[str, Any]] | None = None


class PortfolioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID | None
    name: str
    description: str
    github_url: str | None
    live_url: str | None
    tech_stack: list[str]
    role_alignment: list[str]
    audit_json: dict[str, Any]
    improvement_tasks: list[dict[str, Any]]
    codex_prompt: str | None
    created_at: datetime
    updated_at: datetime


class WeeklyGenerate(BaseModel):
    project_id: uuid.UUID


class WeeklyTaskUpdate(BaseModel):
    status: str = Field(pattern="^(pending|in_progress|complete|skipped)$")


class WeeklyTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    task_date: date
    day_label: str
    task_type: str
    title: str
    description: str
    status: str
    related_job_id: uuid.UUID | None
    related_application_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class WeeklySummary(BaseModel):
    total: int
    complete: int
    skipped: int
    completion_rate: float

