from __future__ import annotations

from fastapi.testclient import TestClient


def create_client(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/tenants",
        headers=headers,
        json={
            "name": "Operational Clinic",
            "industry": "clinic",
            "template_key": "clinic",
            "email": "owner@operational.example",
            "whatsapp_number": "+919999999999",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_operational_modules_are_connected(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    created = create_client(client, admin_headers)
    tenant_id = created["tenant"]["id"]
    site_id = created["site"]["id"]
    draft_id = created["draft"]["id"]

    assert client.get("/api/v1/dashboard/summary", headers=admin_headers).status_code == 200
    assert (
        client.get(f"/api/v1/portal/{tenant_id}/summary", headers=admin_headers).status_code == 200
    )

    site = client.get(f"/api/v1/sites/tenant/{tenant_id}", headers=admin_headers)
    assert site.status_code == 200
    content = site.json()["draft"]["content_snapshot"]
    content["sections"][0]["content"]["heading"] = "Trusted clinic care"
    update = client.patch(
        f"/api/v1/sites/tenant/{tenant_id}/draft",
        headers=admin_headers,
        json={"content": content},
    )
    assert update.status_code == 200
    assert update.json()["validation"]["valid"] is True

    topup = client.post(
        f"/api/v1/credits/{tenant_id}/manual-top-up",
        headers=admin_headers,
        json={
            "amount_usd": "25.00",
            "description": "Integration top-up",
            "external_reference": "integration-payment-1",
        },
    )
    assert topup.status_code == 200
    credits = client.get(f"/api/v1/credits/{tenant_id}", headers=admin_headers)
    assert credits.status_code == 200
    assert float(credits.json()["account"]["balanceUsd"]) == 25.0

    settings = client.patch(
        f"/api/v1/notifications/{tenant_id}/settings",
        headers=admin_headers,
        json={
            "business_enabled": True,
            "visitor_enabled": True,
            "business_template": "new_lead",
            "visitor_template": "lead_received",
        },
    )
    assert settings.status_code == 200

    domain = client.post(
        f"/api/v1/domains/{tenant_id}",
        headers=admin_headers,
        json={
            "hostname": "operational-clinic.example",
            "domain_type": "custom",
            "is_primary": True,
            "registered_to_client": True,
            "renewal_price_usd": "19.00",
        },
    )
    assert domain.status_code == 200, domain.text
    domain_id = domain.json()["id"]
    verify = client.post(
        f"/api/v1/domains/{tenant_id}/{domain_id}/verify?confirmed=true",
        headers=admin_headers,
    )
    assert verify.status_code == 200
    assert verify.json()["status"] == "ACTIVE"

    document = client.post(
        f"/api/v1/documents/{tenant_id}",
        headers=admin_headers,
        json={
            "name": "Clinic FAQ",
            "category": "faq",
            "text": (
                "Appointments are available Monday to Saturday. Call the clinic for "
                "current availability. The clinic provides preventive consultations "
                "and follow-up care."
            ),
        },
    )
    assert document.status_code == 201
    document_id = document.json()["id"]
    details = client.get(
        f"/api/v1/documents/{tenant_id}/{document_id}",
        headers=admin_headers,
    )
    assert details.status_code == 200
    assert details.json()["chunks"]

    enable_chat = client.patch(
        f"/api/v1/tenants/{tenant_id}/features/chatbot?enabled=true",
        headers=admin_headers,
    )
    assert enable_chat.status_code == 200

    for action in ["submit", "approve", "publish"]:
        publication = client.post(f"/api/v1/publishing/{draft_id}/{action}", headers=admin_headers)
        assert publication.status_code == 200, publication.text
    chat = client.post(
        "/api/v1/chatbot/public",
        json={
            "tenant_id": tenant_id,
            "site_id": site_id,
            "question": "When are appointments available?",
        },
    )
    assert chat.status_code == 200
    assert chat.json()["answer"]

    event = client.post(
        "/api/v1/analytics/public",
        json={
            "tenant_id": tenant_id,
            "site_id": site_id,
            "session_id": "integration-session",
            "event_type": "page_view",
            "path": "/",
            "metadata": {},
        },
    )
    assert event.status_code == 202
    analytics = client.get(f"/api/v1/analytics/{tenant_id}", headers=admin_headers)
    assert analytics.status_code == 200
    assert analytics.json()["pageViews"] >= 1

    change = client.post(
        f"/api/v1/changes/{tenant_id}",
        headers=admin_headers,
        json={
            "category": "text",
            "title": "Update clinic hours",
            "description": "Replace the footer hours with the approved schedule.",
            "priority": "NORMAL",
        },
    )
    assert change.status_code == 201
    change_id = change.json()["id"]
    update_change = client.patch(
        f"/api/v1/changes/{tenant_id}/{change_id}",
        headers=admin_headers,
        json={"status": "QUOTED", "quoted_price_minor": 2500},
    )
    assert update_change.status_code == 200

    invoice = client.post(
        f"/api/v1/invoices/{tenant_id}",
        headers=admin_headers,
        json={
            "currency": "USD",
            "tax_minor": 0,
            "line_items": [
                {"description": "Landing page development", "quantity": 1, "unitMinor": 29900}
            ],
        },
    )
    assert invoice.status_code == 201
    invoice_id = invoice.json()["id"]
    assert (
        client.post(
            f"/api/v1/invoices/{tenant_id}/{invoice_id}/issue",
            headers=admin_headers,
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/v1/invoices/{tenant_id}/{invoice_id}/mark-paid",
            headers=admin_headers,
        ).status_code
        == 200
    )
    pdf = client.get(
        f"/api/v1/invoices/{tenant_id}/{invoice_id}/pdf",
        headers=admin_headers,
    )
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"

    seo = client.post(f"/api/v1/seo/{tenant_id}/run", headers=admin_headers)
    assert seo.status_code == 200
    audit_id = seo.json()["id"]
    assert (
        client.get(
            f"/api/v1/seo/{tenant_id}/{audit_id}/pdf",
            headers=admin_headers,
        ).status_code
        == 200
    )

    invite = client.post(
        f"/api/v1/access/{tenant_id}/invitations",
        headers=admin_headers,
        json={"email": "client.user@example.com", "role": "CLIENT_ADMIN", "expires_days": 7},
    )
    assert invite.status_code == 201
    access = client.get(f"/api/v1/access/{tenant_id}/members", headers=admin_headers)
    assert access.status_code == 200
    assert len(access.json()["invitations"]) == 1

    credential = client.post(
        f"/api/v1/access/{tenant_id}/credentials",
        headers=admin_headers,
        json={"provider": "openai", "secret": "sk-development-only-not-real"},
    )
    assert credential.status_code == 200
    credential_id = credential.json()["id"]
    assert (
        client.delete(
            f"/api/v1/access/{tenant_id}/credentials/{credential_id}",
            headers=admin_headers,
        ).status_code
        == 204
    )

    presign = client.post(
        f"/api/v1/assets/{tenant_id}/presign",
        headers=admin_headers,
        json={
            "filename": "clinic.txt",
            "mime_type": "text/plain",
            "size_bytes": 14,
            "category": "document",
            "alt_text": None,
        },
    )
    assert presign.status_code == 200
    asset_id = presign.json()["asset"]["id"]
    upload = client.post(
        f"/api/v1/assets/{tenant_id}/{asset_id}/local-upload",
        headers=admin_headers,
        files={"file": ("clinic.txt", b"Clinic content", "text/plain")},
    )
    assert upload.status_code == 200
    assert (
        client.get(
            f"/api/v1/assets/{tenant_id}/{asset_id}/download",
            headers=admin_headers,
        ).status_code
        == 200
    )

    order = client.post(
        f"/api/v1/payments/{tenant_id}/orders",
        headers=admin_headers,
        json={"pack_id": "standard"},
    )
    assert order.status_code == 201, order.text
    assert order.json()["order"]["id"]
    assert order.json()["payment"]["pack_id"] == "standard"

    logs = client.get(f"/api/v1/audit/{tenant_id}", headers=admin_headers)
    assert logs.status_code == 200
    assert logs.json()["items"]


def test_notification_worker_processes_job_with_credits(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    created = create_client(client, admin_headers)
    tenant_id = created["tenant"]["id"]
    site_id = created["site"]["id"]
    draft_id = created["draft"]["id"]

    for action in ["submit", "approve", "publish"]:
        response = client.post(
            f"/api/v1/publishing/{draft_id}/{action}",
            headers=admin_headers,
        )
        assert response.status_code == 200, response.text

    client.post(
        f"/api/v1/credits/{tenant_id}/manual-top-up",
        headers=admin_headers,
        json={
            "amount_usd": "1.00",
            "description": "Worker test",
            "external_reference": "worker-test-credit",
        },
    )
    lead = client.post(
        "/api/v1/leads/public",
        json={
            "site_id": site_id,
            "name": "Notification Lead",
            "phone": "+919888888888",
            "whatsapp_consent": True,
        },
    )
    assert lead.status_code == 201

    worker_headers = {"X-Worker-Token": "zylora-worker-development-token"}
    jobs = client.get(
        "/api/v1/internal/notification-jobs",
        headers=worker_headers,
    )
    assert jobs.status_code == 200
    matching_jobs = [item for item in jobs.json()["items"] if item["tenant_id"] == tenant_id]
    assert matching_jobs
    job_id = matching_jobs[0]["id"]
    processed = client.post(
        f"/api/v1/internal/notification-jobs/{job_id}/process",
        headers=worker_headers,
    )
    assert processed.status_code == 200
    assert processed.json()["status"] == "SUBMITTED"

    cleanup = client.post(
        "/api/v1/internal/credit-reservations/cleanup",
        headers=worker_headers,
    )
    assert cleanup.status_code == 200
