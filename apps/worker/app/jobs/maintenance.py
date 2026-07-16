from app.api import internal_request
from app.main import app


@app.task(name="zylora.cleanup_credit_reservations")
def cleanup_credit_reservations() -> dict:
    return internal_request("POST", "/credit-reservations/cleanup")
