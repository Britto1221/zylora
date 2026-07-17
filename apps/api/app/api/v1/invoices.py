from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import AuthenticatedUser, require_super_admin, require_tenant_access
from app.core.serialization import model_dict
from app.db.models.entities import Invoice, Tenant
from app.db.models.enums import InvoiceStatus, InvoiceType
from app.db.session import get_db
from app.modules.audit.service import record_audit
from app.modules.billing.service import clear_billing_restriction

router = APIRouter(prefix="/invoices", tags=["invoices"])


class InvoiceCreate(BaseModel):
    currency: str = Field(default="USD", min_length=3, max_length=3)
    tax_minor: int = Field(default=0, ge=0)
    due_at: datetime | None = None
    line_items: list[dict] = Field(min_length=1)


def totals(items: list[dict]) -> int:
    total = 0
    for item in items:
        quantity = int(item.get("quantity", 1))
        unit_minor = int(item.get("unitMinor", 0))
        if quantity < 1 or unit_minor < 0:
            raise HTTPException(status_code=400, detail="Invalid invoice line item.")
        total += quantity * unit_minor
    return total


@router.get("/{tenant_id}")
def list_invoices(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    items = db.scalars(
        select(Invoice).where(Invoice.tenant_id == tenant_id).order_by(Invoice.created_at.desc())
    ).all()
    return {"items": [model_dict(item) for item in items]}


@router.post("/{tenant_id}", status_code=status.HTTP_201_CREATED)
def create_invoice(
    tenant_id: UUID,
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    sequence = (db.scalar(select(func.count(Invoice.id))) or 0) + 1
    subtotal = totals(payload.line_items)
    invoice = Invoice(
        tenant_id=tenant_id,
        number=f"ZY-{datetime.utcnow().year}-{sequence:05d}",
        invoice_type=InvoiceType.ONE_TIME,
        billing_period=None,
        auto_generated=False,
        currency=payload.currency.upper(),
        subtotal_minor=subtotal,
        tax_minor=payload.tax_minor,
        total_minor=subtotal + payload.tax_minor,
        due_at=payload.due_at,
        line_items=payload.line_items,
    )
    db.add(invoice)
    db.flush()
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="invoice",
        entity_id=invoice.id,
        action="invoice.created",
        payload={"number": invoice.number},
    )
    db.commit()
    return model_dict(invoice)


@router.post("/{tenant_id}/{invoice_id}/issue")
def issue_invoice(
    tenant_id: UUID,
    invoice_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    invoice = db.scalar(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant_id)
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    if invoice.status != InvoiceStatus.DRAFT:
        raise HTTPException(status_code=409, detail="Only draft invoices can be issued.")
    invoice.status = InvoiceStatus.ISSUED
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="invoice",
        entity_id=invoice.id,
        action="invoice.issued",
    )
    db.commit()
    return model_dict(invoice)


@router.post("/{tenant_id}/{invoice_id}/mark-paid")
def mark_paid(
    tenant_id: UUID,
    invoice_id: UUID,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    invoice = db.scalar(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant_id)
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    invoice.status = InvoiceStatus.PAID
    invoice.paid_at = datetime.utcnow()
    if invoice.invoice_type == InvoiceType.RECURRING:
        tenant = db.get(Tenant, tenant_id)
        if tenant:
            clear_billing_restriction(
                db,
                tenant=tenant,
                actor_user_id=user.id,
                reason="super_admin_marked_recurring_invoice_paid",
                action="billing.lockout_cleared_by_manual_payment",
            )
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="invoice",
        entity_id=invoice.id,
        action="invoice.paid",
    )
    db.commit()
    return model_dict(invoice)


@router.get("/{tenant_id}/{invoice_id}/text")
def invoice_text(
    tenant_id: UUID,
    invoice_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
):
    from fastapi.responses import PlainTextResponse

    invoice = db.scalar(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant_id)
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    rows = [
        "ZYLORA",
        f"Invoice {invoice.number}",
        f"Status: {invoice.status.value}",
        f"Currency: {invoice.currency}",
        "",
    ]
    for item in invoice.line_items:
        rows.append(
            f"{item.get('description', 'Service')} — "
            f"{item.get('quantity', 1)} x {item.get('unitMinor', 0)} minor units"
        )
    rows.extend(
        [
            "",
            f"Subtotal: {invoice.subtotal_minor}",
            f"Tax: {invoice.tax_minor}",
            f"Total: {invoice.total_minor}",
        ]
    )
    return PlainTextResponse("\n".join(rows))


@router.get("/{tenant_id}/{invoice_id}/pdf")
def invoice_pdf(
    tenant_id: UUID,
    invoice_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
):
    from fastapi.responses import Response

    from app.modules.reports.pdf import simple_pdf

    invoice = db.scalar(
        select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant_id)
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    lines = [
        f"Status: {invoice.status.value}",
        f"Currency: {invoice.currency}",
        "",
        "Line items",
    ]
    for item in invoice.line_items:
        quantity = int(item.get("quantity", 1))
        unit = int(item.get("unitMinor", 0)) / 100
        lines.append(f"{item.get('description', 'Service')} — {quantity} x {unit:.2f}")
    lines.extend(
        [
            "",
            f"Subtotal: {invoice.subtotal_minor / 100:.2f}",
            f"Tax: {invoice.tax_minor / 100:.2f}",
            f"Total: {invoice.total_minor / 100:.2f}",
            f"Due: {invoice.due_at.isoformat() if invoice.due_at else 'On receipt'}",
        ]
    )
    return Response(
        simple_pdf(f"Zylora Invoice {invoice.number}", lines),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{invoice.number}.pdf"'},
    )
