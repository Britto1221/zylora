FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN useradd --create-home --uid 10001 zylora
WORKDIR /app

COPY packages/zylora-ai /tmp/zylora-ai
COPY apps/api /app

RUN python -m pip install --upgrade pip && \
    python -m pip install /tmp/zylora-ai && \
    python -m pip install .

USER zylora
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
