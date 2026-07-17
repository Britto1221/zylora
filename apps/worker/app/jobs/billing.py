from __future__ import annotations

from app.api import internal_request
from app.main import app


@app.task(name="zylora.generate_monthly_recurring_invoices")
def generate_monthly_recurring_invoices() -> dict:
    return internal_request("POST", "/billing/generate-monthly")


@app.task(name="zylora.evaluate_billing_dunning")
def evaluate_billing_dunning() -> dict:
    return internal_request("POST", "/billing/evaluate-dunning")
