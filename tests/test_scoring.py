import pytest
from pydantic import ValidationError

from app.services.ai.schemas import AnswerCriteria, CriterionScore
from app.services.scoring import interview_score, weighted_answer_score


def criteria(score: float) -> AnswerCriteria:
    item = CriterionScore(score=score, reason="Обоснование")
    return AnswerCriteria(**{name: item for name in AnswerCriteria.model_fields})


def test_weighted_score_boundaries() -> None:
    assert weighted_answer_score(criteria(0)) == 0
    assert weighted_answer_score(criteria(10)) == 100
    assert weighted_answer_score(criteria(7)) == 70


def test_invalid_criterion() -> None:
    with pytest.raises(ValidationError):
        CriterionScore(score=11, reason="Нет")


def test_interview_average_and_invalid() -> None:
    assert interview_score([50, 80]) == 65
    with pytest.raises(ValueError):
        interview_score([101])

