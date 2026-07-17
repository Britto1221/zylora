import pytest

from app.modules.storage.service import (
    UploadValidationError,
    detect_mime,
    safe_filename,
    validate_content,
)


def test_active_content_and_traversal_are_rejected_or_sanitized() -> None:
    with pytest.raises(UploadValidationError):
        safe_filename("../../payload.svg")
    assert safe_filename("../../business brochure.pdf") == "business-brochure.pdf"


def test_declared_mime_must_match_bytes() -> None:
    assert detect_mime(b"%PDF-1.7 test") == "application/pdf"
    with pytest.raises(UploadValidationError):
        validate_content(data=b"%PDF-1.7 test", declared_mime_type="text/plain")
