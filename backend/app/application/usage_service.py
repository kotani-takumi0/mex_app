"""
利用量管理サービス
プラン別の利用量チェック・記録・リセット
"""
from datetime import datetime, timezone
from typing import NamedTuple

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import UsageLog, DecisionCase

# ティア別制限
PLAN_LIMITS = {
    "free": {
        "sparring_per_day": 5,
        "retrospective_per_month": 10,
        "total_cases": 50,
    },
    "pro": {
        "sparring_per_day": 50,
        "retrospective_per_month": 999999,  # 実質無制限
        "total_cases": 500,
    },
}


class UsageStatus(NamedTuple):
    """利用量ステータス"""
    used: int
    limit: int
    remaining: int
    is_exceeded: bool


class UsageService:
    """
    利用量管理サービス

    ユーザーのプランに応じた利用量チェックと記録を行う。
    制限超過時はHTTP 429を返すために使用される。
    """

    def check_sparring_quota(self, user_id: str, plan: str) -> UsageStatus:
        """壁打ち回数の制限をチェック（日次）"""
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

            used = (
                db.query(UsageLog)
                .filter(
                    UsageLog.user_id == user_id,
                    UsageLog.action == "idea_sparring",
                    UsageLog.created_at >= today_start,
                )
                .count()
            )

            limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])["sparring_per_day"]
            remaining = max(0, limit - used)

            return UsageStatus(
                used=used,
                limit=limit,
                remaining=remaining,
                is_exceeded=used >= limit,
            )
        finally:
            db.close()

    def check_retrospective_quota(self, user_id: str, plan: str) -> UsageStatus:
        """振り返り回数の制限をチェック（月次）"""
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            used = (
                db.query(UsageLog)
                .filter(
                    UsageLog.user_id == user_id,
                    UsageLog.action == "retrospective",
                    UsageLog.created_at >= month_start,
                )
                .count()
            )

            limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])["retrospective_per_month"]
            remaining = max(0, limit - used)

            return UsageStatus(
                used=used,
                limit=limit,
                remaining=remaining,
                is_exceeded=used >= limit,
            )
        finally:
            db.close()

    def check_case_quota(self, user_id: str, plan: str) -> UsageStatus:
        """保存ケース数の制限をチェック"""
        db = SessionLocal()
        try:
            used = (
                db.query(DecisionCase)
                .filter(DecisionCase.user_id == user_id)
                .count()
            )

            limit = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])["total_cases"]
            remaining = max(0, limit - used)

            return UsageStatus(
                used=used,
                limit=limit,
                remaining=remaining,
                is_exceeded=used >= limit,
            )
        finally:
            db.close()

    def record_usage(self, user_id: str, action: str, tokens_used: int = 0) -> None:
        """利用を記録"""
        db = SessionLocal()
        try:
            log = UsageLog(
                user_id=user_id,
                action=action,
                tokens_used=tokens_used,
            )
            db.add(log)
            db.commit()
        finally:
            db.close()
