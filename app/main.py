import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.bot.handlers import build_router
from app.bot.middleware import DatabaseMiddleware
from app.config import get_settings
from app.database.session import create_session_factory


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    redis = Redis.from_url(settings.redis_url)
    bot = Bot(settings.bot_token.get_secret_value())
    dispatcher = Dispatcher(storage=RedisStorage(redis))
    dispatcher["settings"] = settings
    dispatcher.update.outer_middleware(DatabaseMiddleware(create_session_factory(settings.database_url)))
    dispatcher.include_router(build_router())
    try:
        await dispatcher.start_polling(bot)
    finally:
        await redis.aclose(); await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
