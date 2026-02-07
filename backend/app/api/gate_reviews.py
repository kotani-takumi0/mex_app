"""
ゲートレビューAPIエンドポイント
タスク4.2: ゲートレビューAPIエンドポイントの実装

Design.mdに基づく仕様:
- POST /api/gate-reviews/agenda: アジェンダ候補を生成して返却
- GET /api/gate-reviews/decision-reasons: 過去の採用/不採用理由を検索
"""
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.application.gate_review_service import (
    GateReviewService,
    AgendaRequest,
    HypothesisStatus as DomainHypothesisStatus,
    DecisionReasonSearchRequest,
)
from app.domain.pattern.pattern_analyzer import ProjectPhase

router = APIRouter(prefix="/gate-reviews", tags=["Gate Reviews"])


# リクエスト/レスポンススキーマ
class HypothesisStatusSchema(BaseModel):
    """仮説状況スキーマ"""
    hypothesis: str = Field(..., description="仮説")
    status: str = Field(..., description="状況（verified, falsified, pending）")
    confidence: float = Field(..., ge=0.0, le=1.0, description="信頼度")


class CreateAgendaRequest(BaseModel):
    """アジェンダ生成リクエスト"""
    project_id: str = Field(..., description="プロジェクトID")
    current_phase: str = Field(..., description="現在のフェーズ")
    hypothesis_status: list[HypothesisStatusSchema] = Field(
        default_factory=list, description="仮説状況リスト"
    )


class AgendaItemResponse(BaseModel):
    """アジェンダ項目レスポンス"""
    title: str
    description: str
    priority: int
    related_case_ids: list[str]
    suggested_duration_minutes: int


class SimilarCaseResponse(BaseModel):
    """類似ケースレスポンス"""
    case_id: str
    title: str
    purpose: str
    outcome: str
    score: float
    matched_segments: list[str]


class DiscussionPointResponse(BaseModel):
    """論点レスポンス"""
    topic: str
    key_questions: list[str]
    historical_context: str
    recommended_outcome: str


class AgendaResponseSchema(BaseModel):
    """アジェンダ生成レスポンス"""
    agenda_items: list[AgendaItemResponse]
    related_cases: list[SimilarCaseResponse]
    key_discussion_points: list[DiscussionPointResponse]


class DecisionReasonResponse(BaseModel):
    """判断理由レスポンス"""
    case_id: str
    case_title: str
    decision: str
    primary_reason: str
    contributing_factors: list[str]
    relevance_score: float


# サービスインスタンス
_service: GateReviewService | None = None


def get_service() -> GateReviewService:
    """サービスインスタンスを取得"""
    global _service
    if _service is None:
        _service = GateReviewService()
    return _service


@router.post("/agenda", response_model=AgendaResponseSchema)
async def generate_agenda(request: CreateAgendaRequest):
    """
    会議のアジェンダ候補を生成

    案件フェーズと仮説状況に基づき、アジェンダを自動生成する
    """
    try:
        service = get_service()

        # フェーズを変換
        try:
            phase = ProjectPhase(request.current_phase)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid phase: {request.current_phase}",
            )

        domain_request = AgendaRequest(
            project_id=request.project_id,
            current_phase=phase,
            hypothesis_status=[
                DomainHypothesisStatus(
                    hypothesis=h.hypothesis,
                    status=h.status,
                    confidence=h.confidence,
                )
                for h in request.hypothesis_status
            ],
        )

        result = await service.generate_agenda(domain_request)

        return AgendaResponseSchema(
            agenda_items=[
                AgendaItemResponse(
                    title=item.title,
                    description=item.description,
                    priority=item.priority,
                    related_case_ids=item.related_case_ids,
                    suggested_duration_minutes=item.suggested_duration_minutes,
                )
                for item in result.agenda_items
            ],
            related_cases=[
                SimilarCaseResponse(
                    case_id=c.case_id,
                    title=c.title,
                    purpose=c.purpose,
                    outcome=c.outcome.value,
                    score=c.score,
                    matched_segments=c.matched_segments,
                )
                for c in result.related_cases
            ],
            key_discussion_points=[
                DiscussionPointResponse(
                    topic=p.topic,
                    key_questions=p.key_questions,
                    historical_context=p.historical_context,
                    recommended_outcome=p.recommended_outcome,
                )
                for p in result.key_discussion_points
            ],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/decision-reasons", response_model=list[DecisionReasonResponse])
async def search_decision_reasons(
    query: str = Query(..., description="検索クエリ"),
    limit: int = Query(10, ge=1, le=50, description="取得件数"),
):
    """
    過去の採用/不採用理由を検索

    指定したクエリに関連する過去の判断理由を検索する
    """
    try:
        service = get_service()

        request = DecisionReasonSearchRequest(
            query=query,
            limit=limit,
        )

        results = await service.search_decision_reasons(request)

        return [
            DecisionReasonResponse(
                case_id=r.case_id,
                case_title=r.case_title,
                decision=r.decision,
                primary_reason=r.primary_reason,
                contributing_factors=r.contributing_factors,
                relevance_score=r.relevance_score,
            )
            for r in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
