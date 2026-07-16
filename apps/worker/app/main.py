from celery import Celery

app = Celery(
    "zylora-worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

app.autodiscover_tasks(["app.jobs"])

if __name__ == "__main__":
    app.worker_main(["worker", "--loglevel=INFO"])
