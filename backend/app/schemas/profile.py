import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CareerAssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    asset_type: str
    title: str
    url: str | None
    file_name: str | None
    mime_type: str | None
    is_primary: bool
    created_at: datetime


class CareerLinkCreate(BaseModel):
    project_id: uuid.UUID
    asset_type: str = Field(pattern="^(linkedin|github|portfolio|project|certification|other)$")
    title: str = Field(min_length=2, max_length=240)
    url: HttpUrl


class AnalyzeProfileRequest(BaseModel):
    project_id: uuid.UUID


class CandidateProfileUpdate(BaseModel):
    headline: str | None = Field(default=None, max_length=240)
    summary: str | None = Field(default=None, max_length=5000)
    years_experience: float | None = Field(default=None, ge=0, le=80)
    location: str | None = Field(default=None, max_length=160)
    work_authorization: str | None = Field(default=None, max_length=240)
    skills_json: list[str] | None = None
    experience_json: list[dict[str, Any]] | None = None
    projects_json: list[dict[str, Any]] | None = None
    education_json: list[dict[str, Any]] | None = None
    certifications_json: list[dict[str, Any]] | None = None
    achievements_json: list[dict[str, Any]] | None = None


class CandidateProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    headline: str | None
    summary: str | None
    years_experience: float | None
    location: str | None
    work_authorization: str | None
    skills_json: list[str]
    experience_json: list[dict[str, Any]]
    projects_json: list[dict[str, Any]]
    education_json: list[dict[str, Any]]
    certifications_json: list[dict[str, Any]]
    achievements_json: list[dict[str, Any]]
    strengths_json: list[str]
    gaps_json: list[str]
    best_fit_roles_json: list[str]
    verified_facts_json: list[dict[str, Any]]
    suggestions_json: list[dict[str, Any]]
    reviewed_at: str | None
    updated_at: datetime

