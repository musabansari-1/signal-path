import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RoleCriteriaPayload(BaseModel):
    project_id: uuid.UUID
    job_titles: list[str] = []
    industries: list[str] = []
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=8)
    locations: list[str] = []
    work_modes: list[str] = []
    experience_levels: list[str] = []
    required_skills: list[str] = []
    nice_to_have_skills: list[str] = []
    company_sizes: list[str] = []
    roles_to_avoid: list[str] = []
    industries_to_avoid: list[str] = []
    visa_preference: str | None = Field(default=None, max_length=160)
    company_stage_preference: str | None = Field(default=None, max_length=160)
    notes: str | None = Field(default=None, max_length=3000)

    @model_validator(mode="after")
    def salary_range_is_valid(self) -> "RoleCriteriaPayload":
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValueError("Minimum salary must not exceed maximum salary")
        return self


class RoleCriteriaUpdate(RoleCriteriaPayload):
    project_id: uuid.UUID


class RoleCriteriaResponse(RoleCriteriaPayload):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RoleCriteriaSuggestion(BaseModel):
    job_titles: list[str]
    required_skills: list[str]
    notes: list[str]
    requires_confirmation: bool = True
