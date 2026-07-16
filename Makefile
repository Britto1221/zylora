.PHONY: install dev-api dev-web dev-worker test-api migrate docker-up docker-down

install:
	python -m pip install -e ./packages/zylora-ai
	python -m pip install -e "./apps/api[dev]"
	python -m pip install -e "./apps/worker[dev]"
	npm install

docker-up:
	docker compose up -d

docker-down:
	docker compose down

migrate:
	cd apps/api && alembic upgrade head

dev-api:
	cd apps/api && uvicorn app.main:app --reload --port 8000

dev-web:
	npm run dev:web

dev-worker:
	cd apps/worker && python -m app.main

test-api:
	cd apps/api && pytest
