from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.security import AuthenticatedUser, Role, require_tenant_access


def test_cross_tenant_access_is_denied() -> None:
    user = AuthenticatedUser(
        id=uuid4(),
        role=Role.CLIENT_ADMIN,
        tenant_id=uuid4(),
    )

    with pytest.raises(HTTPException) as error:
        require_tenant_access(uuid4(), user)

    assert error.value.status_code == 403
