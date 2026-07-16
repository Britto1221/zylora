from __future__ import annotations

import sentry_sdk
from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        send_default_pii=False,
    )

app = Celery(
    "zylora-worker",
    broker=settings.redis_url,
    backend=settings.redis_url.replace("/0", "/1"),
    include=[
        "app.jobs.whatsapp_notifications",
        "app.jobs.domain_reminders",
        "app.jobs.seo_audits",
        "app.jobs.maintenance",
    ],
)
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    beat_schedule={
        "process-pending-notifications": {
            "task": "zylora.process_pending_notifications",
            "schedule": 30.0,
        },
        "release-expired-credit-reservations": {
            "task": "zylora.cleanup_credit_reservations",
            "schedule": 300.0,
        },
        "daily-domain-renewal-reminders": {
            "task": "zylora.send_domain_renewal_reminders",
            "schedule": crontab(hour=3, minute=15),
        },
    },
)

if __name__ == "__main__":
    app.worker_main(["worker", "--loglevel=INFO"])
