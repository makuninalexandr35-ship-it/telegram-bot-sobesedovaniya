from aiogram import Router

from app.bot.handlers import admin, common, interview, start


def build_router() -> Router:
    router = Router()
    router.include_routers(start.router, interview.router, admin.router, common.router)
    return router

