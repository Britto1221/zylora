from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from zylora_ai.seo import audit_snapshot

from app.core.security import AuthenticatedUser, require_tenant_access, require_tenant_admin
from app.core.serialization import model_dict
from app.db.models.entities import SeoAudit, Site, SiteVersion
from app.db.models.enums import SeoAuditStatus
from app.db.session import get_db
from app.modules.audit.service import record_audit

router = APIRouter(prefix="/seo", tags=["seo"])


@router.get("/{tenant_id}")
def list_audits(
    tenant_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
) -> dict:
    items = db.scalars(
        select(SeoAudit).where(SeoAudit.tenant_id == tenant_id).order_by(SeoAudit.created_at.desc())
    ).all()
    return {"items": [model_dict(item) for item in items]}


@router.post("/{tenant_id}/run")
def run_audit(
    tenant_id: UUID,
    version_id: UUID | None = None,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    site = db.scalar(select(Site).where(Site.tenant_id == tenant_id))
    if not site:
        raise HTTPException(status_code=404, detail="Website not found.")
    target_id = version_id or site.draft_version_id or site.published_version_id
    version = db.get(SiteVersion, target_id) if target_id else None
    if not version:
        raise HTTPException(status_code=404, detail="No website version is available.")

    audit = SeoAudit(
        tenant_id=tenant_id,
        site_id=site.id,
        version_id=version.id,
        status=SeoAuditStatus.RUNNING,
    )
    db.add(audit)
    db.flush()
    try:
        result = audit_snapshot(version.content_snapshot, version.seo_snapshot)
        audit.score = result["score"]
        audit.grade = result["grade"]
        audit.summary = result["summary"]
        audit.issues_json = result["issues"]
        audit.recommendations_json = result["recommendations"]
        audit.status = SeoAuditStatus.COMPLETED
    except Exception as exc:
        audit.status = SeoAuditStatus.FAILED
        audit.error_message = str(exc)
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="seo_audit",
        entity_id=audit.id,
        action="seo.audit_completed",
        payload={"status": audit.status.value, "score": audit.score},
    )
    db.commit()
    return model_dict(audit)


@router.post("/{tenant_id}/apply/{audit_id}")
def apply_recommendation(
    tenant_id: UUID,
    audit_id: UUID,
    recommendation_code: str,
    db: Session = Depends(get_db),
    user: AuthenticatedUser = Depends(require_tenant_admin),
) -> dict:
    audit = db.scalar(
        select(SeoAudit).where(SeoAudit.id == audit_id, SeoAudit.tenant_id == tenant_id)
    )
    if not audit:
        raise HTTPException(status_code=404, detail="SEO audit not found.")
    site = db.get(Site, audit.site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found.")
    draft = db.get(SiteVersion, site.draft_version_id) if site.draft_version_id else None
    if not draft:
        raise HTTPException(status_code=409, detail="Create an editable draft first.")

    applied = False
    seo = dict(draft.seo_snapshot)
    content = dict(draft.content_snapshot)
    if recommendation_code == "missing_title":
        seo["title"] = content.get("businessName", "Business")
        applied = True
    elif recommendation_code == "missing_description":
        seo["description"] = (
            "Explore the services offered by "
            f"{content.get('businessName', 'this business')} and get in touch."
        )
        applied = True
    elif recommendation_code == "missing_conversion":
        sections = list(content.get("sections", []))
        sections.append(
            {
                "id": "contact",
                "type": "lead-form",
                "visible": True,
                "variant": "panel",
                "content": {
                    "heading": "Contact us",
                    "body": "Tell us what you need.",
                    "fields": ["name", "phone", "message"],
                },
            }
        )
        content["sections"] = sections
        applied = True

    if not applied:
        raise HTTPException(
            status_code=422,
            detail="This recommendation requires manual editing in the content editor.",
        )
    draft.seo_snapshot = seo
    draft.content_snapshot = content
    record_audit(
        db,
        actor_user_id=user.id,
        tenant_id=tenant_id,
        entity_type="site_version",
        entity_id=draft.id,
        action="seo.recommendation_applied_to_draft",
        payload={"audit_id": str(audit.id), "code": recommendation_code},
    )
    db.commit()
    return {"draft": model_dict(draft), "applied": recommendation_code}


@router.get("/{tenant_id}/{audit_id}/pdf")
def audit_pdf(
    tenant_id: UUID,
    audit_id: UUID,
    db: Session = Depends(get_db),
    _: AuthenticatedUser = Depends(require_tenant_access),
):
    from fastapi.responses import Response

    from app.modules.reports.pdf import simple_pdf

    audit = db.scalar(
        select(SeoAudit).where(SeoAudit.id == audit_id, SeoAudit.tenant_id == tenant_id)
    )
    if not audit:
        raise HTTPException(status_code=404, detail="SEO audit not found.")
    lines = [
        f"Score: {audit.score}/100",
        f"Grade: {audit.grade}",
        audit.summary or "",
        "",
        "Issues",
    ]
    for item in audit.issues_json:
        lines.append(f"[{item.get('severity')}] {item.get('title')}: {item.get('detail')}")
    lines.extend(["", "Recommendations"])
    for item in audit.recommendations_json:
        lines.append(f"{item.get('title')}: {item.get('recommendation')}")
    return Response(
        simple_pdf("Zylora SEO Audit", lines),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="seo-audit-{audit.id}.pdf"'},
    )
