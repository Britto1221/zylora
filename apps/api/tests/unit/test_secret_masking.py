from app.core.encryption import mask_secret


def test_secret_is_masked() -> None:
    assert mask_secret("sk-example-secret-1234") == "••••••••1234"
