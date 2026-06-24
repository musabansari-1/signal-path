import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.projects import owned_project
from app.core.security import get_current_user
from app.db import get_db
from app.models.execution import Application, WeeklyTask
from app.models.job import Job
from app.models.user import User
from app.schemas.execution import (
    WeeklyGenerate,
    WeeklySummary,
    WeeklyTaskResponse,
    WeeklyTaskUpdate,
)
from app.services.weekly_plan import week_bounds, weekly_task_specs

router = APIRouter(tags=["weekly plan"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/weekly-plan", response_model=list[WeeklyTaskResponse])
def get_weekly_plan(
    project_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> list[WeeklyTask]:
    owned_project(db, user.id, project_id)
    start, end = week_bounds()
    return list(
        db.scalars(
            select(WeeklyTask)
            .where(
                WeeklyTask.user_id == user.id,
                WeeklyTask.project_id == project_id,
                WeeklyTask.task_date >= start,
                WeeklyTask.task_date <= end,
            )
            .order_by(WeeklyTask.task_date)
        )
    )


@router.post("/weekly-plan/generate", response_model=list[WeeklyTaskResponse])
def generate_weekly_plan(
    payload: WeeklyGenerate, db: DBSession, user: CurrentUser
) -> list[WeeklyTask]:
    owned_project(db, user.id, payload.project_id)
    start, end = week_bounds()
    existing = list(
        db.scalars(
            select(WeeklyTask).where(
                WeeklyTask.user_id == user.id,
                WeeklyTask.project_id == payload.project_id,
                WeeklyTask.task_date >= start,
                WeeklyTask.task_date <= end,
            )
        )
    )
    if existing:
        return sorted(existing, key=lambda task: task.task_date)
    jobs = list(
        db.scalars(
            select(Job).where(Job.user_id == user.id, Job.project_id == payload.project_id)
        )
    )
    applications = list(
        db.scalars(
            select(Application).where(
                Application.user_id == user.id,
                Application.project_id == payload.project_id,
            )
        )
    )
    due = sum(
        1
        for application in applications
        if application.follow_up_date and application.follow_up_date <= date.today()
    )
    tasks = [
        WeeklyTask(user_id=user.id, project_id=payload.project_id, **spec)
        for spec in weekly_task_specs(len(jobs), len(applications), due)
    ]
    db.add_all(tasks)
    db.commit()
    return tasks


def owned_weekly_task(
    db: Session, user_id: uuid.UUID, task_id: uuid.UUID
) -> WeeklyTask:
    task = db.scalar(
        select(WeeklyTask).where(WeeklyTask.id == task_id, WeeklyTask.user_id == user_id)
    )
    if not task:
        raise HTTPException(status_code=404, detail="Weekly task not found")
    return task


@router.patch("/weekly-tasks/{task_id}", response_model=WeeklyTaskResponse)
def update_weekly_task(
    task_id: uuid.UUID,
    payload: WeeklyTaskUpdate,
    db: DBSession,
    user: CurrentUser,
) -> WeeklyTask:
    task = owned_weekly_task(db, user.id, task_id)
    task.status = payload.status
    db.commit()
    return task


@router.get("/weekly-plan/summary", response_model=WeeklySummary)
def weekly_summary(
    project_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> WeeklySummary:
    tasks = get_weekly_plan(project_id, db, user)
    complete = sum(1 for task in tasks if task.status == "complete")
    skipped = sum(1 for task in tasks if task.status == "skipped")
    return WeeklySummary(
        total=len(tasks),
        complete=complete,
        skipped=skipped,
        completion_rate=round(complete / len(tasks) * 100, 1) if tasks else 0,
    )

