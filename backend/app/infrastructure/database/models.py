"""
データベースモデル定義
個人開発アイデア壁打ちアプリ向けスキーマ
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
    Integer,
    Float,
    Boolean,
    Date,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """SQLAlchemy Base class"""
    pass


def generate_uuid() -> str:
    """UUID生成"""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """現在のUTC時刻を返す"""
    return datetime.now(timezone.utc)


class User(Base):
    """
    ユーザーテーブル
    メール/パスワードまたはOAuth認証に対応
    """
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # OAuth時はnull
    auth_provider = Column(String(20), nullable=False, default="email")  # email, google, github
    plan = Column(String(20), nullable=False, default="free")  # free, pro
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    cases = relationship("DecisionCase", back_populates="user", cascade="all, delete-orphan")
    idea_memos = relationship("IdeaMemo", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_plan", "plan"),
    )


class DecisionCase(Base):
    """
    意思決定ケーステーブル
    過去の採用案・没案を保存（ユーザー別にデータ分離）
    """
    __tablename__ = "decision_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    purpose = Column(Text, nullable=False)
    target_market = Column(String(255), nullable=True)
    business_model = Column(Text, nullable=True)
    outcome = Column(String(50), nullable=False)  # adopted, rejected, withdrawn, cancelled
    decision_type = Column(String(10), nullable=False)  # go, no_go
    decision_reason = Column(Text, nullable=False)
    failed_hypotheses = Column(JSON, default=list)
    discussions = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User", back_populates="cases")
    failure_patterns = relationship(
        "CaseFailurePattern",
        back_populates="case",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_decision_cases_title", "title"),
        Index("idx_decision_cases_outcome", "outcome"),
        Index("idx_decision_cases_user_id", "user_id"),
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
    Go/NoGo判断がないレコード用（ユーザー別にデータ分離）
    """
    __tablename__ = "idea_memos"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String(255), nullable=True)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    user = relationship("User", back_populates="idea_memos")

    __table_args__ = (
        Index("idx_idea_memos_user_id", "user_id"),
    )


class UsageLog(Base):
    """
    利用量ログテーブル
    各API呼び出しを記録
    """
    __tablename__ = "usage_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)  # idea_sparring, retrospective
    tokens_used = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        Index("idx_usage_logs_user_id", "user_id"),
        Index("idx_usage_logs_created_at", "created_at"),
    )


class Subscription(Base):
    """
    サブスクリプションテーブル
    Stripe決済と連動
    """
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    plan = Column(String(20), nullable=False, default="free")
    status = Column(String(20), nullable=False, default="active")  # active, canceled, past_due
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    __table_args__ = (
        Index("idx_subscriptions_user_id", "user_id"),
        Index("idx_subscriptions_stripe_customer_id", "stripe_customer_id"),
    )
