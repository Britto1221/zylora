from app.main import app


@app.task(name="zylora.run_seo_audit")
def run_seo_audit(tenant_id: str, site_id: str) -> dict:
    return {
        "tenant_id": tenant_id,
        "site_id": site_id,
        "status": "queued",
    }
