from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import MAIN_MENU, keyboard
from app.bot.states import DeleteData
from app.repositories.users import UserRepository

router = Router(name="common")


@router.message(Command("delete_data"))
@router.callback_query(F.data == "settings:delete")
async def request_delete(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.set_state(DeleteData.confirm)
    target = event.message if isinstance(event, CallbackQuery) else event
    await target.answer(
        "⚠️ Удалить профиль, интервью и результаты без возможности восстановления?",
        reply_markup=keyboard([[('Да, удалить', 'delete:confirm')], [('Отмена', 'cancel')]]),
    )
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(DeleteData.confirm, F.data == "delete:confirm")
async def confirm_delete(
    query: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    deleted = await UserRepository(session).delete_by_telegram_id(query.from_user.id)
    await state.clear()
    text = "Ваши данные удалены." if deleted else "Сохранённые данные не найдены."
    await query.message.answer(text)
    await query.answer()


@router.message(Command("profile"))
async def profile(message: Message) -> None:
    await message.answer("👤 Профиль хранит профессию, уровень, опыт, цель и язык. Изменение доступно через /settings.")


@router.message(Command("progress"))
@router.callback_query(F.data.in_({"menu:progress", "menu:results"}))
async def progress(event: Message | CallbackQuery) -> None:
    target = event.message if isinstance(event, CallbackQuery) else event
    await target.answer("📈 Здесь появится динамика после завершения первого интервью.", reply_markup=MAIN_MENU)
    if isinstance(event, CallbackQuery): await event.answer()


@router.message(Command("settings"))
@router.callback_query(F.data == "menu:settings")
async def settings(event: Message | CallbackQuery) -> None:
    target = event.message if isinstance(event, CallbackQuery) else event
    await target.answer("⚙️ Настройки", reply_markup=keyboard([[('Изменить профиль', 'settings:profile')], [('Удалить мои данные', 'settings:delete')], [('🏠 В меню', 'menu:home')]]))
    if isinstance(event, CallbackQuery): await event.answer()


@router.callback_query(F.data == "menu:premium")
async def premium(query: CallbackQuery) -> None:
    await query.message.answer("💎 Премиум откроет расширенные режимы и аналитику. Реальная оплата не подключена и запланирована для следующей версии.", reply_markup=MAIN_MENU); await query.answer()


@router.callback_query(F.data == "menu:faq")
async def faq(query: CallbackQuery) -> None:
    await query.message.answer("🧠 Частые темы: рассказ о себе, достижения, ошибки, конфликты и мотивация. Выберите «Тренировка ответов» в новом интервью.", reply_markup=MAIN_MENU); await query.answer()


@router.callback_query(F.data == "menu:home")
async def home(query: CallbackQuery) -> None:
    await query.message.edit_text("Главное меню", reply_markup=MAIN_MENU); await query.answer()


@router.callback_query(F.data.startswith("menu:"))
async def placeholder(query: CallbackQuery) -> None:
    await query.answer("Раздел станет доступен после накопления данных интервью.", show_alert=True)
