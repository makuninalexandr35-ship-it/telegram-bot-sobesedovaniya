from app.services.ai.schemas import AnswerCriteria

WEIGHTS = {
    "relevance": 0.15, "specificity": 0.15, "structure": 0.10,
    "persuasiveness": 0.10, "professionalism": 0.10, "depth": 0.15,
    "vacancy_fit": 0.15, "wording_confidence": 0.10,
}


def weighted_answer_score(criteria: AnswerCriteria) -> float:
    """Возвращает детерминированную оценку 0–100."""
    values = criteria.model_dump()
    result = sum(values[name]["score"] * weight for name, weight in WEIGHTS.items()) * 10
    return round(result, 1)


def interview_score(scores: list[float]) -> float:
    if not scores:
        return 0.0
    if any(score < 0 or score > 100 for score in scores):
        raise ValueError("Оценка должна быть в диапазоне 0–100")
    return round(sum(scores) / len(scores), 1)

