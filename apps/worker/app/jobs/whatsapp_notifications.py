from app.main import app


@app.task(
    name="zylora.send_whatsapp_notification",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=5,
)
def send_whatsapp_notification(notification_job_id: str) -> dict:
    """
    Production implementation must:
    1. Load the job and tenant.
    2. Re-check status and idempotency.
    3. Verify sufficient USD credits.
    4. Deduct or reserve the configured charge atomically.
    5. Submit the approved WhatsApp template.
    6. Save the provider message ID.
    7. Finalize delivery/refund from webhook status.

    It must never raise an error back to the public lead form.
    """
    return {"notification_job_id": notification_job_id, "queued": True}
