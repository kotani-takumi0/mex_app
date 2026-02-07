"""
ダッシュボードAPIエンドポイント
アイデア一覧・利用量・履歴の表示
"""
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import CurrentUser, get_current_user_dependency
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import DecisionCase, IdeaMemo, UsageLog

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class CaseSummary(BaseModel):
    """ケースサマリー"""
    id: str
    title: str
    outcome: str
    created_at: str


class UsageSummary(BaseModel):
    """利用量サマリー"""
    sparring_count_today: int
    retrospective_count_month: int
    total_cases: int


class DashboardResponse(BaseModel):
    """ダッシュボードレスポンス"""
    recent_cases: list[CaseSummary]
    usage: UsageSummary


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """
    ダッシュボード情報を取得

    ユーザーのアイデア一覧・利用量・履歴を返却する。
    認証必須。
    """
    db = SessionLocal()
    try:
        # 最近のケース一覧（最新20件）
        recent_cases = (
            db.query(DecisionCase)
            .filter(DecisionCase.user_id == current_user.user_id)
            .order_by(DecisionCase.created_at.desc())
            .limit(20)
            .all()
        )

        case_summaries = [
            CaseSummary(
                id=c.id,
                title=c.title,
                outcome=c.outcome,
                created_at=c.created_at.isoformat() if c.created_at else "",
            )
            for c in recent_cases
        ]

        # 利用量集計
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        sparring_count_today = (
            db.query(UsageLog)
            .filter(
                UsageLog.user_id == current_user.user_id,
                UsageLog.action == "idea_sparring",
                UsageLog.created_at >= today_start,
            )
            .count()
        )

        retrospective_count_month = (
            db.query(UsageLog)
            .filter(
                UsageLog.user_id == current_user.user_id,
                UsageLog.action == "retrospective",
                UsageLog.created_at >= month_start,
            )
            .count()
        )

        total_cases = (
            db.query(DecisionCase)
            .filter(DecisionCase.user_id == current_user.user_id)
            .count()
        )

        return DashboardResponse(
            recent_cases=case_summaries,
            usage=UsageSummary(
                sparring_count_today=sparring_count_today,
                retrospective_count_month=retrospective_count_month,
                total_cases=total_cases,
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    finally:
        db.close()
