from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Interview, InterviewQuestion


class InterviewRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, interview_id: int) -> Interview | None:
        return await self.session.scalar(select(Interview).where(Interview.id == interview_id).options(selectinload(Interview.questions).selectinload(InterviewQuestion.answer)))

    async def add(self, interview: Interview) -> Interview:
        self.session.add(interview)
        await self.session.flush()
        return interview

