from __future__ import annotations

from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import AuthenticatedUser, create_development_token, get_current_user
from app.db.models.entities import ClientInvitation, TenantMembership
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


class DevelopmentLogin(BaseModel):
    email: EmailStr
    password: str


@router.post("/development-login")
def development_login(payload: DevelopmentLogin, db: Session = Depends(get_db)) -> dict:
    if settings.is_production:
        raise HTTPException(status_code=404, detail="Not found.")
    email = str(payload.email).lower()
    permitted = email in settings.super_admin_email_set
    if not permitted:
        permitted = bool(
            db.scalar(
                select(TenantMembership.id).where(
                    TenantMembership.email == email,
                    TenantMembership.is_active.is_(True),
                )
            )
            or db.scalar(
                select(ClientInvitation.id).where(
                    ClientInvitation.email == email,
                    ClientInvitation.status == "PENDING",
                )
            )
        )
    if not permitted or payload.password != settings.dev_admin_password:
        raise HTTPException(status_code=401, detail="Invalid development credentials.")
    token = create_development_token(email)
    return {"access_token": token, "token_type": "bearer", "expires_in": 43200}


@router.get("/me")
def me(user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "is_super_admin": user.is_super_admin,
    }
