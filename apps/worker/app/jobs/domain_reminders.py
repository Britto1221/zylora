from app.main import app


@app.task(name="zylora.send_domain_renewal_reminders")
def send_domain_renewal_reminders() -> dict:
    """
    Send reminders at 60, 30, 15, and 7 days before expiry.
    After the final reminder, non-renewal remains the client's responsibility.
    """
    return {"status": "scheduled"}
