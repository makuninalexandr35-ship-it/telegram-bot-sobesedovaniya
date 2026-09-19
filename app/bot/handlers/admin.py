from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import Settings
from app.exceptions import AccessDenied
from app.services.security import ensure_admin

router = Router(name="admin")


@router.message(Command("admin"))
async def admin(message: Message, settings: Settings) -> None:
    try:
        ensure_admin(message.from_user.id, settings.admin_telegram_ids)
    except AccessDenied:
        await message.answer("Команда недоступна."); return
    await message.answer("🛡 Администрирование\nСтатистика и рассылка доступны через сервисный слой. Для рассылки требуется отдельное подтверждение.")

