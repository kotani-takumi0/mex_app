"""
データベースセッション管理
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# Render Starter プランは接続数が限られるため、本番では控えめなプール設定を使用
_is_production = settings.app_env == "production"

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5 if _is_production else 20,
    max_overflow=3 if _is_production else 10,
    pool_timeout=30,
    pool_recycle=600 if _is_production else 3600,
    echo=settings.debug,
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションの依存性注入用ジェネレータ
    FastAPIのDependsで使用。例外時は自動ロールバック。
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
