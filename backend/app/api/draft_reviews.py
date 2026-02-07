"""
企画ドラフトレビューAPIエンドポイント
タスク4.1: 企画ドラフトレビューAPIエンドポイントの実装

Design.mdに基づく仕様:
- POST /api/draft-reviews: 企画ドラフト情報を受け取り、類似ケース・問い・懸念点を返却
- PUT /api/draft-reviews/{id}/progress: 回答進捗を更新し、未検討項目を返却
- GET /api/draft-reviews/{id}/progress: レビュー進捗を取得
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.application.draft_review_service import (
    DraftReviewService,
    DraftReviewRequest,
    AnswerProgressUpdate,
)

router = APIRouter(prefix="/draft-reviews", tags=["Draft Reviews"])


# リクエスト/レスポンススキーマ
class CreateDraftReviewRequest(BaseModel):
    """ドラフトレビュー作成リクエスト"""
    draft_id: str = Field(..., description="ドラフトID")
    purpose: str = Field(..., description="企画の目的")
    target_market: str = Field(..., description="ターゲット市場")
    business_model: str = Field(..., description="ビジネスモデル")
    additional_context: str | None = Field(None, description="追加コンテキスト")


class SimilarCaseResponse(BaseModel):
    """類似ケースレスポンス"""
    case_id: str
    title: str
    purpose: str
    outcome: str
    score: float
    matched_segments: list[str]

    model_config = {"from_attributes": True}


class ConcernPointResponse(BaseModel):
    """懸念点レスポンス"""
    category: str
    summary: str
    frequency: int
    related_case_ids: list[str]


class QuestionResponse(BaseModel):
    """問いレスポンス"""
    id: str
    question: str
    rationale: str
    related_case_ids: list[str]
    related_patterns: list[str]
    category: str


class ReviewProgressResponse(BaseModel):
    """レビュー進捗レスポンス"""
    total_questions: int
    answered_questions: int
    unanswered_question_ids: list[str]


class DraftReviewResponseSchema(BaseModel):
    """ドラフトレビューレスポンス"""
    similar_cases: list[SimilarCaseResponse]
    concern_points: list[ConcernPointResponse]
    questions: list[QuestionResponse]
    review_progress: ReviewProgressResponse


class UpdateProgressRequest(BaseModel):
    """進捗更新リクエスト"""
    question_id: str = Field(..., description="質問ID")
    answer: str = Field(..., description="回答内容")


# サービスインスタンス（本番ではDI使用）
_service: DraftReviewService | None = None


def get_service() -> DraftReviewService:
    """サービスインスタンスを取得"""
    global _service
    if _service is None:
        _service = DraftReviewService()
    return _service


@router.post("", response_model=DraftReviewResponseSchema, status_code=status.HTTP_200_OK)
async def create_draft_review(request: CreateDraftReviewRequest):
    """
    企画ドラフトをレビュー

    企画ドラフト情報を受け取り、類似ケース・問い・懸念点を返却する
    """
    try:
        service = get_service()

        domain_request = DraftReviewRequest(
            draft_id=request.draft_id,
            purpose=request.purpose,
            target_market=request.target_market,
            business_model=request.business_model,
            additional_context=request.additional_context,
        )

        result = await service.review_draft(domain_request)

        return DraftReviewResponseSchema(
            similar_cases=[
                SimilarCaseResponse(
                    case_id=c.case_id,
                    title=c.title,
                    purpose=c.purpose,
                    outcome=c.outcome.value,
                    score=c.score,
                    matched_segments=c.matched_segments,
                )
                for c in result.similar_cases
            ],
            concern_points=[
                ConcernPointResponse(
                    category=cp.category,
                    summary=cp.summary,
                    frequency=cp.frequency,
                    related_case_ids=cp.related_case_ids,
                )
                for cp in result.concern_points
            ],
            questions=[
                QuestionResponse(
                    id=q.id,
                    question=q.question,
                    rationale=q.rationale,
                    related_case_ids=q.related_case_ids,
                    related_patterns=q.related_patterns,
                    category=q.category.value,
                )
                for q in result.questions
            ],
            review_progress=ReviewProgressResponse(
                total_questions=result.review_progress.total_questions,
                answered_questions=result.review_progress.answered_questions,
                unanswered_question_ids=result.review_progress.unanswered_question_ids,
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put("/{draft_id}/progress", response_model=ReviewProgressResponse)
async def update_progress(draft_id: str, request: UpdateProgressRequest):
    """
    回答進捗を更新

    Args:
        draft_id: ドラフトID
        request: 進捗更新リクエスト

    Returns:
        更新後の進捗情報
    """
    try:
        service = get_service()

        update = AnswerProgressUpdate(
            draft_id=draft_id,
            question_id=request.question_id,
            answer=request.answer,
        )

        progress = await service.update_answer_progress(update)

        return ReviewProgressResponse(
            total_questions=progress.total_questions,
            answered_questions=progress.answered_questions,
            unanswered_question_ids=progress.unanswered_question_ids,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/{draft_id}/progress", response_model=ReviewProgressResponse)
async def get_progress(draft_id: str):
    """
    レビュー進捗を取得

    Args:
        draft_id: ドラフトID

    Returns:
        現在の進捗情報
    """
    try:
        service = get_service()
        progress = await service.get_review_progress(draft_id)

        return ReviewProgressResponse(
            total_questions=progress.total_questions,
            answered_questions=progress.answered_questions,
            unanswered_question_ids=progress.unanswered_question_ids,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
