"""
データベースモデル定義
Design.mdの Physical Data Model に基づく実装
"""
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """SQLAlchemy Base class"""
    pass


def generate_uuid() -> str:
    """UUID生成（SQLite互換のため文字列を返す）"""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """現在のUTC時刻を返す"""
    return datetime.now(timezone.utc)


class DecisionCase(Base):
    """
    意思決定ケーステーブル
    過去の採用案・没案を保存
    """
    __tablename__ = "decision_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=False)
    target_market = Column(String(255), nullable=True)
    business_model = Column(Text, nullable=True)
    outcome = Column(String(50), nullable=False)  # adopted, rejected, withdrawn, cancelled
    decision_type = Column(String(10), nullable=False)  # go, no_go
    decision_reason = Column(Text, nullable=False)
    failed_hypotheses = Column(JSON, default=list)  # JSONB in PostgreSQL
    discussions = Column(JSON, default=list)  # JSONB in PostgreSQL
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    failure_patterns = relationship(
        "CaseFailurePattern",
        back_populates="case",
        cascade="all, delete-orphan",
    )

    # Indexes for full-text search (PostgreSQL specific)
    __table_args__ = (
        Index("idx_decision_cases_title", "title"),
        Index("idx_decision_cases_outcome", "outcome"),
    )


class FailurePatternTag(Base):
    """
    失敗パターンタグマスターテーブル
    カテゴリ: financial, operational, market, technical, organizational
    """
    __tablename__ = "failure_pattern_tags"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)

    # Relationships
    cases = relationship(
        "CaseFailurePattern",
        back_populates="tag",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_failure_pattern_tags_category", "category"),
    )


class CaseFailurePattern(Base):
    """
    ケースと失敗パターンの関連テーブル（多対多）
    """
    __tablename__ = "case_failure_patterns"

    case_id = Column(
        String(36),
        ForeignKey("decision_cases.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id = Column(
        String(36),
        ForeignKey("failure_pattern_tags.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    case = relationship("DecisionCase", back_populates="failure_patterns")
    tag = relationship("FailurePatternTag", back_populates="cases")


class IdeaMemo(Base):
    """
    アイデアメモテーブル
    Go/NoGo判断がないレコード用
    """
    __tablename__ = "idea_memos"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(255), nullable=True)
    content = Column(JSON, nullable=False)  # JSONB in PostgreSQL
    created_at = Column(DateTime(timezone=True), default=utc_now)
