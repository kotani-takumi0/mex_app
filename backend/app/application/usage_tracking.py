"""
利用量記録

UsageLogテーブルにアクション履歴を書き込む。
独立したDBセッションで実行し、呼び出し元のトランザクションに影響しない。
"""

import logging

from app.infrastructure.database.models import UsageLog
from app.infrastructure.database.session import SessionLocal

logger = logging.getLogger(__name__)


def log_usage(user_id: str, action: str, tokens_used: int = 0) -> None:
    """UsageLogに1レコードを書き込む"""
    db = SessionLocal()
    try:
        record = UsageLog(
            user_id=user_id,
            action=action,
            tokens_used=tokens_used,
        )
        db.add(record)
        db.commit()
    except Exception:
        db.rollback()
        logger.error("Failed to log usage: user=%s action=%s", user_id, action, exc_info=True)
    finally:
        db.close()
