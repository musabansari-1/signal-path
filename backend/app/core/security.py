import hashlib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, Literal

import jwt
from fastapi import Depends, HTTPException, Request, Response, status
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.models.user import RefreshSession, User

password_hasher = PasswordHash.recommended()
ACCESS_COOKIE = "rolewise_access"
REFRESH_COOKIE = "rolewise_refresh"


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def _encode_token(
    user_id: uuid.UUID,
    token_type: Literal["access", "refresh"],
    expires_delta: timedelta,
    jti: str | None = None,
) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": jti or uuid.uuid4().hex,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: Literal["access", "refresh"]) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session"
        ) from exc
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return payload


def token_fingerprint(jti: str) -> str:
    return hashlib.sha256(jti.encode("utf-8")).hexdigest()


def issue_token_pair(db: Session, user: User) -> TokenPair:
    now = datetime.now(UTC)
    jti = uuid.uuid4().hex
    refresh_expires = now + timedelta(days=settings.refresh_token_expire_days)
    db.add(
        RefreshSession(
            user_id=user.id,
            token_hash=token_fingerprint(jti),
            expires_at=refresh_expires,
            created_at=now,
        )
    )
    access_token = _encode_token(
        user.id, "access", timedelta(minutes=settings.access_token_expire_minutes)
    )
    refresh_token = _encode_token(
        user.id,
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
        jti=jti,
    )
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


def set_auth_cookies(response: Response, tokens: TokenPair) -> None:
    common = {
        "httponly": True,
        "secure": settings.auth_cookie_secure,
        "samesite": "lax",
    }
    response.set_cookie(
        ACCESS_COOKIE,
        tokens.access_token,
        max_age=settings.access_token_expire_minutes * 60,
        path="/api",
        **common,
    )
    response.set_cookie(
        REFRESH_COOKIE,
        tokens.refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/auth",
        **common,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/api")
    response.delete_cookie(REFRESH_COOKIE, path="/api/auth")


def _bearer_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        return authorization.removeprefix("Bearer ").strip()
    return None


DBSession = Annotated[Session, Depends(get_db)]


def get_current_user(request: Request, db: DBSession) -> User:
    token = request.cookies.get(ACCESS_COOKIE) or _bearer_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    payload = decode_token(token, "access")
    user = db.get(User, uuid.UUID(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account unavailable")
    return user


def get_refresh_session(db: Session, refresh_token: str) -> tuple[User, RefreshSession]:
    payload = decode_token(refresh_token, "refresh")
    fingerprint = token_fingerprint(payload["jti"])
    refresh_session = db.scalar(
        select(RefreshSession).where(RefreshSession.token_hash == fingerprint)
    )
    now = datetime.now(UTC)
    expires_at = refresh_session.expires_at if refresh_session else now
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if not refresh_session or refresh_session.revoked_at is not None or expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    user = db.get(User, refresh_session.user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account unavailable")
    return user, refresh_session
