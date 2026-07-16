from app.api import internal_request
from app.main import app


@app.task(
    name="zylora.run_seo_audit",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def run_seo_audit(tenant_id: str) -> dict:
    return internal_request("POST", f"/seo/{tenant_id}/run")
