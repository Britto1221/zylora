from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid5, NAMESPACE_DNS

import jwt
from fastapi import Depends, Header, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.entities import TenantMembership
from app.db.models.enums import MembershipRole
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=True)
settings = get_settings()
_jwks_client: PyJWKClient | None = None


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID
    email: str
    is_super_admin: bool


def create_development_token(email: str) -> str:
    if settings.is_production:
        raise RuntimeError("Development authentication is disabled in production.")
    normalized = email.strip().lower()
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(uuid5(NAMESPACE_DNS, normalized)),
            "email": normalized,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=12)).timestamp()),
            "iss": "zylora-development",
            "aud": settings.auth_audience,
        },
        settings.dev_auth_secret,
        algorithm="HS256",
    )


def get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        if not settings.auth_jwks_url:
            raise RuntimeError("AUTH_JWKS_URL is not configured.")
        _jwks_client = PyJWKClient(settings.auth_jwks_url, cache_keys=True, lifespan=3600)
    return _jwks_client


def decode_access_token(token: str) -> dict:
    try:
        if not settings.is_production and not settings.auth_jwks_url:
            return jwt.decode(
                token,
                settings.dev_auth_secret,
                algorithms=["HS256"],
                audience=settings.auth_audience,
                issuer="zylora-development",
                options={"require": ["exp", "iat", "sub"]},
            )
        signing_key = get_jwks_client().get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=settings.auth_algorithm_list,
            audience=settings.auth_audience,
            issuer=settings.auth_issuer,
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> AuthenticatedUser:
    claims = decode_access_token(credentials.credentials)
    try:
        user_id = UUID(str(claims["sub"]))
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token subject.") from exc
    email = str(claims.get("email", "")).strip().lower()
    return AuthenticatedUser(
        id=user_id,
        email=email,
        is_super_admin=email in settings.super_admin_email_set,
    )


def require_super_admin(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    if not user.is_super_admin:
        raise HTTPException(status_code=403, detail="Super-admin access required.")
    return user


def _membership(db: Session, tenant_id: UUID, user_id: UUID) -> TenantMembership | None:
    return db.scalar(
        select(TenantMembership).where(
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.user_id == user_id,
            TenantMembership.is_active.is_(True),
        )
    )


def require_tenant_access(
    tenant_id: UUID = Path(...),
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    if user.is_super_admin or _membership(db, tenant_id, user.id):
        return user
    raise HTTPException(status_code=403, detail="Cross-tenant access denied.")


def require_tenant_admin(
    tenant_id: UUID = Path(...),
    user: AuthenticatedUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    if user.is_super_admin:
        return user
    membership = _membership(db, tenant_id, user.id)
    if membership and membership.role == MembershipRole.CLIENT_ADMIN:
        return user
    raise HTTPException(status_code=403, detail="Client-admin access required.")


def require_worker_token(x_worker_token: str = Header(default="")) -> None:
    if x_worker_token != settings.internal_worker_token:
        raise HTTPException(status_code=401, detail="Invalid worker token.")
