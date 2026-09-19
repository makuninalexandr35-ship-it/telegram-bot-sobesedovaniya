from pydantic import BaseModel, Field, model_validator


class CriterionScore(BaseModel):
    score: float = Field(ge=0, le=10)
    reason: str = Field(min_length=1, max_length=500)


class AnswerCriteria(BaseModel):
    relevance: CriterionScore
    specificity: CriterionScore
    structure: CriterionScore
    persuasiveness: CriterionScore
    professionalism: CriterionScore
    depth: CriterionScore
    vacancy_fit: CriterionScore
    wording_confidence: CriterionScore


class AnswerEvaluation(BaseModel):
    criteria: AnswerCriteria
    strengths: list[str]
    mistakes: list[str]
    improvements: list[str]
    additions: list[str]
    improved_answer: str
    professional_answer: str
    needs_follow_up: bool = False
    follow_up_question: str | None = None
    contradictions: list[str] = Field(default_factory=list)
    new_weaknesses: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_follow_up(self) -> "AnswerEvaluation":
        if self.needs_follow_up and not self.follow_up_question:
            raise ValueError("Для уточнения нужен текст вопроса")
        return self


class GeneratedQuestion(BaseModel):
    text: str = Field(min_length=5)
    category: str
    difficulty: str
    is_follow_up: bool = False
    topics: list[str] = Field(default_factory=list)


class VacancyAnalysis(BaseModel):
    title: str | None = None
    inferred_level: str | None = None
    explicit_requirements: list[str]
    reasoned_assumptions: list[str]
    responsibilities: list[str]
    hard_skills: list[str]
    soft_skills: list[str]
    tools: list[str]
    likely_topics: list[str]
    difficult_areas: list[str]
    resume_matches: list[str] = Field(default_factory=list)
    resume_gaps: list[str] = Field(default_factory=list)


class ResumeAnalysis(BaseModel):
    skills: list[str]
    achievements: list[str]
    experience_summary: str
    facts: list[str]
    unverified_inferences: list[str] = Field(default_factory=list)


class WeaknessAnalysis(BaseModel):
    weaknesses: list[str]
    recurring: list[str]
    recommended_topics: list[str]


class InterviewSummary(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    hardest_questions: list[str]
    training_topics: list[str]
    recommendations: list[str]
    summary: str

