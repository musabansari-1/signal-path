import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db import get_db
from app.models.operations import BackgroundJob
from app.models.user import User
from app.schemas.operations import BackgroundJobResponse

router = APIRouter(prefix="/background-jobs", tags=["operations"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=list[BackgroundJobResponse])
def list_background_jobs(
    db: DBSession, user: CurrentUser, project_id: uuid.UUID | None = None
) -> list[BackgroundJob]:
    query = select(BackgroundJob).where(BackgroundJob.user_id == user.id)
    if project_id:
        query = query.where(BackgroundJob.project_id == project_id)
    return list(db.scalars(query.order_by(BackgroundJob.created_at.desc()).limit(100)))

