from aiogram.fsm.state import State, StatesGroup


class Onboarding(StatesGroup):
    profession = State(); level = State(); experience = State(); position = State(); vacancy_choice = State(); vacancy = State(); resume_choice = State(); resume = State()


class InterviewSetup(StatesGroup):
    interview_type = State(); difficulty = State(); duration = State(); language = State(); answering = State()


class DeleteData(StatesGroup):
    confirm = State()

