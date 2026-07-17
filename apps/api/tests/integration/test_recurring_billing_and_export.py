from __future__ import annotations

import io
import zipfile
from datetime import datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.security import create_development_token
from app.db.models.entities import (
    AuditLog,
    Invoice,
    NotificationJob,
    Site,
    SiteVersion,
    Tenant,
    TenantMembership,
)
from app.db.models.enums import (
    BillingStatus,
    InvoiceStatus,
    InvoiceType,
    MembershipRole,
    SiteVersionStatus,
)
from app.db.session import SessionLocal
from app.modules.billing.service import generate_recurring_invoice
from app.modules.payments.service import (
    create_invoice_checkout_order,
    record_captured_invoice_payment,
)


def create_tenant(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/api/v1/tenants",
        headers=headers,
        json={
            "name": "Recurring Studio",
            "industry": "agency",
            "template_key": "agency",
            "email": "billing@recurring.example",
            "whatsapp_number": "+919999999998",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def add_client_membership(tenant_id: UUID, email: str) -> str:
    token = create_development_token(email)
    from app.core.security import decode_access_token

    user_id = UUID(str(decode_access_token(token)["sub"]))
    with SessionLocal() as db:
        db.add(
            TenantMembership(
                tenant_id=tenant_id,
                user_id=user_id,
                email=email,
                role=MembershipRole.CLIENT_ADMIN,
            )
        )
        db.commit()
    return token


def test_recurring_billing_dunning_lockout_and_export(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    created = create_tenant(client, admin_headers)
    tenant_id = UUID(created["tenant"]["id"])
    site_id = created["site"]["id"]

    configured = client.put(
        f"/api/v1/billing/{tenant_id}/configuration",
        headers=admin_headers,
        json={
            "monthly_amount_minor": 129900,
            "billing_currency": "INR",
            "billing_day": 7,
        },
    )
    assert configured.status_code == 200, configured.text
    assert configured.json()["billingCurrency"] == "INR"

    with SessionLocal() as db:
        tenant = db.get(Tenant, tenant_id)
        assert tenant is not None
        invoice = generate_recurring_invoice(
            db,
            tenant=tenant,
            year=2026,
            month=7,
            actor_user_id=UUID(int=1),
        )
        assert invoice is not None
        first_id = invoice.id
        duplicate = generate_recurring_invoice(
            db,
            tenant=tenant,
            year=2026,
            month=7,
            actor_user_id=UUID(int=1),
        )
        assert duplicate is not None and duplicate.id == first_id
        invoice.due_at = datetime.utcnow() - timedelta(days=11)
        invoice.status = InvoiceStatus.ISSUED
        site = db.get(Site, UUID(site_id))
        assert site is not None and site.draft_version_id is not None
        version = db.get(SiteVersion, site.draft_version_id)
        assert version is not None
        version.status = SiteVersionStatus.PUBLISHED
        version.published_at = datetime.utcnow()
        site.published_version_id = version.id
        db.commit()

    token = add_client_membership(tenant_id, "client@recurring.example")
    client_headers = {"Authorization": f"Bearer {token}"}

    status_response = client.get(
        f"/api/v1/billing/{tenant_id}/status",
        headers=client_headers,
    )
    assert status_response.status_code == 200, status_response.text
    assert status_response.json()["billingStatus"] == "restricted"
    assert status_response.json()["daysPastDue"] >= 10

    blocked = client.get(f"/api/v1/portal/{tenant_id}/summary", headers=client_headers)
    assert blocked.status_code == 402

    public_lead = client.post(
        "/api/v1/leads/public",
        json={
            "site_id": site_id,
            "name": "Public visitor",
            "email": "visitor@example.com",
            "message": "This must work while billing is restricted.",
            "whatsapp_consent": False,
            "marketing_consent": False,
            "website": "",
        },
    )
    assert public_lead.status_code == 201, public_lead.text

    clear = client.post(
        f"/api/v1/billing/{tenant_id}/clear-lockout",
        headers=admin_headers,
    )
    assert clear.status_code == 200
    assert clear.json()["billingStatus"] == "current"

    # The manual override remains effective for this overdue invoice.
    assert (
        client.get(f"/api/v1/billing/{tenant_id}/status", headers=client_headers)
        .json()["billingStatus"]
        == "current"
    )
    assert (
        client.get(f"/api/v1/portal/{tenant_id}/summary", headers=client_headers).status_code
        == 200
    )

    export = client.post(f"/api/v1/exports/{tenant_id}", headers=admin_headers)
    assert export.status_code == 200, export.text
    with zipfile.ZipFile(io.BytesIO(export.content)) as archive:
        names = set(archive.namelist())
        assert {"index.html", "styles.css", ".env.example", "README.md"}.issubset(names)
        combined = b"\n".join(archive.read(name) for name in names)
        assert b"OPENAI_API_KEY" not in combined
        assert b"DATABASE_URL" not in combined
        assert b"other tenant" not in combined.lower()
        assert b"Dynamic lead capture is not included" in combined

    with SessionLocal() as db:
        tenant = db.get(Tenant, tenant_id)
        assert tenant is not None and tenant.billing_status == BillingStatus.CURRENT
        invoice = db.scalar(
            select(Invoice).where(
                Invoice.tenant_id == tenant_id,
                Invoice.invoice_type == InvoiceType.RECURRING,
            )
        )
        assert invoice is not None and invoice.currency == "INR"
        jobs = db.scalars(
            select(NotificationJob).where(NotificationJob.tenant_id == tenant_id)
        ).all()
        billing_keys = {
            job.idempotency_key
            for job in jobs
            if job.idempotency_key.startswith("billing:")
        }
        assert any("day-3:email" in key for key in billing_keys)
        assert any("day-8:whatsapp" in key for key in billing_keys)
        actions = set(
            db.scalars(
                select(AuditLog.action).where(AuditLog.tenant_id == tenant_id)
            ).all()
        )
        assert "billing.configuration_updated" in actions
        assert "billing.lockout_manual_override" in actions
        assert "client.export_generated" in actions


def test_verified_recurring_payment_clears_restriction(
    client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    created = create_tenant(client, admin_headers)
    tenant_id = UUID(created["tenant"]["id"])
    with SessionLocal() as db:
        tenant = db.get(Tenant, tenant_id)
        assert tenant is not None
        tenant.monthly_amount_minor = 9900
        tenant.billing_currency = "USD"
        tenant.billing_day = 1
        tenant.billing_status = BillingStatus.RESTRICTED
        invoice = generate_recurring_invoice(
            db,
            tenant=tenant,
            year=2026,
            month=8,
            actor_user_id=UUID(int=1),
        )
        assert invoice is not None
        invoice.due_at = datetime.utcnow() - timedelta(days=12)
        invoice.status = InvoiceStatus.OVERDUE
        payment, order = create_invoice_checkout_order(
            db,
            tenant_id=tenant_id,
            invoice_id=invoice.id,
            receipt=f"test-{invoice.number}",
        )
        record_captured_invoice_payment(
            db,
            provider_payment_id="pay_recurring_verified",
            provider_order_id=str(order["id"]),
            charged_amount_minor=invoice.total_minor,
            charged_currency=invoice.currency,
            event_id="event_recurring_verified",
            metadata={"test": True},
            actor_user_id=UUID(int=2),
        )
        db.commit()
        db.refresh(tenant)
        db.refresh(invoice)
        db.refresh(payment)
        assert tenant.billing_status == BillingStatus.CURRENT
        assert invoice.status == InvoiceStatus.PAID
        assert payment.status == "CAPTURED"
