import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.career_profile import profile_for_project
from app.api.routes.jobs import owned_job
from app.core.security import get_current_user
from app.db import get_db
from app.models.artifact import GeneratedMessage, GeneratedResume
from app.models.user import User
from app.schemas.artifact import (
    MessageGenerateRequest,
    MessageResponse,
    MessageUpdate,
    ResumeGenerateRequest,
    ResumeResponse,
    ResumeUpdate,
)
from app.services.artifact_export import export_resume_docx, export_resume_pdf
from app.services.message_generation import generate_grounded_message
from app.services.resume_generation import generate_grounded_resume

router = APIRouter(tags=["application artifacts"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def owned_resume(db: Session, user_id: uuid.UUID, resume_id: uuid.UUID) -> GeneratedResume:
    resume = db.scalar(
        select(GeneratedResume).where(
            GeneratedResume.id == resume_id, GeneratedResume.user_id == user_id
        )
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


def owned_message(db: Session, user_id: uuid.UUID, message_id: uuid.UUID) -> GeneratedMessage:
    message = db.scalar(
        select(GeneratedMessage).where(
            GeneratedMessage.id == message_id, GeneratedMessage.user_id == user_id
        )
    )
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.post("/resumes/generate", response_model=ResumeResponse, status_code=201)
def generate_resume(
    payload: ResumeGenerateRequest, db: DBSession, user: CurrentUser
) -> GeneratedResume:
    job = owned_job(db, user.id, payload.job_id)
    profile = profile_for_project(db, user.id, job.project_id)
    if not profile or not profile.verified_facts_json:
        raise HTTPException(
            status_code=422,
            detail="Review a candidate profile with verified facts before generating a resume",
        )
    content, markdown, checklist = generate_grounded_resume(profile, job)
    resume = GeneratedResume(
        user_id=user.id,
        project_id=job.project_id,
        job_id=job.id,
        title=payload.title or f"{job.title} at {job.company_name}",
        content_json=content,
        markdown_content=markdown,
        truthfulness_check_json=checklist,
    )
    db.add(resume)
    db.commit()
    return resume


@router.get("/resumes", response_model=list[ResumeResponse])
def list_resumes(
    project_id: uuid.UUID,
    db: DBSession,
    user: CurrentUser,
    job_id: uuid.UUID | None = None,
) -> list[GeneratedResume]:
    query = select(GeneratedResume).where(
        GeneratedResume.user_id == user.id, GeneratedResume.project_id == project_id
    )
    if job_id:
        query = query.where(GeneratedResume.job_id == job_id)
    return list(db.scalars(query.order_by(GeneratedResume.updated_at.desc())))


@router.get("/resumes/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: uuid.UUID, db: DBSession, user: CurrentUser) -> GeneratedResume:
    return owned_resume(db, user.id, resume_id)


@router.patch("/resumes/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: uuid.UUID, payload: ResumeUpdate, db: DBSession, user: CurrentUser
) -> GeneratedResume:
    resume = owned_resume(db, user.id, resume_id)
    checklist = dict(resume.truthfulness_check_json)
    content_changed = payload.content_json is not None or payload.markdown_content is not None
    if payload.title is not None:
        resume.title = payload.title
    if payload.content_json is not None:
        resume.content_json = payload.content_json
    if payload.markdown_content is not None:
        resume.markdown_content = payload.markdown_content
    if content_changed:
        checklist["ready_for_export"] = False
        checklist["user_confirmed_at"] = None
        checklist["warnings"] = list(
            dict.fromkeys(
                [
                    *checklist.get("warnings", []),
                    "Edited content requires a fresh truthfulness review.",
                ]
            )
        )
    if payload.confirm_truthfulness:
        checklist["ready_for_export"] = True
        checklist["user_confirmed_at"] = datetime.now(UTC).isoformat()
    resume.truthfulness_check_json = checklist
    db.commit()
    return resume


def _require_export_ready(resume: GeneratedResume) -> None:
    if not resume.truthfulness_check_json.get("ready_for_export"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Review and confirm the truthfulness checklist before export",
        )


@router.post("/resumes/{resume_id}/export-pdf")
def export_pdf(resume_id: uuid.UUID, db: DBSession, user: CurrentUser) -> FileResponse:
    resume = owned_resume(db, user.id, resume_id)
    _require_export_ready(resume)
    resume.export_pdf_path = export_resume_pdf(resume)
    db.commit()
    return FileResponse(
        resume.export_pdf_path,
        media_type="application/pdf",
        filename=f"{Path(resume.title).stem}-resume.pdf",
    )


@router.post("/resumes/{resume_id}/export-docx")
def export_docx(resume_id: uuid.UUID, db: DBSession, user: CurrentUser) -> FileResponse:
    resume = owned_resume(db, user.id, resume_id)
    _require_export_ready(resume)
    resume.export_docx_path = export_resume_docx(resume)
    db.commit()
    return FileResponse(
        resume.export_docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"{Path(resume.title).stem}-resume.docx",
    )


@router.post("/messages/generate", response_model=MessageResponse, status_code=201)
def generate_message(
    payload: MessageGenerateRequest, db: DBSession, user: CurrentUser
) -> GeneratedMessage:
    job = owned_job(db, user.id, payload.job_id)
    profile = profile_for_project(db, user.id, job.project_id)
    if not profile:
        raise HTTPException(status_code=422, detail="Complete your candidate profile first")
    subject, content, claims, warnings = generate_grounded_message(
        profile, job, payload.message_type, payload.tone, payload.length
    )
    message = GeneratedMessage(
        user_id=user.id,
        project_id=job.project_id,
        job_id=job.id,
        message_type=payload.message_type,
        tone=payload.tone,
        subject_line=subject,
        content=content,
        claims_used_json=claims,
        review_warnings_json=warnings,
    )
    db.add(message)
    db.commit()
    return message


@router.get("/messages", response_model=list[MessageResponse])
def list_messages(
    project_id: uuid.UUID,
    db: DBSession,
    user: CurrentUser,
    job_id: uuid.UUID | None = None,
) -> list[GeneratedMessage]:
    query = select(GeneratedMessage).where(
        GeneratedMessage.user_id == user.id, GeneratedMessage.project_id == project_id
    )
    if job_id:
        query = query.where(GeneratedMessage.job_id == job_id)
    return list(db.scalars(query.order_by(GeneratedMessage.updated_at.desc())))


@router.patch("/messages/{message_id}", response_model=MessageResponse)
def update_message(
    message_id: uuid.UUID, payload: MessageUpdate, db: DBSession, user: CurrentUser
) -> GeneratedMessage:
    message = owned_message(db, user.id, message_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(message, field, value)
    if payload.content is not None:
        message.review_warnings_json = list(
            dict.fromkeys(
                [*message.review_warnings_json, "Edited content requires your review before use."]
            )
        )
    db.commit()
    return message


@router.delete("/messages/{message_id}", status_code=204)
def delete_message(message_id: uuid.UUID, db: DBSession, user: CurrentUser) -> Response:
    message = owned_message(db, user.id, message_id)
    db.delete(message)
    db.commit()
    return Response(status_code=204)

