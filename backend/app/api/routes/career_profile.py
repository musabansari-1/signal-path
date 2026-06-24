import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.projects import owned_project
from app.core.security import get_current_user
from app.db import get_db
from app.models.profile import CandidateProfile, CareerAsset
from app.models.user import User
from app.schemas.profile import (
    AnalyzeProfileRequest,
    CandidateProfileResponse,
    CandidateProfileUpdate,
    CareerAssetResponse,
    CareerLinkCreate,
)
from app.services.career_assets import (
    extract_text,
    persist_upload,
    read_validated_upload,
    remove_upload,
)
from app.services.profile_analysis import analyze_assets, apply_analysis, mark_profile_reviewed

router = APIRouter(tags=["career profile"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def owned_asset(db: Session, user_id: uuid.UUID, asset_id: uuid.UUID) -> CareerAsset:
    asset = db.scalar(
        select(CareerAsset).where(CareerAsset.id == asset_id, CareerAsset.user_id == user_id)
    )
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Career asset not found")
    return asset


def profile_for_project(
    db: Session, user_id: uuid.UUID, project_id: uuid.UUID
) -> CandidateProfile | None:
    return db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == user_id, CandidateProfile.project_id == project_id
        )
    )


@router.post("/career-assets/upload", response_model=CareerAssetResponse, status_code=201)
def upload_career_asset(
    project_id: Annotated[uuid.UUID, Form()],
    file: Annotated[UploadFile, File()],
    db: DBSession,
    user: CurrentUser,
    asset_type: Annotated[str, Form()] = "resume",
    is_primary: Annotated[bool, Form()] = False,
) -> CareerAsset:
    owned_project(db, user.id, project_id)
    if asset_type not in {"resume", "previous_resume", "certification", "project", "other"}:
        raise HTTPException(status_code=422, detail="Unsupported career asset type")
    data, filename, mime_type = read_validated_upload(file)
    text = extract_text(data, filename)
    path = persist_upload(data, user.id, filename)
    if is_primary:
        for current in db.scalars(
            select(CareerAsset).where(
                CareerAsset.user_id == user.id,
                CareerAsset.project_id == project_id,
                CareerAsset.asset_type.in_(["resume", "previous_resume"]),
            )
        ):
            current.is_primary = False
    asset = CareerAsset(
        user_id=user.id,
        project_id=project_id,
        asset_type=asset_type,
        title=filename,
        file_path=path,
        file_name=filename,
        mime_type=mime_type,
        extracted_text=text,
        is_primary=is_primary,
    )
    db.add(asset)
    db.commit()
    return asset


@router.post("/career-assets", response_model=CareerAssetResponse, status_code=201)
def add_career_link(payload: CareerLinkCreate, db: DBSession, user: CurrentUser) -> CareerAsset:
    owned_project(db, user.id, payload.project_id)
    asset = CareerAsset(
        user_id=user.id,
        project_id=payload.project_id,
        asset_type=payload.asset_type,
        title=payload.title,
        url=str(payload.url),
    )
    db.add(asset)
    db.commit()
    return asset


@router.get("/career-assets", response_model=list[CareerAssetResponse])
def list_career_assets(
    project_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> list[CareerAsset]:
    owned_project(db, user.id, project_id)
    return list(
        db.scalars(
            select(CareerAsset)
            .where(CareerAsset.user_id == user.id, CareerAsset.project_id == project_id)
            .order_by(CareerAsset.created_at.desc())
        )
    )


@router.delete("/career-assets/{asset_id}", status_code=204)
def delete_career_asset(asset_id: uuid.UUID, db: DBSession, user: CurrentUser) -> Response:
    asset = owned_asset(db, user.id, asset_id)
    remove_upload(asset.file_path)
    db.delete(asset)
    db.commit()
    return Response(status_code=204)


@router.post("/candidate-profile/analyze", response_model=CandidateProfileResponse)
def analyze_candidate_profile(
    payload: AnalyzeProfileRequest, db: DBSession, user: CurrentUser
) -> CandidateProfile:
    owned_project(db, user.id, payload.project_id)
    assets = list(
        db.scalars(
            select(CareerAsset).where(
                CareerAsset.user_id == user.id,
                CareerAsset.project_id == payload.project_id,
                CareerAsset.extracted_text.is_not(None),
            )
        )
    )
    if not assets:
        raise HTTPException(status_code=422, detail="Upload a readable career file before analysis")
    profile = profile_for_project(db, user.id, payload.project_id)
    if not profile:
        profile = CandidateProfile(user_id=user.id, project_id=payload.project_id)
        db.add(profile)
    extraction, records = analyze_assets(assets)
    apply_analysis(profile, extraction, records)
    db.commit()
    return profile


@router.get("/candidate-profile", response_model=CandidateProfileResponse | None)
def get_candidate_profile(
    project_id: uuid.UUID, db: DBSession, user: CurrentUser
) -> CandidateProfile | None:
    owned_project(db, user.id, project_id)
    return profile_for_project(db, user.id, project_id)


@router.patch("/candidate-profile", response_model=CandidateProfileResponse)
def update_candidate_profile(
    project_id: uuid.UUID,
    payload: CandidateProfileUpdate,
    db: DBSession,
    user: CurrentUser,
) -> CandidateProfile:
    owned_project(db, user.id, project_id)
    profile = profile_for_project(db, user.id, project_id)
    if not profile:
        profile = CandidateProfile(user_id=user.id, project_id=project_id)
        db.add(profile)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(profile, field, value)
    manual_facts = [
        {
            "category": "skill",
            "value": skill,
            "source_asset_id": None,
            "evidence_quote": None,
            "verification": "user_confirmed",
        }
        for skill in (profile.skills_json or [])
    ]
    sourced = [
        fact
        for fact in (profile.verified_facts_json or [])
        if fact.get("verification") == "source_quote"
    ]
    profile.verified_facts_json = [*sourced, *manual_facts]
    mark_profile_reviewed(profile)
    db.commit()
    return profile
