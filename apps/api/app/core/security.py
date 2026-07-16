from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status


class Role(StrEnum):
    SUPER_ADMIN = "SUPER_ADMIN"
    CLIENT_ADMIN = "CLIENT_ADMIN"
    CLIENT_VIEWER = "CLIENT_VIEWER"


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID
    role: Role
    tenant_id: UUID | None


def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None),
) -> AuthenticatedUser:
    """
    Development-only auth adapter.

    Replace this header-based implementation with Supabase Auth, Clerk,
    Auth.js, or another verified identity provider before production.
    """
    if not x_user_id or not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authenticated user headers.",
        )

    try:
        role = Role(x_user_role)
        user_id = UUID(x_user_id)
        tenant_id = UUID(x_tenant_id) if x_tenant_id else None
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication headers.",
        ) from exc

    return AuthenticatedUser(id=user_id, role=role, tenant_id=tenant_id)


def require_super_admin(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    if user.role is not Role.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super-admin access required.",
        )
    return user


def require_tenant_access(
    tenant_id: UUID,
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    if user.role is Role.SUPER_ADMIN:
        return user
    if user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-tenant access denied.",
        )
    return user
