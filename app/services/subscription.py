from datetime import UTC, datetime

from app.database.models import Subscription
from app.exceptions import AccessDenied

PREMIUM_FEATURES = {"vacancy", "resume", "professional", "stress", "expert", "mistakes"}


class SubscriptionService:
    def __init__(self, free_limit: int = 3) -> None:
        self.free_limit = free_limit

    def is_premium(self, subscription: Subscription | None) -> bool:
        return bool(subscription and subscription.plan == "premium" and subscription.status == "active" and (subscription.expires_at is None or subscription.expires_at > datetime.now(UTC)))

    def ensure_access(self, feature: str, subscription: Subscription | None, monthly_count: int = 0) -> None:
        if self.is_premium(subscription):
            return
        if feature in PREMIUM_FEATURES or monthly_count >= self.free_limit:
            raise AccessDenied("Эта возможность доступна в Премиум. Оплата появится в следующей версии.")

