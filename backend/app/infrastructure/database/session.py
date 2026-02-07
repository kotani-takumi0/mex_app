"""
データベースセッション管理
"""
from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import get_settings

settings = get_settings()

# エンジン作成（PostgreSQL用）
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug,
)

# セッションファクトリ
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションの依存性注入用ジェネレータ
    FastAPIのDependsで使用
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
