from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from app.exceptions import AccessDenied
from app.services.subscription import SubscriptionService


def test_free_and_premium_access() -> None:
    service = SubscriptionService(free_limit=3)
    service.ensure_access("hr", None, 2)
    with pytest.raises(AccessDenied): service.ensure_access("stress", None)
    premium = SimpleNamespace(plan="premium", status="active", expires_at=datetime.now(UTC) + timedelta(days=1))
    service.ensure_access("stress", premium)

