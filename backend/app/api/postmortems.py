"""
ポストモーテムAPIエンドポイント
タスク4.3: ポストモーテムAPIエンドポイントの実装

Design.mdに基づく仕様:
- GET /api/postmortems/template/{projectId}: ポストモーテムテンプレートを取得
- POST /api/postmortems: ポストモーテム情報を受け取り、ケースまたはメモとして保存
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.application.postmortem_service import (
    PostmortemService,
    PostmortemSubmission,
    FailedHypothesis as DomainFailedHypothesis,
    DiscussionRecord as DomainDiscussionRecord,
    ProjectOutcome,
    GoNoGoDecision as DomainGoNoGoDecision,
)

router = APIRouter(prefix="/postmortems", tags=["Postmortems"])


# リクエスト/レスポンススキーマ
class TemplateSectionResponse(BaseModel):
    """テンプレートセクションレスポンス"""
    name: str
    description: str


class PostmortemTemplateResponse(BaseModel):
    """ポストモーテムテンプレートレスポンス"""
    project_id: str
    sections: list[TemplateSectionResponse]
    outcome_options: list[str]


class FailedHypothesisSchema(BaseModel):
    """失敗した仮説スキーマ"""
    hypothesis: str = Field(..., description="仮説")
    failure_reason: str = Field(..., description="失敗理由")


class DiscussionRecordSchema(BaseModel):
    """議論記録スキーマ"""
    topic: str = Field(..., description="トピック")
    summary: str = Field(..., description="要約")
    discussed_at: str = Field(..., description="議論日")


class GoNoGoDecisionSchema(BaseModel):
    """Go/NoGo判断スキーマ"""
    decision: str = Field(..., description="判断（go or no_go）")
    reason: str = Field(..., description="理由（1〜3文）")


class CreatePostmortemRequest(BaseModel):
    """ポストモーテム作成リクエスト"""
    project_id: str = Field(..., description="プロジェクトID")
    outcome: str = Field(..., description="結果（withdrawn, cancelled, pending）")
    decision: GoNoGoDecisionSchema | None = Field(None, description="Go/NoGo判断")
    failed_hypotheses: list[FailedHypothesisSchema] = Field(
        default_factory=list, description="失敗した仮説リスト"
    )
    discussions: list[DiscussionRecordSchema] = Field(
        default_factory=list, description="議論記録リスト"
    )


class PostmortemResultResponse(BaseModel):
    """ポストモーテム結果レスポンス"""
    record_type: str
    record_id: str
    assigned_patterns: list[str]


class FailurePatternSuggestionResponse(BaseModel):
    """失敗パターン提案レスポンス"""
    category: str
    name: str
    confidence: float
    rationale: str


# サービスインスタンス
_service: PostmortemService | None = None


def get_service() -> PostmortemService:
    """サービスインスタンスを取得"""
    global _service
    if _service is None:
        _service = PostmortemService()
    return _service


@router.get("/template/{project_id}", response_model=PostmortemTemplateResponse)
async def get_template(project_id: str):
    """
    ポストモーテムテンプレートを取得

    Args:
        project_id: プロジェクトID

    Returns:
        ポストモーテムテンプレート
    """
    try:
        service = get_service()
        template = await service.get_template(project_id)

        return PostmortemTemplateResponse(
            project_id=template.project_id,
            sections=[
                TemplateSectionResponse(
                    name=s["name"],
                    description=s["description"],
                )
                for s in template.sections
            ],
            outcome_options=template.outcome_options,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("", response_model=PostmortemResultResponse)
async def create_postmortem(request: CreatePostmortemRequest):
    """
    ポストモーテムを作成

    Go/NoGo判断の有無に応じて、ケースまたはメモとして保存する
    """
    try:
        service = get_service()

        # outcomeを変換
        try:
            outcome = ProjectOutcome(request.outcome)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid outcome: {request.outcome}",
            )

        # ドメインオブジェクトに変換
        decision = None
        if request.decision:
            decision = DomainGoNoGoDecision(
                decision=request.decision.decision,
                reason=request.decision.reason,
            )

        submission = PostmortemSubmission(
            project_id=request.project_id,
            outcome=outcome,
            decision=decision,
            failed_hypotheses=[
                DomainFailedHypothesis(
                    hypothesis=h.hypothesis,
                    failure_reason=h.failure_reason,
                )
                for h in request.failed_hypotheses
            ],
            discussions=[
                DomainDiscussionRecord(
                    topic=d.topic,
                    summary=d.summary,
                    discussed_at=d.discussed_at,
                )
                for d in request.discussions
            ],
        )

        result = await service.submit_postmortem(submission)

        return PostmortemResultResponse(
            record_type=result.record_type,
            record_id=result.record_id,
            assigned_patterns=result.assigned_patterns,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/suggest-patterns", response_model=list[FailurePatternSuggestionResponse])
async def suggest_failure_patterns(request: CreatePostmortemRequest):
    """
    失敗パターンを推定

    ポストモーテム情報から該当する失敗パターンを推定する
    """
    try:
        service = get_service()

        # outcomeを変換
        try:
            outcome = ProjectOutcome(request.outcome)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid outcome: {request.outcome}",
            )

        decision = None
        if request.decision:
            decision = DomainGoNoGoDecision(
                decision=request.decision.decision,
                reason=request.decision.reason,
            )

        submission = PostmortemSubmission(
            project_id=request.project_id,
            outcome=outcome,
            decision=decision,
            failed_hypotheses=[
                DomainFailedHypothesis(
                    hypothesis=h.hypothesis,
                    failure_reason=h.failure_reason,
                )
                for h in request.failed_hypotheses
            ],
            discussions=[
                DomainDiscussionRecord(
                    topic=d.topic,
                    summary=d.summary,
                    discussed_at=d.discussed_at,
                )
                for d in request.discussions
            ],
        )

        suggestions = await service.suggest_failure_patterns(submission)

        return [
            FailurePatternSuggestionResponse(
                category=s.category,
                name=s.name,
                confidence=s.confidence,
                rationale=s.rationale,
            )
            for s in suggestions
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
