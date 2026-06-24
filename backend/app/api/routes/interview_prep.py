import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.applications import owned_application
from app.api.routes.career_profile import profile_for_project
from app.api.routes.jobs import owned_job
from app.api.routes.projects import owned_project
from app.core.security import get_current_user
from app.db import get_db
from app.models.execution import InterviewPrepPlan
from app.models.user import User
from app.schemas.execution import (
    InterviewPrepGenerate,
    InterviewPrepResponse,
    InterviewPrepUpdate,
)
from app.services.interview_prep import build_interview_prep

router = APIRouter(prefix="/interview-prep", tags=["interview prep"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def owned_plan(db: Session, user_id: uuid.UUID, plan_id: uuid.UUID) -> InterviewPrepPlan:
    plan = db.scalar(
        select(InterviewPrepPlan).where(
            InterviewPrepPlan.id == plan_id, InterviewPrepPlan.user_id == user_id
        )
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Interview plan not found")
    return plan


@router.post("/generate", response_model=InterviewPrepResponse, status_code=201)
def generate_interview_prep(
    payload: InterviewPrepGenerate, db: DBSession, user: CurrentUser
) -> InterviewPrepPlan:
    job = owned_job(db, user.id, payload.job_id)
    profile = profile_for_project(db, user.id, job.project_id)
    if not profile:
        raise HTTPException(status_code=422, detail="Complete your candidate profile first")
    if payload.application_id:
        application = owned_application(db, user.id, payload.application_id)
        if application.job_id != job.id:
            raise HTTPException(status_code=422, detail="Application belongs to a different job")
    content = build_interview_prep(profile, job, payload.interview_stage)
    plan = InterviewPrepPlan(
        user_id=user.id,
        project_id=job.project_id,
        job_id=job.id,
        application_id=payload.application_id,
        interview_stage=payload.interview_stage,
        interview_date=payload.interview_date,
        **content,
    )
    db.add(plan)
    db.commit()
    return plan


@router.get("", response_model=list[InterviewPrepResponse])
def list_interview_prep(
    project_id: uuid.UUID,
    db: DBSession,
    user: CurrentUser,
    application_id: uuid.UUID | None = None,
) -> list[InterviewPrepPlan]:
    owned_project(db, user.id, project_id)
    query = select(InterviewPrepPlan).where(
        InterviewPrepPlan.user_id == user.id,
        InterviewPrepPlan.project_id == project_id,
    )
    if application_id:
        query = query.where(InterviewPrepPlan.application_id == application_id)
    return list(db.scalars(query.order_by(InterviewPrepPlan.updated_at.desc())))


@router.patch("/{plan_id}", response_model=InterviewPrepResponse)
def update_interview_prep(
    plan_id: uuid.UUID,
    payload: InterviewPrepUpdate,
    db: DBSession,
    user: CurrentUser,
) -> InterviewPrepPlan:
    plan = owned_plan(db, user.id, plan_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    db.commit()
    return plan


@router.post("/{plan_id}/generate-questions", response_model=InterviewPrepResponse)
def regenerate_questions(
    plan_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> InterviewPrepPlan:
    plan = owned_plan(db, user.id, plan_id)
    job = owned_job(db, user.id, plan.job_id)
    profile = profile_for_project(db, user.id, plan.project_id)
    if not profile:
        raise HTTPException(status_code=422, detail="Candidate profile unavailable")
    content = build_interview_prep(profile, job, plan.interview_stage)
    for field, value in content.items():
        setattr(plan, field, value)
    db.commit()
    return plan

