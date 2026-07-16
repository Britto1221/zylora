from fastapi.testclient import TestClient


def test_invalid_token_is_rejected(client: TestClient) -> None:
    response = client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": "Bearer invalid"},
    )
    assert response.status_code == 401
