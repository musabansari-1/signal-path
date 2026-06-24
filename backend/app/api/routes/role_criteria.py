import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.career_profile import profile_for_project
from app.api.routes.projects import owned_project
from app.core.security import get_current_user
from app.db import get_db
from app.models.profile import RoleCriteria
from app.models.user import User
from app.schemas.criteria import (
    RoleCriteriaPayload,
    RoleCriteriaResponse,
    RoleCriteriaSuggestion,
    RoleCriteriaUpdate,
)
from app.schemas.profile import AnalyzeProfileRequest

router = APIRouter(prefix="/role-criteria", tags=["role criteria"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def criteria_for_project(
    db: Session, user_id: uuid.UUID, project_id: uuid.UUID
) -> RoleCriteria | None:
    return db.scalar(
        select(RoleCriteria).where(
            RoleCriteria.user_id == user_id, RoleCriteria.project_id == project_id
        )
    )


@router.get("/{project_id}", response_model=RoleCriteriaResponse | None)
def get_role_criteria(
    project_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> RoleCriteria | None:
    owned_project(db, user.id, project_id)
    return criteria_for_project(db, user.id, project_id)


@router.post("", response_model=RoleCriteriaResponse, status_code=201)
def create_role_criteria(
    payload: RoleCriteriaPayload, db: DBSession, user: CurrentUser
) -> RoleCriteria:
    owned_project(db, user.id, payload.project_id)
    if criteria_for_project(db, user.id, payload.project_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Role criteria already exist"
        )
    criteria = RoleCriteria(user_id=user.id, **payload.model_dump())
    db.add(criteria)
    db.commit()
    return criteria


@router.patch("/{criteria_id}", response_model=RoleCriteriaResponse)
def update_role_criteria(
    criteria_id: uuid.UUID, payload: RoleCriteriaUpdate, db: DBSession, user: CurrentUser
) -> RoleCriteria:
    criteria = db.scalar(
        select(RoleCriteria).where(RoleCriteria.id == criteria_id, RoleCriteria.user_id == user.id)
    )
    if not criteria:
        raise HTTPException(status_code=404, detail="Role criteria not found")
    if payload.project_id != criteria.project_id:
        raise HTTPException(status_code=422, detail="Criteria cannot be moved between projects")
    for field, value in payload.model_dump().items():
        if field != "project_id":
            setattr(criteria, field, value)
    db.commit()
    return criteria


@router.post("/suggest", response_model=RoleCriteriaSuggestion)
def suggest_role_criteria(
    payload: AnalyzeProfileRequest, db: DBSession, user: CurrentUser
) -> RoleCriteriaSuggestion:
    project = owned_project(db, user.id, payload.project_id)
    profile = profile_for_project(db, user.id, payload.project_id)
    if not profile:
        raise HTTPException(status_code=422, detail="Analyze or complete your profile first")
    roles = profile.best_fit_roles_json or [project.target_role]
    return RoleCriteriaSuggestion(
        job_titles=roles[:5],
        required_skills=(profile.skills_json or [])[:10],
        notes=[
            "These suggestions come from your confirmed profile and project goal.",
            "Review them before saving; suggestions are never applied automatically.",
        ],
    )
