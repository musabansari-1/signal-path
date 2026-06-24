import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db import get_db
from app.models.project import JobSearchProject
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def owned_project(db: Session, user_id: uuid.UUID, project_id: uuid.UUID) -> JobSearchProject:
    project = db.scalar(
        select(JobSearchProject).where(
            JobSearchProject.id == project_id, JobSearchProject.user_id == user_id
        )
    )
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: DBSession,
    user: CurrentUser,
) -> JobSearchProject:
    project = JobSearchProject(user_id=user.id, **payload.model_dump())
    db.add(project)
    db.flush()
    if user.active_project_id is None:
        user.active_project_id = project.id
    db.commit()
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    db: DBSession, user: CurrentUser
) -> list[JobSearchProject]:
    return list(
        db.scalars(
            select(JobSearchProject)
            .where(JobSearchProject.user_id == user.id)
            .order_by(JobSearchProject.updated_at.desc())
        )
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: uuid.UUID,
    db: DBSession,
    user: CurrentUser,
) -> JobSearchProject:
    return owned_project(db, user.id, project_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: DBSession,
    user: CurrentUser,
) -> JobSearchProject:
    project = owned_project(db, user.id, project_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    return project


@router.post("/{project_id}/activate", response_model=ProjectResponse)
def activate_project(
    project_id: uuid.UUID,
    db: DBSession,
    user: CurrentUser,
) -> JobSearchProject:
    project = owned_project(db, user.id, project_id)
    user.active_project_id = project.id
    db.commit()
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID,
    db: DBSession,
    user: CurrentUser,
) -> Response:
    project = owned_project(db, user.id, project_id)
    if user.active_project_id == project.id:
        user.active_project_id = None
    db.delete(project)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
