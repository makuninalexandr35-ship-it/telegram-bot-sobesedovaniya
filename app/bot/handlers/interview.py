from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards import DIFFICULTIES, DURATIONS, INTERVIEW_TYPES, LANGUAGES, MAIN_MENU
from app.bot.states import InterviewSetup

router = Router(name="interview")


@router.message(Command("interview"))
@router.callback_query(F.data == "menu:interview")
async def interview_start(event: Message | CallbackQuery, state: FSMContext) -> None:
    await state.clear(); await state.set_state(InterviewSetup.interview_type)
    target = event.message if isinstance(event, CallbackQuery) else event
    await target.answer("Выберите тип собеседования.", reply_markup=INTERVIEW_TYPES)
    if isinstance(event, CallbackQuery): await event.answer()


@router.callback_query(InterviewSetup.interview_type, F.data.startswith("type:"))
async def choose_type(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(interview_type=query.data.split(":")[1]); await state.set_state(InterviewSetup.difficulty)
    await query.message.answer("Выберите сложность.", reply_markup=DIFFICULTIES); await query.answer()


@router.callback_query(InterviewSetup.difficulty, F.data.startswith("difficulty:"))
async def choose_difficulty(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(difficulty=query.data.split(":")[1]); await state.set_state(InterviewSetup.duration)
    await query.message.answer("Выберите количество основных вопросов.", reply_markup=DURATIONS); await query.answer()


@router.callback_query(InterviewSetup.duration, F.data.startswith("duration:"))
async def choose_duration(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(duration=int(query.data.split(":")[1])); await state.set_state(InterviewSetup.language)
    await query.message.answer("Выберите язык собеседования.", reply_markup=LANGUAGES); await query.answer()


@router.callback_query(InterviewSetup.language, F.data.startswith("language:"))
async def choose_language(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(language=query.data.split(":")[1]); data = await state.get_data()
    await state.clear()
    await query.message.answer(
        "Параметры сохранены. Для генерации интервью нужен заполненный профиль и доступный ИИ-сервис.\n"
        f"Тип: {data['interview_type']}; сложность: {data['difficulty']}; вопросов: {data['duration']}.",
        reply_markup=MAIN_MENU,
    ); await query.answer()

