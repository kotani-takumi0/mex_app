"""
プロジェクト振り返りAPIエンドポイント
旧 postmortems.py をリネーム＋改修。

- GET /api/retrospectives/template/{projectId}: 振り返りテンプレートを取得
- POST /api/retrospectives: 振り返りを記録
- POST /api/retrospectives/suggest-patterns: 失敗パターンを推定
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.auth.dependencies import CurrentUser, get_current_user_dependency
from app.application.usage_service import UsageService
from app.application.retrospective_service import (
    RetrospectiveService,
    RetrospectiveSubmission,
    LessonLearned as DomainLessonLearned,
    DiscussionRecord as DomainDiscussionRecord,
    ProjectOutcome,
    ProjectDecision as DomainProjectDecision,
)

router = APIRouter(prefix="/retrospectives", tags=["Retrospectives"])


# リクエスト/レスポンススキーマ
class TemplateSectionResponse(BaseModel):
    """テンプレートセクションレスポンス"""
    name: str
    description: str


class RetrospectiveTemplateResponse(BaseModel):
    """振り返りテンプレートレスポンス"""
    project_id: str
    sections: list[TemplateSectionResponse]
    outcome_options: list[str]


class LessonLearnedSchema(BaseModel):
    """学んだことスキーマ"""
    topic: str = Field(..., description="トピック")
    insight: str = Field(..., description="インサイト")


class DiscussionRecordSchema(BaseModel):
    """振り返りメモスキーマ"""
    topic: str = Field(..., description="トピック")
    summary: str = Field(..., description="要約")
    discussed_at: str = Field(..., description="日付")


class ProjectDecisionSchema(BaseModel):
    """プロジェクト判断スキーマ"""
    decision: str = Field(..., description="判断（continue, pivot, stop）")
    reason: str = Field(..., description="理由")


class CreateRetrospectiveRequest(BaseModel):
    """振り返り作成リクエスト"""
    project_id: str = Field(..., description="プロジェクトID")
    project_title: str = Field(..., description="プロジェクト名")
    outcome: str = Field(..., description="結果（completed, shipped, withdrawn, cancelled, pending）")
    decision: ProjectDecisionSchema | None = Field(None, description="プロジェクト判断")
    lessons_learned: list[LessonLearnedSchema] = Field(
        default_factory=list, description="学んだことリスト"
    )
    discussions: list[DiscussionRecordSchema] = Field(
        default_factory=list, description="振り返りメモリスト"
    )


class RetrospectiveResultResponse(BaseModel):
    """振り返り結果レスポンス"""
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
_service: RetrospectiveService | None = None
_usage_service: UsageService | None = None


def get_service() -> RetrospectiveService:
    """サービスインスタンスを取得"""
    global _service
    if _service is None:
        _service = RetrospectiveService()
    return _service


def get_usage_service() -> UsageService:
    global _usage_service
    if _usage_service is None:
        _usage_service = UsageService()
    return _usage_service


@router.get("/template/{project_id}", response_model=RetrospectiveTemplateResponse)
async def get_template(
    project_id: str,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """振り返りテンプレートを取得"""
    try:
        service = get_service()
        template = await service.get_template(project_id)

        return RetrospectiveTemplateResponse(
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


@router.post("", response_model=RetrospectiveResultResponse)
async def create_retrospective(
    request: CreateRetrospectiveRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """
    振り返りを記録

    判断の有無に応じて、ケースまたはメモとして保存する。
    認証必須。
    """
    try:
        # 利用量チェック
        usage = get_usage_service()
        quota = usage.check_retrospective_quota(current_user.user_id, current_user.plan)
        if quota.is_exceeded:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"振り返り記録の上限に達しました（{quota.limit}件/月）。Proプランにアップグレードしてください。",
            )

        service = get_service()

        try:
            outcome = ProjectOutcome(request.outcome)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid outcome: {request.outcome}",
            )

        decision = None
        if request.decision:
            decision = DomainProjectDecision(
                decision=request.decision.decision,
                reason=request.decision.reason,
            )

        submission = RetrospectiveSubmission(
            project_id=request.project_id,
            project_title=request.project_title,
            outcome=outcome,
            decision=decision,
            lessons_learned=[
                DomainLessonLearned(
                    topic=ll.topic,
                    insight=ll.insight,
                )
                for ll in request.lessons_learned
            ],
            discussions=[
                DomainDiscussionRecord(
                    topic=d.topic,
                    summary=d.summary,
                    discussed_at=d.discussed_at,
                )
                for d in request.discussions
            ],
            user_id=current_user.user_id,
        )

        result = await service.submit_retrospective(submission)

        # 利用を記録
        usage.record_usage(current_user.user_id, "retrospective")

        return RetrospectiveResultResponse(
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
async def suggest_failure_patterns(
    request: CreateRetrospectiveRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """失敗パターンを推定"""
    try:
        service = get_service()

        try:
            outcome = ProjectOutcome(request.outcome)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid outcome: {request.outcome}",
            )

        decision = None
        if request.decision:
            decision = DomainProjectDecision(
                decision=request.decision.decision,
                reason=request.decision.reason,
            )

        submission = RetrospectiveSubmission(
            project_id=request.project_id,
            project_title=request.project_title,
            outcome=outcome,
            decision=decision,
            lessons_learned=[
                DomainLessonLearned(
                    topic=ll.topic,
                    insight=ll.insight,
                )
                for ll in request.lessons_learned
            ],
            discussions=[
                DomainDiscussionRecord(
                    topic=d.topic,
                    summary=d.summary,
                    discussed_at=d.discussed_at,
                )
                for d in request.discussions
            ],
            user_id=current_user.user_id,
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
