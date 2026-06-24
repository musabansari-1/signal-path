from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import (
    REFRESH_COOKIE,
    clear_auth_cookies,
    get_current_user,
    get_refresh_session,
    hash_password,
    issue_token_pair,
    set_auth_cookies,
    verify_password,
)
from app.db import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: DBSession) -> User:
    email = payload.email.lower()
    if db.scalar(select(User).where(func.lower(User.email) == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    tokens = issue_token_pair(db, user)
    db.commit()
    set_auth_cookies(response, tokens)
    return user


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest, response: Response, db: DBSession) -> User:
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    tokens = issue_token_pair(db, user)
    db.commit()
    set_auth_cookies(response, tokens)
    return user


@router.get("/me", response_model=UserResponse)
def me(current_user: CurrentUser) -> User:
    return current_user


@router.post("/refresh", response_model=UserResponse)
def refresh(request: Request, response: Response, db: DBSession) -> User:
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    user, old_session = get_refresh_session(db, refresh_token)
    old_session.revoked_at = datetime.now(UTC)
    tokens = issue_token_pair(db, user)
    db.commit()
    set_auth_cookies(response, tokens)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: DBSession) -> Response:
    refresh_token = request.cookies.get(REFRESH_COOKIE)
    if refresh_token:
        try:
            _, refresh_session = get_refresh_session(db, refresh_token)
            refresh_session.revoked_at = datetime.now(UTC)
            db.commit()
        except HTTPException:
            pass
    clear_auth_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
