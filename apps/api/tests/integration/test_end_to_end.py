from __future__ import annotations

from fastapi.testclient import TestClient


def test_admin_can_create_publish_and_capture_lead(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    created = client.post(
        "/api/v1/tenants",
        headers=admin_headers,
        json={
            "name": "Integration Academy",
            "industry": "school",
            "template_key": "school",
            "email": "client@example.com",
            "whatsapp_number": "+919999999999",
        },
    )
    assert created.status_code == 201, created.text
    payload = created.json()
    tenant_id = payload["tenant"]["id"]
    site_id = payload["site"]["id"]
    draft_id = payload["draft"]["id"]

    submit = client.post(f"/api/v1/publishing/{draft_id}/submit", headers=admin_headers)
    assert submit.status_code == 200, submit.text
    approve = client.post(f"/api/v1/publishing/{draft_id}/approve", headers=admin_headers)
    assert approve.status_code == 200, approve.text
    publish = client.post(f"/api/v1/publishing/{draft_id}/publish", headers=admin_headers)
    assert publish.status_code == 200, publish.text

    # Zero credits must not prevent lead storage.
    lead = client.post(
        "/api/v1/leads/public",
        json={
            "site_id": site_id,
            "name": "Prospective Student",
            "email": "student@example.com",
            "phone": "+919888888888",
            "message": "I need admission information.",
            "whatsapp_consent": True,
        },
    )
    assert lead.status_code == 201, lead.text
    assert lead.json()["accepted"] is True

    leads = client.get(f"/api/v1/leads/tenant/{tenant_id}", headers=admin_headers)
    assert leads.status_code == 200
    assert leads.json()["total"] == 1
