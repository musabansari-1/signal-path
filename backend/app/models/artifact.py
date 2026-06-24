import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class GeneratedResume(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "generated_resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    content_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    export_pdf_path: Mapped[str | None] = mapped_column(String(1024))
    export_docx_path: Mapped[str | None] = mapped_column(String(1024))
    truthfulness_check_json: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )


class GeneratedMessage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "generated_messages"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("job_search_projects.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="SET NULL"), index=True
    )
    application_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    message_type: Mapped[str] = mapped_column(String(60), nullable=False)
    tone: Mapped[str] = mapped_column(String(40), nullable=False)
    subject_line: Mapped[str | None] = mapped_column(String(300))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    claims_used_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, default=list, nullable=False
    )
    review_warnings_json: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

