from app.api import internal_request
from app.main import app


@app.task(
    name="zylora.send_domain_renewal_reminders",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def send_domain_renewal_reminders() -> dict:
    return internal_request("POST", "/domain-reminders/run")
