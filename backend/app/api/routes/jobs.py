import csv
import io
import uuid
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.career_profile import profile_for_project
from app.api.routes.projects import owned_project
from app.api.routes.role_criteria import criteria_for_project
from app.core.security import get_current_user
from app.db import get_db
from app.models.job import Job, JobScore
from app.models.user import User
from app.schemas.job import (
    BulkScoreRequest,
    CsvImportResult,
    JobCreate,
    JobDiscoveryRequest,
    JobDiscoveryResult,
    JobResponse,
    JobScoreResponse,
    JobUpdate,
)
from app.services.job_discovery import (
    build_discovery_query,
    discover_remote_jobs,
    normalize_listing_url,
)
from app.services.job_parser import apply_job_extraction, deterministic_job_extraction, parse_job
from app.services.job_scoring import compute_job_score

router = APIRouter(prefix="/jobs", tags=["jobs"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def owned_job(db: Session, user_id: uuid.UUID, job_id: uuid.UUID) -> Job:
    job = db.scalar(select(Job).where(Job.id == job_id, Job.user_id == user_id))
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


def _job_values(payload: JobCreate | JobUpdate) -> dict[str, object]:
    values = payload.model_dump(exclude_unset=True)
    for field in ("source_url", "application_url"):
        if values.get(field) is not None:
            values[field] = str(values[field])
    return values


@router.post("", response_model=JobResponse, status_code=201)
def create_job(payload: JobCreate, db: DBSession, user: CurrentUser) -> Job:
    owned_project(db, user.id, payload.project_id)
    job = Job(user_id=user.id, **_job_values(payload))
    db.add(job)
    db.commit()
    return job


@router.get("", response_model=list[JobResponse])
def list_jobs(
    project_id: uuid.UUID,
    db: DBSession,
    user: CurrentUser,
    job_status: str | None = None,
    min_score: int | None = None,
    search: str | None = None,
) -> list[Job]:
    owned_project(db, user.id, project_id)
    query = select(Job).where(Job.user_id == user.id, Job.project_id == project_id)
    if job_status:
        query = query.where(Job.status == job_status)
    if min_score is not None:
        query = query.where(Job.latest_score >= min_score)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.where(Job.title.ilike(pattern) | Job.company_name.ilike(pattern))
    return list(db.scalars(query.order_by(Job.created_at.desc())))


@router.post("/discover", response_model=JobDiscoveryResult)
def discover_jobs(
    payload: JobDiscoveryRequest, db: DBSession, user: CurrentUser
) -> JobDiscoveryResult:
    """Find live remote listings matching the candidate profile and save new ones."""
    project = owned_project(db, user.id, payload.project_id)
    profile = profile_for_project(db, user.id, payload.project_id)
    if not profile:
        raise HTTPException(
            status_code=422, detail="Complete your candidate profile before discovering jobs"
        )
    criteria = criteria_for_project(db, user.id, payload.project_id)
    query = build_discovery_query(profile, criteria, project.target_role)
    if not query:
        raise HTTPException(
            status_code=422, detail="Add a target role or skills before discovering jobs"
        )
    try:
        listings = discover_remote_jobs(query, payload.limit)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail="Job discovery is temporarily unavailable. Please try again."
        ) from exc

    known_urls = {
        normalize_listing_url(url)
        for url in db.scalars(
            select(Job.source_url).where(
                Job.user_id == user.id,
                Job.project_id == payload.project_id,
                Job.source_url.is_not(None),
            )
        )
        if url
    }
    imported_jobs: list[Job] = []
    skipped = 0
    for listing in listings:
        listing_url = normalize_listing_url(listing.url)
        if listing_url in known_urls:
            skipped += 1
            continue
        job = Job(
            user_id=user.id,
            project_id=payload.project_id,
            source_type="internet",
            source_url=listing_url,
            application_url=listing_url,
            company_name=listing.company_name,
            title=listing.title,
            description=listing.description,
            location=listing.location,
            work_mode="remote",
            employment_type=listing.employment_type,
        )
        # Live discovery should remain fast and not consume an LLM call for every listing.
        apply_job_extraction(job, deterministic_job_extraction(job.description))
        db.add(job)
        db.flush()
        score = compute_job_score(job, profile, criteria)
        db.add(score)
        imported_jobs.append(job)
        known_urls.add(listing_url)
    db.commit()
    return JobDiscoveryResult(
        searched_for=query, imported=len(imported_jobs), skipped=skipped, jobs=imported_jobs
    )


@router.post("/import-csv", response_model=CsvImportResult)
def import_jobs_csv(
    project_id: Annotated[uuid.UUID, Form()],
    file: Annotated[UploadFile, File()],
    db: DBSession,
    user: CurrentUser,
) -> CsvImportResult:
    owned_project(db, user.id, project_id)
    data = file.file.read(2_000_001)
    if len(data) > 2_000_000:
        raise HTTPException(status_code=413, detail="CSV files must be smaller than 2 MB")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=422, detail="CSV must use UTF-8 encoding") from exc
    reader = csv.DictReader(io.StringIO(text))
    required_headers = {"company_name", "title", "description"}
    if not reader.fieldnames or not required_headers.issubset(reader.fieldnames):
        raise HTTPException(
            status_code=422,
            detail="CSV requires company_name, title, and description columns",
        )
    imported = 0
    skipped = 0
    errors: list[str] = []
    for row_number, row in enumerate(reader, start=2):
        if imported + skipped >= 500:
            errors.append("Import stopped at the 500-row limit")
            break
        if not all((row.get(header) or "").strip() for header in required_headers):
            skipped += 1
            errors.append(f"Row {row_number}: missing a required value")
            continue
        job = Job(
            user_id=user.id,
            project_id=project_id,
            source_type="csv",
            company_name=row["company_name"].strip(),
            title=row["title"].strip(),
            description=row["description"].strip()[:200_000],
            location=(row.get("location") or "").strip() or None,
            work_mode=(row.get("work_mode") or "").strip().lower() or None,
            source_url=(row.get("source_url") or "").strip() or None,
            application_url=(row.get("application_url") or "").strip() or None,
        )
        db.add(job)
        imported += 1
    db.commit()
    return CsvImportResult(imported=imported, skipped=skipped, errors=errors[:25])


@router.post("/score-bulk", response_model=list[JobScoreResponse])
def score_jobs_bulk(
    payload: BulkScoreRequest, db: DBSession, user: CurrentUser
) -> list[JobScore]:
    owned_project(db, user.id, payload.project_id)
    profile = profile_for_project(db, user.id, payload.project_id)
    if not profile:
        raise HTTPException(
            status_code=422, detail="Complete your candidate profile before scoring"
        )
    criteria = criteria_for_project(db, user.id, payload.project_id)
    query = select(Job).where(Job.user_id == user.id, Job.project_id == payload.project_id)
    if payload.job_ids:
        query = query.where(Job.id.in_(payload.job_ids))
    scores: list[JobScore] = []
    for job in db.scalars(query):
        existing = db.scalar(select(JobScore).where(JobScore.job_id == job.id))
        score = compute_job_score(job, profile, criteria, existing)
        if not existing:
            db.add(score)
        scores.append(score)
    db.commit()
    return scores


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: uuid.UUID, db: DBSession, user: CurrentUser) -> Job:
    return owned_job(db, user.id, job_id)


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(job_id: uuid.UUID, payload: JobUpdate, db: DBSession, user: CurrentUser) -> Job:
    job = owned_job(db, user.id, job_id)
    for field, value in _job_values(payload).items():
        setattr(job, field, value)
    db.commit()
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: uuid.UUID, db: DBSession, user: CurrentUser) -> Response:
    job = owned_job(db, user.id, job_id)
    db.delete(job)
    db.commit()
    return Response(status_code=204)


@router.post("/{job_id}/parse", response_model=JobResponse)
def parse_saved_job(job_id: uuid.UUID, db: DBSession, user: CurrentUser) -> Job:
    job = owned_job(db, user.id, job_id)
    apply_job_extraction(job, parse_job(job))
    db.commit()
    return job


@router.post("/{job_id}/score", response_model=JobScoreResponse)
def score_job(job_id: uuid.UUID, db: DBSession, user: CurrentUser) -> JobScore:
    job = owned_job(db, user.id, job_id)
    profile = profile_for_project(db, user.id, job.project_id)
    if not profile:
        raise HTTPException(
            status_code=422, detail="Complete your candidate profile before scoring"
        )
    criteria = criteria_for_project(db, user.id, job.project_id)
    existing = db.scalar(select(JobScore).where(JobScore.job_id == job.id))
    score = compute_job_score(job, profile, criteria, existing)
    if not existing:
        db.add(score)
    db.commit()
    return score


@router.get("/{job_id}/score", response_model=JobScoreResponse | None)
def get_job_score(job_id: uuid.UUID, db: DBSession, user: CurrentUser) -> JobScore | None:
    job = owned_job(db, user.id, job_id)
    return db.scalar(
        select(JobScore).where(JobScore.job_id == job.id, JobScore.user_id == user.id)
    )
