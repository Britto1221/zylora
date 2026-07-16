from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.encryption import SecretCipher, mask_secret
from app.core.security import (
    AuthenticatedUser,
    get_current_user,
    require_super_admin,
    require_tenant_access,
)
from app.core.serialization import model_dict
from app.db.models.entities import (
    ApiCredential,
    ClientInvitation,
    Tenant,
    TenantMembership,
)
from app.db.models.enums import MembershipRole
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.email.service import send_email

router = APIRouter(prefix="/access", tags=["access"])
settings = get_settings()


class InvitationCreate(BaseModel):
    email: EmailStr
    role: MembershipRole = MembershipRole.CLIENT_ADMIN
    expires_days: int = Field(default=7, ge=1, le=30)


class InvitationAccept(BaseModel):
    token: str = Field(min_length=20, max_length=500)


class CredentialCreate(BaseModel):
    provider: str = Field(pattern=r"^(openai|anthropic|google)$")
    secret: str = Field(min_length=10, max_length=1000)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


@router.get("/{tenant_id}/members")
def members(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    memberships = db.scalars(
        select(TenantMembership)
        .where(TenantMembership.tenant_id == tenant_id)
        .order_by(TenantMembership.created_at)
    ).all()
    invitations = db.scalars(
        select(ClientInvitation)
        .where(ClientInvitation.tenant_id == tenant_id)
        .order_by(ClientInvitation.created_at.desc())
    ).all()
    credentials = db.scalars(
        select(ApiCredential)
        .where(ApiCredential.tenant_id == tenant_id)
        .order_by(ApiCredential.provider)
    ).all()
    return {
        "members": [model_dict(item) for item in memberships],
        "invitations": [model_dict(item) for item in invitations],
        "credentials": [
            {
                "id": str(item.id),
                "provider": item.provider,
                "masked": f"••••••••{item.secret_last_four}",
                "status": item.status,
                "lastVerifiedAt": item.last_verified_at.isoformat() if item.last_verified_at else None,
            }
            for item in credentials
        ],
    }


@router.post("/{tenant_id}/invitations", status_code=status.HTTP_201_CREATED)
def create_invitation(
    tenant_id: UUID,
    payload: InvitationCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Client not found.")
    email = str(payload.email).lower()
    existing = db.scalar(
        select(TenantMembership).where(
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.email == email,
            TenantMembership.is_active.is_(True),
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="This user already has access.")

    raw_token = secrets.token_urlsafe(36)
    invitation = ClientInvitation(
        tenant_id=tenant_id,
        email=email,
        role=payload.role,
        token_hash=token_hash(raw_token),
        expires_at=datetime.utcnow() + timedelta(days=payload.expires_days),
        invited_by=user.id,
    )
    db.add(invitation)
    db.flush()
    invite_url = (
        f"{settings.web_origin}/invite?token={raw_token}"
        f"&tenant={tenant.slug}"
    )
    delivery = send_email(
        to=email,
        subject=f"You have been invited to {tenant.name} on Zylora",
        text=(
            f"Use this secure invitation link before {invitation.expires_at.isoformat()}: "
            f"{invite_url}"
        ),
        idempotency_key=f"invitation:{invitation.id}",
    )
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="client_invitation",
        entity_id=invitation.id,
        action="access.invitation_created",
        payload={"email": email, "role": payload.role.value},
    )
    db.commit()
    result = model_dict(invitation)
    # Raw tokens are returned only in local development to enable complete local testing.
    if not settings.is_production:
        result["developmentToken"] = raw_token
        result["developmentUrl"] = invite_url
    result["delivery"] = delivery
    return result


@router.post("/invitations/accept")
def accept_invitation(
    payload: InvitationAccept,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user),
) -> dict:
    invitation = db.scalar(
        select(ClientInvitation).where(
            ClientInvitation.token_hash == token_hash(payload.token)
        )
    )
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found.")
    if invitation.status != "PENDING":
        raise HTTPException(status_code=409, detail="Invitation is no longer active.")
    if invitation.expires_at < datetime.utcnow():
        invitation.status = "EXPIRED"
        db.commit()
        raise HTTPException(status_code=410, detail="Invitation has expired.")
    if invitation.email.lower() != user.email.lower():
        raise HTTPException(status_code=403, detail="Invitation email does not match this account.")

    membership = db.scalar(
        select(TenantMembership).where(
            TenantMembership.tenant_id == invitation.tenant_id,
            TenantMembership.user_id == user.id,
        )
    )
    if not membership:
        membership = TenantMembership(
            tenant_id=invitation.tenant_id,
            user_id=user.id,
            email=user.email,
            role=invitation.role,
        )
        db.add(membership)
    else:
        membership.is_active = True
        membership.role = invitation.role
    invitation.status = "ACCEPTED"
    invitation.accepted_user_id = user.id
    invitation.accepted_at = datetime.utcnow()
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=invitation.tenant_id,
        entity_type="client_invitation",
        entity_id=invitation.id,
        action="access.invitation_accepted",
    )
    db.commit()
    return {"tenantId": str(invitation.tenant_id), "role": invitation.role.value}


@router.delete("/{tenant_id}/members/{membership_id}", status_code=204)
def revoke_member(
    tenant_id: UUID,
    membership_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
):
    membership = db.scalar(
        select(TenantMembership).where(
            TenantMembership.id == membership_id,
            TenantMembership.tenant_id == tenant_id,
        )
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found.")
    membership.is_active = False
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="tenant_membership",
        entity_id=membership.id,
        action="access.membership_revoked",
    )
    db.commit()


@router.post("/{tenant_id}/credentials")
def save_credential(
    tenant_id: UUID,
    payload: CredentialCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    cipher = SecretCipher()
    credential = db.scalar(
        select(ApiCredential).where(
            ApiCredential.tenant_id == tenant_id,
            ApiCredential.provider == payload.provider,
        )
    )
    if not credential:
        credential = ApiCredential(
            tenant_id=tenant_id,
            provider=payload.provider,
            encrypted_secret="",
            secret_last_four="",
        )
        db.add(credential)
    credential.encrypted_secret = cipher.encrypt(payload.secret)
    credential.secret_last_four = payload.secret[-4:]
    credential.status = "ACTIVE"
    credential.last_verified_at = None
    db.flush()
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="api_credential",
        entity_id=credential.id,
        action="access.credential_saved",
        payload={"provider": payload.provider},
    )
    db.commit()
    return {
        "id": str(credential.id),
        "provider": credential.provider,
        "masked": mask_secret(payload.secret),
        "status": credential.status,
    }


@router.post("/{tenant_id}/credentials/{credential_id}/test")
def test_credential(
    tenant_id: UUID,
    credential_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    credential = db.scalar(
        select(ApiCredential).where(
            ApiCredential.id == credential_id,
            ApiCredential.tenant_id == tenant_id,
        )
    )
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found.")
    secret = SecretCipher().decrypt(credential.encrypted_secret)
    try:
        if credential.provider == "openai":
            response = httpx.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {secret}"},
                timeout=12,
            )
        elif credential.provider == "anthropic":
            response = httpx.get(
                "https://api.anthropic.com/v1/models",
                headers={"x-api-key": secret, "anthropic-version": "2023-06-01"},
                timeout=12,
            )
        else:
            response = httpx.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={secret}",
                timeout=12,
            )
        response.raise_for_status()
        credential.status = "VERIFIED"
        credential.last_verified_at = datetime.utcnow()
        db.commit()
        return {"verified": True, "provider": credential.provider}
    except Exception as exc:
        credential.status = "INVALID"
        db.commit()
        raise HTTPException(status_code=422, detail="Provider rejected this credential.") from exc


@router.delete("/{tenant_id}/credentials/{credential_id}", status_code=204)
def delete_credential(
    tenant_id: UUID,
    credential_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_access),
):
    credential = db.scalar(
        select(ApiCredential).where(
            ApiCredential.id == credential_id,
            ApiCredential.tenant_id == tenant_id,
        )
    )
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found.")
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="api_credential",
        entity_id=credential.id,
        action="access.credential_deleted",
        payload={"provider": credential.provider},
    )
    db.delete(credential)
    db.commit()
