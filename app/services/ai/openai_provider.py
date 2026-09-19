import asyncio
import json
from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

from app.exceptions import AIUnavailable, InvalidAIResponse
from app.prompts import BASE, EVALUATION, QUESTION, RESUME, SUMMARY, VACANCY
from app.services.ai.schemas import AnswerEvaluation, GeneratedQuestion, InterviewSummary, ResumeAnalysis, VacancyAnalysis

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider:
    def __init__(self, api_key: str, model: str, timeout: float = 45, retries: int = 1) -> None:
        self.client = AsyncOpenAI(api_key=api_key, timeout=timeout)
        self.model, self.timeout, self.retries = model, timeout, retries

    async def _structured(self, instruction: str, payload: dict, schema: type[T]) -> T:
        async def request() -> T:
            response = await self.client.responses.create(
                model=self.model,
                input=[{"role": "system", "content": BASE + "\n" + instruction}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
                text={"format": {"type": "json_schema", "name": schema.__name__, "schema": schema.model_json_schema(), "strict": True}},
            )
            try:
                return schema.model_validate_json(response.output_text)
            except ValidationError as error:
                raise InvalidAIResponse("ИИ вернул некорректную структуру") from error

        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                return await asyncio.wait_for(request(), self.timeout)
            except (TimeoutError, InvalidAIResponse, ConnectionError) as error:
                last_error = error
                if attempt < self.retries:
                    await asyncio.sleep(0.25 * (attempt + 1))
        if isinstance(last_error, InvalidAIResponse):
            raise last_error
        raise AIUnavailable("Сервис ИИ временно недоступен") from last_error

    async def generate_question(self, context: dict) -> GeneratedQuestion:
        return await self._structured(QUESTION, context, GeneratedQuestion)

    async def evaluate_answer(self, context: dict) -> AnswerEvaluation:
        return await self._structured(EVALUATION, context, AnswerEvaluation)

    async def analyze_vacancy(self, text: str, resume: str | None = None) -> VacancyAnalysis:
        return await self._structured(VACANCY, {"vacancy_data": text, "resume_data": resume}, VacancyAnalysis)

    async def analyze_resume(self, text: str) -> ResumeAnalysis:
        return await self._structured(RESUME, {"resume_data": text}, ResumeAnalysis)

    async def create_summary(self, context: dict) -> InterviewSummary:
        return await self._structured(SUMMARY, context, InterviewSummary)
