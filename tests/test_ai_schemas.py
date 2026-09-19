import pytest
from pydantic import ValidationError

from app.services.ai.schemas import AnswerEvaluation


def test_follow_up_requires_question() -> None:
    item = {"score": 5, "reason": "Краткое обоснование"}
    payload = {
        "criteria": {name: item for name in ("relevance", "specificity", "structure", "persuasiveness", "professionalism", "depth", "vacancy_fit", "wording_confidence")},
        "strengths": [], "mistakes": [], "improvements": [], "additions": [],
        "improved_answer": "Ответ", "professional_answer": "Ответ", "needs_follow_up": True,
    }
    with pytest.raises(ValidationError): AnswerEvaluation.model_validate(payload)

