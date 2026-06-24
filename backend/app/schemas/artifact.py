import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResumeGenerateRequest(BaseModel):
    job_id: uuid.UUID
    title: str | None = Field(default=None, max_length=240)


class ResumeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    content_json: dict[str, Any] | None = None
    markdown_content: str | None = Field(default=None, min_length=1, max_length=100_000)
    confirm_truthfulness: bool = False


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    job_id: uuid.UUID
    title: str
    content_json: dict[str, Any]
    markdown_content: str
    export_pdf_path: str | None
    export_docx_path: str | None
    truthfulness_check_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class MessageGenerateRequest(BaseModel):
    job_id: uuid.UUID
    message_type: str = Field(
        pattern="^(cover_letter|recruiter_dm|hiring_manager_message|referral_request|follow_up|fit_summary)$"
    )
    tone: str = Field(
        default="professional",
        pattern="^(professional|warm|concise|confident|friendly|startup)$",
    )
    length: str = Field(default="concise", pattern="^(short|concise|standard)$")


class MessageUpdate(BaseModel):
    subject_line: str | None = Field(default=None, max_length=300)
    content: str | None = Field(default=None, min_length=1, max_length=20_000)
    tone: str | None = Field(default=None, max_length=40)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    job_id: uuid.UUID | None
    message_type: str
    tone: str
    subject_line: str | None
    content: str
    claims_used_json: list[dict[str, Any]]
    review_warnings_json: list[str]
    created_at: datetime
    updated_at: datetime
