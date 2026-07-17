from uuid import NAMESPACE_DNS, UUID, uuid5

from fastapi.testclient import TestClient

from app.core.security import create_development_token
from app.db.models.entities import TenantMembership
from app.db.models.enums import MembershipRole
from app.db.session import SessionLocal


def create_tenant(client: TestClient, headers: dict[str, str], name: str) -> dict:
    response = client.post(
        "/api/v1/tenants",
        headers=headers,
        json={"name": name, "industry": "general", "template_key": "general"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def member_headers(tenant_id: str, email: str, role: MembershipRole) -> dict[str, str]:
    with SessionLocal() as db:
        db.add(
            TenantMembership(
                tenant_id=UUID(tenant_id),
                user_id=uuid5(NAMESPACE_DNS, email),
                email=email,
                role=role,
                is_active=True,
            )
        )
        db.commit()
    return {"Authorization": f"Bearer {create_development_token(email)}"}


def test_cross_tenant_access_is_denied(client: TestClient, admin_headers: dict[str, str]) -> None:
    a = create_tenant(client, admin_headers, "Tenant Boundary A")
    b = create_tenant(client, admin_headers, "Tenant Boundary B")
    tenant_a, tenant_b = a["tenant"]["id"], b["tenant"]["id"]
    headers = member_headers(tenant_a, "tenant.admin@zylora.dev", MembershipRole.CLIENT_ADMIN)
    assert client.get(f"/api/v1/tenants/{tenant_a}", headers=headers).status_code == 200
    for path in [
        f"/tenants/{tenant_b}",
        f"/sites/tenant/{tenant_b}",
        f"/leads/tenant/{tenant_b}",
        f"/credits/{tenant_b}",
        f"/documents/{tenant_b}",
        f"/assets/{tenant_b}",
        f"/payments/{tenant_b}",
    ]:
        assert client.get(f"/api/v1{path}", headers=headers).status_code == 403


def test_viewer_cannot_mutate_or_publish(client: TestClient, admin_headers: dict[str, str]) -> None:
    created = create_tenant(client, admin_headers, "Viewer Permissions")
    tenant_id, draft_id = created["tenant"]["id"], created["draft"]["id"]
    viewer = member_headers(tenant_id, "tenant.viewer@zylora.dev", MembershipRole.CLIENT_VIEWER)
    assert client.get(f"/api/v1/tenants/{tenant_id}", headers=viewer).status_code == 200
    assert (
        client.patch(
            f"/api/v1/tenants/{tenant_id}", headers=viewer, json={"owner_name": "Blocked"}
        ).status_code
        == 403
    )
    assert (
        client.patch(
            f"/api/v1/sites/tenant/{tenant_id}/draft",
            headers=viewer,
            json={"theme": {"primaryColor": "#000"}},
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"/api/v1/documents/{tenant_id}",
            headers=viewer,
            json={"name": "Blocked", "category": "faq", "text": "Not allowed"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"/api/v1/payments/{tenant_id}/orders", headers=viewer, json={"pack_id": "mini"}
        ).status_code
        == 403
    )
    assert client.post(f"/api/v1/publishing/{draft_id}/submit", headers=viewer).status_code == 403
