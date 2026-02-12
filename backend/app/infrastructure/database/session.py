"""
データベースセッション管理
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import get_settings

settings = get_settings()

# エンジン作成（PostgreSQL用、本番向けプール設定込み）
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
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
