from __future__ import annotations

from app.api import internal_request
from app.main import app


@app.task(
    name="zylora.process_notification_job",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=5,
)
def process_notification_job(notification_job_id: str) -> dict:
    return internal_request("POST", f"/notification-jobs/{notification_job_id}/process")


@app.task(name="zylora.process_pending_notifications")
def process_pending_notifications(limit: int = 50) -> dict:
    result = internal_request("GET", "/notification-jobs", params={"limit": limit})
    ids = [item["id"] for item in result.get("items", [])]
    for job_id in ids:
        process_notification_job.delay(job_id)
    return {"queued": len(ids), "ids": ids}
