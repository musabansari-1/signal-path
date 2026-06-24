import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    target_role: str = Field(min_length=2, max_length=160)
    target_industry: str | None = Field(default=None, max_length=160)
    target_location: str | None = Field(default=None, max_length=160)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    target_role: str | None = Field(default=None, min_length=2, max_length=160)
    target_industry: str | None = Field(default=None, max_length=160)
    target_location: str | None = Field(default=None, max_length=160)
    status: ProjectStatus | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    target_role: str
    target_industry: str | None
    target_location: str | None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

