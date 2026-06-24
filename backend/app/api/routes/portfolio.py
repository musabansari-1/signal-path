import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.projects import owned_project
from app.core.security import get_current_user
from app.db import get_db
from app.models.execution import PortfolioProject
from app.models.user import User
from app.schemas.execution import PortfolioCreate, PortfolioResponse, PortfolioUpdate
from app.services.portfolio_audit import audit_portfolio_project, build_codex_prompt

router = APIRouter(prefix="/portfolio-projects", tags=["portfolio"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def owned_portfolio_project(
    db: Session, user_id: uuid.UUID, portfolio_id: uuid.UUID
) -> PortfolioProject:
    project = db.scalar(
        select(PortfolioProject).where(
            PortfolioProject.id == portfolio_id, PortfolioProject.user_id == user_id
        )
    )
    if not project:
        raise HTTPException(status_code=404, detail="Portfolio project not found")
    return project


def _portfolio_values(payload: PortfolioCreate | PortfolioUpdate) -> dict[str, object]:
    values = payload.model_dump(exclude_unset=True)
    for field in ("github_url", "live_url"):
        if values.get(field) is not None:
            values[field] = str(values[field])
    return values


@router.post("", response_model=PortfolioResponse, status_code=201)
def create_portfolio_project(
    payload: PortfolioCreate, db: DBSession, user: CurrentUser
) -> PortfolioProject:
    if payload.project_id:
        owned_project(db, user.id, payload.project_id)
    project = PortfolioProject(user_id=user.id, **_portfolio_values(payload))
    db.add(project)
    db.commit()
    return project


@router.get("", response_model=list[PortfolioResponse])
def list_portfolio_projects(
    db: DBSession, user: CurrentUser, project_id: uuid.UUID | None = None
) -> list[PortfolioProject]:
    query = select(PortfolioProject).where(PortfolioProject.user_id == user.id)
    if project_id:
        owned_project(db, user.id, project_id)
        query = query.where(
            (PortfolioProject.project_id == project_id)
            | (PortfolioProject.project_id.is_(None))
        )
    return list(db.scalars(query.order_by(PortfolioProject.updated_at.desc())))


@router.patch("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio_project(
    portfolio_id: uuid.UUID,
    payload: PortfolioUpdate,
    db: DBSession,
    user: CurrentUser,
) -> PortfolioProject:
    project = owned_portfolio_project(db, user.id, portfolio_id)
    for field, value in _portfolio_values(payload).items():
        setattr(project, field, value)
    db.commit()
    return project


@router.post("/{portfolio_id}/audit", response_model=PortfolioResponse)
def audit_project(
    portfolio_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> PortfolioProject:
    project = owned_portfolio_project(db, user.id, portfolio_id)
    target_role = None
    if project.project_id:
        target_role = owned_project(db, user.id, project.project_id).target_role
    audit = audit_portfolio_project(project, target_role)
    project.audit_json = audit
    project.role_alignment = audit["role_alignment"]
    project.improvement_tasks = audit["tasks"]
    db.commit()
    return project


@router.post("/{portfolio_id}/codex-prompt", response_model=PortfolioResponse)
def generate_codex_prompt(
    portfolio_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> PortfolioProject:
    project = owned_portfolio_project(db, user.id, portfolio_id)
    project.codex_prompt = build_codex_prompt(project)
    db.commit()
    return project

