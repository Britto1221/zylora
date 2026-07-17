from __future__ import annotations

import io
import zipfile
from datetime import datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.security import create_development_token, decode_access_token
from app.db.models.entities import (
    AuditLog,
    Site,
    SiteVersion,
    Tenant,
    TenantMembership,
    TenantNote,
)
from app.db.models.enums import (
    BillingStatus,
    InvoiceStatus,
    MembershipRole,
    SiteVersionStatus,
    TenantStatus,
)
from app.db.session import SessionLocal
from app.modules.billing.service import generate_recurring_invoice


def create_client(client: TestClient, headers: dict[str, str], name: str, email: str) -> dict:
    response = client.post(
        "/api/v1/tenants",
        headers=headers,
        json={"name": name, "industry": "agency", "template_key": "agency", "email": email},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_super_admin_portfolio_bulk_revenue_pause_notes_and_health(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    alpha = create_client(client, admin_headers, "Portfolio Alpha", "alpha@example.com")
    beta = create_client(client, admin_headers, "Portfolio Beta", "beta@example.com")
    alpha_id = UUID(alpha["tenant"]["id"])
    beta_id = UUID(beta["tenant"]["id"])

    for tenant_id, amount, currency in ((alpha_id, 19900, "USD"), (beta_id, 249900, "INR")):
        response = client.put(
            f"/api/v1/billing/{tenant_id}/configuration",
            headers=admin_headers,
            json={"monthly_amount_minor": amount, "billing_currency": currency, "billing_day": 20},
        )
        assert response.status_code == 200, response.text

    with SessionLocal() as db:
        alpha_tenant = db.get(Tenant, alpha_id)
        beta_tenant = db.get(Tenant, beta_id)
        assert alpha_tenant and beta_tenant
        alpha_site = db.scalar(select(Site).where(Site.tenant_id == alpha_id))
        assert alpha_site and alpha_site.draft_version_id
        alpha_version = db.get(SiteVersion, alpha_site.draft_version_id)
        assert alpha_version
        alpha_version.status = SiteVersionStatus.PUBLISHED
        alpha_version.published_at = datetime.utcnow()
        alpha_site.published_version_id = alpha_version.id

        beta_invoice = generate_recurring_invoice(
            db,
            tenant=beta_tenant,
            year=2026,
            month=9,
            actor_user_id=UUID(int=1),
        )
        assert beta_invoice
        beta_invoice.due_at = datetime.utcnow() - timedelta(days=12)
        beta_invoice.status = InvoiceStatus.OVERDUE
        beta_tenant.billing_status = BillingStatus.RESTRICTED

        login_email = "alpha.user@example.com"
        token = create_development_token(login_email)
        user_id = UUID(str(decode_access_token(token)["sub"]))
        db.add(
            TenantMembership(
                tenant_id=alpha_id,
                user_id=user_id,
                email=login_email,
                role=MembershipRole.CLIENT_ADMIN,
            )
        )
        db.commit()

    login = client.post(
        "/api/v1/auth/development-login",
        json={"email": "alpha.user@example.com", "password": "zylora-admin"},
    )
    assert login.status_code == 200, login.text

    filtered = client.get(
        "/api/v1/tenants?billing_status=current&site_status=live&page_size=100",
        headers=admin_headers,
    )
    assert filtered.status_code == 200, filtered.text
    alpha_item = next(item for item in filtered.json()["items"] if item["id"] == str(alpha_id))
    assert alpha_item["site_status"] == "live"
    assert alpha_item["last_login_at"] is not None
    assert alpha_item["health_status"] == "Healthy"
    assert alpha_item["health_reasons"]

    pause = client.post(
        f"/api/v1/admin/clients/{alpha_id}/pause",
        headers=admin_headers,
        json={"paused": True, "reason": "Client requested a temporary commercial hold."},
    )
    assert pause.status_code == 200, pause.text
    assert pause.json()["operational_status"] == "paused"

    with SessionLocal() as db:
        alpha_tenant = db.get(Tenant, alpha_id)
        assert alpha_tenant and alpha_tenant.operational_status == TenantStatus.PAUSED
        skipped = generate_recurring_invoice(
            db,
            tenant=alpha_tenant,
            year=2026,
            month=10,
            actor_user_id=UUID(int=1),
        )
        assert skipped is None

    # Pausing is not a portal lockout.
    client_token = login.json()["access_token"]
    portal = client.get(
        f"/api/v1/portal/{alpha_id}/summary",
        headers={"Authorization": f"Bearer {client_token}"},
    )
    assert portal.status_code == 200, portal.text

    client_headers = {"Authorization": f"Bearer {client_token}"}
    forbidden_revenue = client.get("/api/v1/dashboard/revenue", headers=client_headers)
    assert forbidden_revenue.status_code == 403
    forbidden_bulk = client.post(
        "/api/v1/admin/clients/bulk/payment-reminders",
        headers=client_headers,
        json={"tenant_ids": [str(alpha_id)]},
    )
    assert forbidden_bulk.status_code == 403
    forbidden_notes = client.get(
        f"/api/v1/admin/clients/{alpha_id}/notes",
        headers=client_headers,
    )
    assert forbidden_notes.status_code == 403

    for text in ("First operational note.", "Second note preserves history."):
        note = client.post(
            f"/api/v1/admin/clients/{alpha_id}/notes",
            headers=admin_headers,
            json={"text": text},
        )
        assert note.status_code == 200, note.text
    notes = client.get(f"/api/v1/admin/clients/{alpha_id}/notes", headers=admin_headers)
    assert notes.status_code == 200
    assert [item["body"] for item in notes.json()["items"]][:2] == [
        "Second note preserves history.",
        "First operational note.",
    ]

    reminder = client.post(
        "/api/v1/admin/clients/bulk/payment-reminders",
        headers=admin_headers,
        json={"tenant_ids": [str(beta_id)]},
    )
    assert reminder.status_code == 200, reminder.text
    assert reminder.json()["results"][0]["queued"] >= 1

    override = client.post(
        "/api/v1/admin/clients/bulk/clear-lockouts",
        headers=admin_headers,
        json={"tenant_ids": [str(beta_id)]},
    )
    assert override.status_code == 200, override.text
    assert override.json()["results"][0]["billingStatus"] == "current"

    revenue = client.get("/api/v1/dashboard/revenue", headers=admin_headers)
    assert revenue.status_code == 200, revenue.text
    payload = revenue.json()
    # Alpha is paused and therefore excluded from current billable MRR.
    with SessionLocal() as db:
        expected_usd = sum(
            tenant.monthly_amount_minor
            for tenant in db.scalars(select(Tenant)).all()
            if tenant.is_active
            and tenant.operational_status == TenantStatus.ACTIVE
            and tenant.billing_currency == "USD"
            and tenant.monthly_amount_minor > 0
        )
        expected_inr = sum(
            tenant.monthly_amount_minor
            for tenant in db.scalars(select(Tenant)).all()
            if tenant.is_active
            and tenant.operational_status == TenantStatus.ACTIVE
            and tenant.billing_currency == "INR"
            and tenant.monthly_amount_minor > 0
        )
    assert payload["mrr"]["USD"] == expected_usd
    assert payload["mrr"]["INR"] == expected_inr
    assert set(payload["billingStatusCounts"]) == {"current", "warned", "restricted"}

    bundle = client.post(
        "/api/v1/exports/bulk",
        headers=admin_headers,
        json={"tenant_ids": [str(alpha_id), str(beta_id)]},
    )
    assert bundle.status_code == 200, bundle.text
    with zipfile.ZipFile(io.BytesIO(bundle.content)) as archive:
        assert len([name for name in archive.namelist() if name.endswith(".zip")]) == 2

    with SessionLocal() as db:
        assert db.scalar(select(TenantNote.id).where(TenantNote.tenant_id == alpha_id))
        actions = set(db.scalars(select(AuditLog.action)).all())
        assert "tenant.paused" in actions
        assert "tenant.note_added" in actions
        assert "billing.payment_reminder_manual" in actions
        assert "billing.lockout_bulk_override_requested" in actions
        assert "client.bulk_export_generated" in actions
