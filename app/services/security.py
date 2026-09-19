from redis.asyncio import Redis

from app.exceptions import AccessDenied


def ensure_admin(telegram_id: int, admin_ids: frozenset[int]) -> None:
    if telegram_id not in admin_ids:
        raise AccessDenied("Административный раздел недоступен")


class RateLimiter:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def allow(self, scope: str, user_id: int, limit: int, period: int) -> bool:
        key = f"rate:{scope}:{user_id}"
        value = await self.redis.incr(key)
        if value == 1:
            await self.redis.expire(key, period)
        return value <= limit

    async def acquire_lock(self, action: str, user_id: int, ttl: int = 30) -> bool:
        return bool(await self.redis.set(f"lock:{action}:{user_id}", "1", ex=ttl, nx=True))

