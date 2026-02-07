"""
アイデア壁打ちAPIエンドポイント
旧 draft_reviews.py をリネーム＋改修。

- POST /api/idea-sparring: アイデアを壁打ちし、類似ケース・問い・懸念点を返却
- PUT /api/idea-sparring/{id}/progress: 回答進捗を更新
- GET /api/idea-sparring/{id}/progress: 壁打ち進捗を取得
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.dependencies import CurrentUser, get_current_user_dependency
from app.application.idea_sparring_service import (
    IdeaSparringService,
    IdeaSparringRequest,
    AnswerProgressUpdate,
)
from app.application.usage_service import UsageService

router = APIRouter(prefix="/idea-sparring", tags=["Idea Sparring"])


# リクエスト/レスポンススキーマ
class CreateIdeaSparringRequest(BaseModel):
    """アイデア壁打ちリクエスト"""
    idea_id: str = Field(..., description="アイデアID")
    purpose: str = Field(..., description="アイデアの概要・目的")
    target_market: str = Field(..., description="ターゲットユーザー")
    business_model: str = Field(..., description="マネタイズ方法")
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


class SparringProgressResponse(BaseModel):
    """壁打ち進捗レスポンス"""
    total_questions: int
    answered_questions: int
    unanswered_question_ids: list[str]


class IdeaSparringResponseSchema(BaseModel):
    """アイデア壁打ちレスポンス"""
    similar_cases: list[SimilarCaseResponse]
    concern_points: list[ConcernPointResponse]
    questions: list[QuestionResponse]
    sparring_progress: SparringProgressResponse


class UpdateProgressRequest(BaseModel):
    """進捗更新リクエスト"""
    question_id: str = Field(..., description="質問ID")
    answer: str = Field(..., description="回答内容")


# サービスインスタンス
_service: IdeaSparringService | None = None
_usage_service: UsageService | None = None


def get_service() -> IdeaSparringService:
    """サービスインスタンスを取得"""
    global _service
    if _service is None:
        _service = IdeaSparringService()
    return _service


def get_usage_service() -> UsageService:
    """利用量管理サービスインスタンスを取得"""
    global _usage_service
    if _usage_service is None:
        _usage_service = UsageService()
    return _usage_service


@router.post("", response_model=IdeaSparringResponseSchema, status_code=status.HTTP_200_OK)
async def create_idea_sparring(
    request: CreateIdeaSparringRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """
    アイデアを壁打ち

    アイデア情報を受け取り、類似ケース・問い・懸念点を返却する。
    認証必須。ユーザーのデータのみ検索対象。
    """
    try:
        # 利用量チェック
        usage = get_usage_service()
        quota = usage.check_sparring_quota(current_user.user_id, current_user.plan)
        if quota.is_exceeded:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"壁打ち回数の上限に達しました（{quota.limit}回/日）。Proプランにアップグレードしてください。",
            )

        service = get_service()

        domain_request = IdeaSparringRequest(
            idea_id=request.idea_id,
            purpose=request.purpose,
            target_market=request.target_market,
            business_model=request.business_model,
            additional_context=request.additional_context,
            user_id=current_user.user_id,
        )

        result = await service.spar_idea(domain_request)

        # 利用を記録
        usage.record_usage(current_user.user_id, "idea_sparring")

        return IdeaSparringResponseSchema(
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
            sparring_progress=SparringProgressResponse(
                total_questions=result.sparring_progress.total_questions,
                answered_questions=result.sparring_progress.answered_questions,
                unanswered_question_ids=result.sparring_progress.unanswered_question_ids,
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put("/{idea_id}/progress", response_model=SparringProgressResponse)
async def update_progress(
    idea_id: str,
    request: UpdateProgressRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """回答進捗を更新"""
    try:
        service = get_service()

        update = AnswerProgressUpdate(
            idea_id=idea_id,
            question_id=request.question_id,
            answer=request.answer,
        )

        progress = await service.update_answer_progress(update)

        return SparringProgressResponse(
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


@router.get("/{idea_id}/progress", response_model=SparringProgressResponse)
async def get_progress(
    idea_id: str,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """壁打ち進捗を取得"""
    try:
        service = get_service()
        progress = await service.get_sparring_progress(idea_id)

        return SparringProgressResponse(
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
