from __future__ import annotations

import os
from pathlib import Path

TEST_DB = Path(__file__).parent / "test-zylora.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["ENVIRONMENT"] = "development"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["SUPER_ADMIN_EMAILS"] = "admin@zylora.dev"
os.environ["DEV_ADMIN_PASSWORD"] = "zylora-admin"

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/development-login",
        json={"email": "admin@zylora.dev", "password": "zylora-admin"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture()
def admin_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}
