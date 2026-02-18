"""
プランベースの利用制限ガード

Freeプランのユーザーに対してプロジェクト数・クイズ生成回数の
上限を適用する。FastAPI Depends パターンで各エンドポイントに注入。
"""

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser, get_current_user_dependency
from app.infrastructure.database.models import Project, UsageLog, User
from app.infrastructure.database.session import get_db

FREE_PROJECT_LIMIT = 2
FREE_QUIZ_MONTHLY_LIMIT = 2


def _get_user_plan(user_id: str, db: Session) -> str:
    """
    DBから最新のプランを取得する。

    JWTに含まれるplanはトークン発行時点の値であり、
    Webhook経由でプランが変更されてもJWTは更新されない。
    そのためDB側の値を正とする。
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return "free"
    return user.plan or "free"


async def check_project_limit(
    current_user: CurrentUser = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
) -> CurrentUser:
    """Freeプランのプロジェクト作成上限をチェック"""
    plan = _get_user_plan(current_user.user_id, db)
    if plan != "free":
        return current_user

    project_count = (
        db.query(Project)
        .filter(Project.user_id == current_user.user_id)
        .count()
    )

    if project_count >= FREE_PROJECT_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Freeプランではプロジェクトは{FREE_PROJECT_LIMIT}件までです。Proプランにアップグレードしてください。",
        )

    return current_user


async def check_quiz_limit(
    current_user: CurrentUser = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
) -> CurrentUser:
    """Freeプランのクイズ生成月間上限をチェック"""
    plan = _get_user_plan(current_user.user_id, db)
    if plan != "free":
        return current_user

    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    quiz_count = (
        db.query(UsageLog)
        .filter(
            UsageLog.user_id == current_user.user_id,
            UsageLog.action == "quiz_generate",
            UsageLog.created_at >= month_start,
        )
        .count()
    )

    if quiz_count >= FREE_QUIZ_MONTHLY_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Freeプランではクイズ生成は月{FREE_QUIZ_MONTHLY_LIMIT}回までです。Proプランにアップグレードしてください。",
        )

    return current_user
