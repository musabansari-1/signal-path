import uuid
from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.artifacts import owned_resume
from app.api.routes.jobs import owned_job
from app.api.routes.projects import owned_project
from app.core.security import get_current_user
from app.db import get_db
from app.models.execution import Application, ApplicationStatus
from app.models.job import Job, JobStatus
from app.models.user import User
from app.schemas.execution import (
    ApplicationAnalytics,
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)

router = APIRouter(prefix="/applications", tags=["applications"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
VALID_STATUSES = {status.value for status in ApplicationStatus}
INTERVIEW_STATUSES = {
    ApplicationStatus.INTERVIEW_SCHEDULED,
    ApplicationStatus.TECHNICAL_INTERVIEW,
    ApplicationStatus.FINAL_INTERVIEW,
    ApplicationStatus.OFFER,
}
RESPONSE_STATUSES = {
    ApplicationStatus.RECRUITER_REPLIED,
    *INTERVIEW_STATUSES,
    ApplicationStatus.REJECTED,
}


def owned_application(
    db: Session, user_id: uuid.UUID, application_id: uuid.UUID
) -> Application:
    application = db.scalar(
        select(Application).where(
            Application.id == application_id, Application.user_id == user_id
        )
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


def _values(payload: ApplicationCreate | ApplicationUpdate) -> dict[str, object]:
    values = payload.model_dump(exclude_unset=True)
    if values.get("contact_linkedin_url") is not None:
        values["contact_linkedin_url"] = str(values["contact_linkedin_url"])
    if values.get("contact_email") is not None:
        values["contact_email"] = str(values["contact_email"])
    return values


@router.post("", response_model=ApplicationResponse, status_code=201)
def create_application(
    payload: ApplicationCreate, db: DBSession, user: CurrentUser
) -> Application:
    job = owned_job(db, user.id, payload.job_id)
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Unsupported application status")
    if db.scalar(
        select(Application).where(
            Application.user_id == user.id, Application.job_id == job.id
        )
    ):
        raise HTTPException(
            status_code=409, detail="This job is already in your application tracker"
        )
    if payload.resume_id:
        resume = owned_resume(db, user.id, payload.resume_id)
        if resume.job_id != job.id:
            raise HTTPException(status_code=422, detail="Resume belongs to a different job")
    values = _values(payload)
    values.pop("job_id", None)
    application = Application(
        user_id=user.id,
        project_id=job.project_id,
        job_id=job.id,
        company_name=job.company_name,
        role_title=job.title,
        **values,
    )
    if application.status == ApplicationStatus.APPLIED and not application.date_applied:
        application.date_applied = date.today()
    if application.status == ApplicationStatus.APPLIED:
        job.status = JobStatus.APPLIED
    db.add(application)
    db.commit()
    return application


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    project_id: uuid.UUID,
    db: DBSession,
    user: CurrentUser,
    application_status: str | None = None,
) -> list[Application]:
    owned_project(db, user.id, project_id)
    query = select(Application).where(
        Application.user_id == user.id, Application.project_id == project_id
    )
    if application_status:
        query = query.where(Application.status == application_status)
    return list(db.scalars(query.order_by(Application.updated_at.desc())))


@router.get("/analytics", response_model=ApplicationAnalytics)
def application_analytics(
    project_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> ApplicationAnalytics:
    owned_project(db, user.id, project_id)
    applications = list(
        db.scalars(
            select(Application).where(
                Application.user_id == user.id, Application.project_id == project_id
            )
        )
    )
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    applied = [item for item in applications if item.date_applied]
    responses = [item for item in applications if item.status in RESPONSE_STATUSES]
    interviews = [item for item in applications if item.status in INTERVIEW_STATUSES]
    scores = [
        score
        for score in db.scalars(
            select(Job.latest_score).where(
                Job.user_id == user.id,
                Job.project_id == project_id,
                Job.latest_score.is_not(None),
            )
        )
        if score is not None
    ]
    due = [
        item
        for item in applications
        if item.follow_up_date
        and item.follow_up_date <= today
        and item.status not in {ApplicationStatus.REJECTED, ApplicationStatus.OFFER}
    ]
    applied_count = len(applied)
    return ApplicationAnalytics(
        total_applications=len(applications),
        applied_this_week=sum(1 for item in applied if item.date_applied >= monday),
        interviews=len(interviews),
        offers=sum(1 for item in applications if item.status == ApplicationStatus.OFFER),
        rejections=sum(1 for item in applications if item.status == ApplicationStatus.REJECTED),
        response_rate=round(len(responses) / applied_count * 100, 1) if applied_count else 0,
        interview_rate=round(len(interviews) / applied_count * 100, 1) if applied_count else 0,
        average_match_score=round(sum(scores) / len(scores), 1) if scores else None,
        follow_ups_due=len(due),
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> Application:
    return owned_application(db, user.id, application_id)


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: uuid.UUID,
    payload: ApplicationUpdate,
    db: DBSession,
    user: CurrentUser,
) -> Application:
    application = owned_application(db, user.id, application_id)
    values = _values(payload)
    if payload.status and payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Unsupported application status")
    if payload.resume_id:
        resume = owned_resume(db, user.id, payload.resume_id)
        if resume.job_id != application.job_id:
            raise HTTPException(status_code=422, detail="Resume belongs to a different job")
    for field, value in values.items():
        setattr(application, field, value)
    if payload.status == ApplicationStatus.APPLIED and not application.date_applied:
        application.date_applied = date.today()
    db.commit()
    return application


@router.delete("/{application_id}", status_code=204)
def delete_application(
    application_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> Response:
    application = owned_application(db, user.id, application_id)
    db.delete(application)
    db.commit()
    return Response(status_code=204)
