from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.security import create_development_token


def test_user_without_membership_cannot_access_another_tenant(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    created = client.post(
        "/api/v1/tenants",
        headers=admin_headers,
        json={"name": "Private Tenant", "industry": "general", "template_key": "general"},
    )
    tenant_id = created.json()["tenant"]["id"]
    outsider = create_development_token("outsider@example.com")
    response = client.get(
        f"/api/v1/tenants/{tenant_id}",
        headers={"Authorization": f"Bearer {outsider}"},
    )
    assert response.status_code == 403
