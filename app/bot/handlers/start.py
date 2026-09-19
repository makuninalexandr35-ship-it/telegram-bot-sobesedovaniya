import re

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards import LEVELS, MAIN_MENU, RESUME, VACANCY
from app.bot.states import Onboarding
from app.repositories.users import UserRepository
from app.config import Settings
from app.exceptions import UnsupportedDocument
from app.services.resume import extract_resume

router = Router(name="start")


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    user, _ = await UserRepository(session).get_or_create(
        message.from_user.id, message.from_user.username, message.from_user.first_name
    )
    if user.profile:
        await message.answer("С возвращением!", reply_markup=MAIN_MENU)
        return
    await state.update_data(user_id=user.id)
    await state.set_state(Onboarding.profession)
    await message.answer("👋 Добро пожаловать в ИИ-тренажёр собеседований!\n\nШаг 1/6. На какую профессию или специальность вы претендуете?")


@router.message(Command("menu"))
async def menu(message: Message, state: FSMContext) -> None:
    await state.clear(); await message.answer("Главное меню", reply_markup=MAIN_MENU)


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer("Я провожу пошаговые тренировочные интервью. Используйте /interview для старта, /menu для меню и /cancel для отмены.")


@router.message(Command("cancel"))
@router.callback_query(F.data == "cancel")
async def cancel(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    target = event.message if isinstance(event, CallbackQuery) else event
    await target.answer("Сценарий отменён.", reply_markup=MAIN_MENU)
    if isinstance(event, CallbackQuery): await event.answer()


@router.message(Onboarding.profession)
async def profession(message: Message, state: FSMContext) -> None:
    if not message.text or not 2 <= len(message.text.strip()) <= 255:
        await message.answer("Введите профессию текстом (от 2 до 255 символов)."); return
    await state.update_data(profession=message.text.strip()); await state.set_state(Onboarding.level)
    await message.answer("Шаг 2/6. Выберите уровень.", reply_markup=LEVELS)


@router.callback_query(Onboarding.level, F.data.startswith("level:"))
async def level(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(level=query.data.split(":", 1)[1]); await state.set_state(Onboarding.experience)
    await query.message.answer("Шаг 3/6. Укажите опыт: например, «2 года» или «6 месяцев»."); await query.answer()


@router.message(Onboarding.experience)
async def experience(message: Message, state: FSMContext) -> None:
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*(год|лет|года|месяц|месяц|месяцев|мес)", (message.text or "").casefold())
    if not match:
        await message.answer("Не удалось распознать опыт. Пример: «1,5 года» или «8 месяцев»."); return
    value = float(match.group(1).replace(",", ".")); years = value / 12 if match.group(2).startswith("мес") else value
    if years > 60: await message.answer("Проверьте значение: максимум 60 лет."); return
    await state.update_data(experience_years=years); await state.set_state(Onboarding.position)
    await message.answer("Шаг 4/6. На какую конкретную должность вы готовитесь?")


@router.message(Onboarding.position)
async def position(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 2: await message.answer("Введите название должности."); return
    await state.update_data(target_position=message.text.strip()); await state.set_state(Onboarding.vacancy_choice)
    await message.answer("Шаг 5/6. Есть описание конкретной вакансии?", reply_markup=VACANCY)


@router.callback_query(Onboarding.vacancy_choice, F.data.startswith("vacancy:"))
async def vacancy_choice(query: CallbackQuery, state: FSMContext) -> None:
    if query.data == "vacancy:paste":
        await state.set_state(Onboarding.vacancy); await query.message.answer("Вставьте текст вакансии одним сообщением.")
    else:
        await state.set_state(Onboarding.resume_choice); await query.message.answer("Шаг 6/6. Добавить резюме?", reply_markup=RESUME)
    await query.answer()


@router.message(Onboarding.vacancy)
async def vacancy_text(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text) < 20: await message.answer("Текст слишком короткий."); return
    await state.update_data(vacancy=message.text[:20000]); await state.set_state(Onboarding.resume_choice)
    await message.answer("Шаг 6/6. Добавить резюме?", reply_markup=RESUME)


@router.callback_query(Onboarding.resume_choice, F.data.startswith("resume:"))
async def resume_choice(query: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    action = query.data.split(":")[1]
    if action == "skip":
        data = await state.get_data()
        await UserRepository(session).save_profile(
            data["user_id"], profession=data["profession"], specialization=None,
            experience_level=data["level"], experience_years=data["experience_years"],
            target_position=data["target_position"], interview_language="ru",
            resume_text=None, vacancy_text=data.get("vacancy"),
        )
        await state.clear(); await query.message.answer("Настройка завершена. Данные можно изменить в настройках.", reply_markup=MAIN_MENU)
    else:
        await state.update_data(resume_mode=action); await state.set_state(Onboarding.resume)
        await query.message.answer("Вставьте текст резюме." if action == "paste" else "Загрузите файл TXT, PDF или DOCX (до 5 МБ).")
    await query.answer()


async def finish_onboarding(
    message: Message, state: FSMContext, session: AsyncSession, resume_text: str
) -> None:
    data = await state.get_data()
    await UserRepository(session).save_profile(
        data["user_id"], profession=data["profession"], specialization=None,
        experience_level=data["level"], experience_years=data["experience_years"],
        target_position=data["target_position"], interview_language="ru",
        resume_text=resume_text, vacancy_text=data.get("vacancy"),
    )
    await state.clear()
    await message.answer(
        "Данные сохранены. Анализ будет выполнен при подготовке интервью.", reply_markup=MAIN_MENU
    )


@router.message(Onboarding.resume)
async def resume_input(
    message: Message, state: FSMContext, session: AsyncSession, settings: Settings
) -> None:
    data = await state.get_data()
    if data.get("resume_mode") == "paste":
        if not message.text or len(message.text.strip()) < 20:
            await message.answer("Резюме слишком короткое. Вставьте содержательный текст.")
            return
        await finish_onboarding(message, state, session, message.text[: settings.max_resume_chars])
        return
    if not message.document or not message.document.file_name:
        await message.answer("Отправьте документ TXT, PDF или DOCX.")
        return
    if message.document.file_size and message.document.file_size > settings.max_upload_bytes:
        await message.answer("Файл превышает допустимый размер.")
        return
    buffer = await message.bot.download(message.document)
    try:
        text = extract_resume(
            message.document.file_name, buffer.read(), settings.max_upload_bytes,
            settings.max_resume_chars,
        )
    except UnsupportedDocument as error:
        await message.answer(str(error))
        return
    await finish_onboarding(message, state, session, text)
