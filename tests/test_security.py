import pytest

from app.exceptions import AccessDenied
from app.services.security import ensure_admin


def test_admin_access() -> None:
    ensure_admin(10, frozenset({10}))
    with pytest.raises(AccessDenied):
        ensure_admin(11, frozenset({10}))

