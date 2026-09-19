import re
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Interview, InterviewAnswer, InterviewQuestion, InterviewStatus
from app.exceptions import InterviewStateError
from app.repositories.interviews import InterviewRepository
from app.services.ai.base import AIProvider
from app.services.ai.schemas import GeneratedQuestion
from app.services.scoring import interview_score, weighted_answer_score


def normalize_question(text: str) -> str:
    return re.sub(r"[^a-zа-яё0-9]+", " ", text.casefold()).strip()


class InterviewService:
    def __init__(self, session: AsyncSession, ai: AIProvider) -> None:
        self.session, self.ai = session, ai
        self.repo = InterviewRepository(session)

    async def create(self, user_id: int, profession: str, interview_type: str, difficulty: str, language: str, planned_questions: int, vacancy: str | None = None, target_position: str | None = None) -> Interview:
        if planned_questions not in {5, 10, 20, 30}:
            raise ValueError("Недопустимое количество вопросов")
        interview = Interview(user_id=user_id, profession=profession, target_position=target_position, vacancy=vacancy, difficulty=difficulty, interview_type=interview_type, language=language, planned_questions=planned_questions, status=InterviewStatus.ACTIVE, started_at=datetime.now(UTC))
        return await self.repo.add(interview)

    async def next_question(self, interview_id: int, context: dict) -> InterviewQuestion:
        interview = await self.repo.get(interview_id)
        if not interview or interview.status is not InterviewStatus.ACTIVE:
            raise InterviewStateError("Интервью не активно")
        asked = {item.normalized_text for item in interview.questions}
        for _ in range(3):
            generated: GeneratedQuestion = await self.ai.generate_question({**context, "asked_questions": [q.text for q in interview.questions]})
            normalized = normalize_question(generated.text)
            if normalized not in asked:
                question = InterviewQuestion(interview_id=interview.id, text=generated.text, normalized_text=normalized, category=generated.category, difficulty=generated.difficulty, sequence_number=len(interview.questions) + 1, is_follow_up=generated.is_follow_up, created_at=datetime.now(UTC))
                self.session.add(question)
                await self.session.flush()
                return question
        raise InterviewStateError("Не удалось создать неповторяющийся вопрос")

    async def answer(self, interview_id: int, question_id: int, text: str, context: dict) -> InterviewAnswer:
        interview = await self.repo.get(interview_id)
        if not interview or interview.status is not InterviewStatus.ACTIVE:
            raise InterviewStateError("Нельзя отвечать в завершённом интервью")
        question = next((q for q in interview.questions if q.id == question_id), None)
        if not question or question.answer:
            raise InterviewStateError("Ответ уже сохранён или вопрос не найден")
        evaluation = await self.ai.evaluate_answer({**context, "question": question.text, "answer": text})
        score = weighted_answer_score(evaluation.criteria)
        answer = InterviewAnswer(interview_id=interview.id, question_id=question.id, answer=text, score=score, criteria=evaluation.criteria.model_dump(), feedback={"strengths": evaluation.strengths, "mistakes": evaluation.mistakes, "improvements": evaluation.improvements, "additions": evaluation.additions, "contradictions": evaluation.contradictions, "weaknesses": evaluation.new_weaknesses, "follow_up": evaluation.follow_up_question if evaluation.needs_follow_up else None}, improved_answer=evaluation.improved_answer, professional_answer=evaluation.professional_answer, created_at=datetime.now(UTC))
        self.session.add(answer)
        await self.session.flush()
        return answer

    async def complete(self, interview_id: int) -> float:
        interview = await self.repo.get(interview_id)
        if not interview or interview.status is not InterviewStatus.ACTIVE:
            raise InterviewStateError("Интервью не активно")
        scores = [q.answer.score for q in interview.questions if q.answer]
        interview.score = interview_score(scores)
        interview.status, interview.finished_at = InterviewStatus.COMPLETED, datetime.now(UTC)
        await self.session.flush()
        return interview.score
