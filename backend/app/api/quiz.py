"""理解度チェック（クイズ）API"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.application.quiz_service import (
    QuizAnswerResult,
    QuizGenerateRequest,
    QuizQuestionSummary,
    QuizService,
    SkillScoreSummary,
)
from app.auth.dependencies import CurrentUser, get_current_user_dependency

router = APIRouter(prefix="/quiz", tags=["Quiz"])

_service: QuizService | None = None


def get_service() -> QuizService:
    global _service
    if _service is None:
        _service = QuizService()
    return _service


class GenerateQuizRequest(BaseModel):
    count: int = Field(5, ge=1, le=20)
    difficulty: str = Field("medium")
    technologies: list[str] = Field(default_factory=list)


class QuizQuestionResponse(BaseModel):
    id: str
    technology: str
    question: str
    options: list[str]
    difficulty: str
    devlog_entry_id: str | None


class GenerateQuizResponse(BaseModel):
    questions: list[QuizQuestionResponse]
    total_generated: int


class QuizAnswerRequest(BaseModel):
    selected_answer: int = Field(..., ge=0, le=3)
    time_spent_seconds: int | None = Field(None, ge=0)


class ScoreUpdateResponse(BaseModel):
    technology: str
    previous_score: float
    new_score: float
    total_questions: int
    correct_answers: int


class QuizAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: int
    explanation: str
    score_update: ScoreUpdateResponse


class SkillScoreResponse(BaseModel):
    technology: str
    score: float
    total_questions: int
    correct_answers: int
    last_assessed_at: str | None


class SkillScoreListResponse(BaseModel):
    scores: list[SkillScoreResponse]


@router.post("/{project_id}/generate", response_model=GenerateQuizResponse)
async def generate_quiz(
    project_id: str,
    request: GenerateQuizRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    try:
        service = get_service()
        questions = await service.generate_quiz(
            current_user.user_id,
            project_id,
            QuizGenerateRequest(
                count=request.count,
                difficulty=request.difficulty,
                technologies=request.technologies,
            ),
        )
        return GenerateQuizResponse(
            questions=[_to_question_response(q) for q in questions],
            total_generated=len(questions),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{question_id}/answer", response_model=QuizAnswerResponse)
async def answer_quiz(
    question_id: str,
    request: QuizAnswerRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    try:
        service = get_service()
        result = service.answer_question(
            current_user.user_id,
            question_id,
            request.selected_answer,
            request.time_spent_seconds,
        )
        return _to_answer_response(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/scores", response_model=SkillScoreListResponse)
async def get_skill_scores(
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    service = get_service()
    scores = service.get_skill_scores(current_user.user_id)
    return SkillScoreListResponse(scores=[_to_score_response(s) for s in scores])


@router.get("/{project_id}", response_model=GenerateQuizResponse)
async def get_quiz_questions(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    service = get_service()
    questions = service.get_questions(current_user.user_id, project_id)
    return GenerateQuizResponse(
        questions=[_to_question_response(q) for q in questions],
        total_generated=len(questions),
    )


def _to_question_response(question: QuizQuestionSummary) -> QuizQuestionResponse:
    return QuizQuestionResponse(
        id=question.id,
        technology=question.technology,
        question=question.question,
        options=question.options,
        difficulty=question.difficulty,
        devlog_entry_id=question.devlog_entry_id,
    )


def _to_answer_response(result: QuizAnswerResult) -> QuizAnswerResponse:
    return QuizAnswerResponse(
        is_correct=result.is_correct,
        correct_answer=result.correct_answer,
        explanation=result.explanation,
        score_update=ScoreUpdateResponse(
            technology=result.score_update.technology,
            previous_score=result.score_update.previous_score,
            new_score=result.score_update.new_score,
            total_questions=result.score_update.total_questions,
            correct_answers=result.score_update.correct_answers,
        ),
    )


def _to_score_response(score: SkillScoreSummary) -> SkillScoreResponse:
    return SkillScoreResponse(
        technology=score.technology,
        score=score.score,
        total_questions=score.total_questions,
        correct_answers=score.correct_answers,
        last_assessed_at=score.last_assessed_at,
    )
