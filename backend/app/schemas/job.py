import uuid
from datetime import datetime
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from app.models.job import JobStatus


class JobCreate(BaseModel):
    project_id: uuid.UUID
    company_name: str = Field(min_length=1, max_length=240)
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=20, max_length=200_000)
    source_url: AnyHttpUrl | None = None
    application_url: AnyHttpUrl | None = None
    location: str | None = Field(default=None, max_length=240)
    work_mode: str | None = Field(default=None, max_length=40)
    employment_type: str | None = Field(default=None, max_length=80)
    source_type: str = Field(default="manual", pattern="^(manual|url|csv|company_page|internet)$")


class JobUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=240)
    title: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = Field(default=None, min_length=20, max_length=200_000)
    source_url: AnyHttpUrl | None = None
    application_url: AnyHttpUrl | None = None
    location: str | None = Field(default=None, max_length=240)
    work_mode: str | None = Field(default=None, max_length=40)
    employment_type: str | None = Field(default=None, max_length=80)
    status: JobStatus | None = None


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    source_type: str
    source_url: str | None
    company_name: str
    title: str
    description: str
    location: str | None
    work_mode: str | None
    employment_type: str | None
    experience_level: str | None
    minimum_years_experience: float | None
    salary_min: int | None
    salary_max: int | None
    currency: str | None
    required_skills: list[str]
    nice_to_have_skills: list[str]
    responsibilities: list[str]
    qualifications: list[str]
    benefits: list[str]
    red_flags: list[str]
    missing_information: list[str]
    application_url: str | None
    parsed_json: dict[str, Any]
    status: JobStatus
    latest_score: int | None
    created_at: datetime
    updated_at: datetime


class JobScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    total_score: int
    skill_match_score: int
    experience_match_score: int
    criteria_match_score: int
    keyword_match_score: int
    location_fit_score: int
    growth_potential_score: int
    difficulty_score: int
    recommendation: str
    strengths: list[str]
    gaps: list[str]
    keywords_to_add: list[str]
    explanation: str
    application_strategy: str
    scored_at: datetime


class BulkScoreRequest(BaseModel):
    project_id: uuid.UUID
    job_ids: list[uuid.UUID] | None = None


class CsvImportResult(BaseModel):
    imported: int
    skipped: int
    errors: list[str]


class JobDiscoveryRequest(BaseModel):
    project_id: uuid.UUID
    limit: int = Field(default=15, ge=1, le=50)


class JobDiscoveryResult(BaseModel):
    searched_for: str
    imported: int
    skipped: int
    jobs: list[JobResponse]
