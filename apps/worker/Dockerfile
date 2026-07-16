FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd --create-home --uid 10001 zylora
WORKDIR /app

COPY packages/zylora-ai /tmp/zylora-ai
COPY apps/worker /app

RUN python -m pip install --upgrade pip && \
    python -m pip install /tmp/zylora-ai && \
    python -m pip install .

USER zylora

CMD ["celery", "-A", "app.main:app", "worker", "--loglevel=INFO", "--concurrency=2"]
