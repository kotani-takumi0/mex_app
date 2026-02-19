"""
データベースモデル定義
MEX App（AI開発ポートフォリオ）向けスキーマ
"""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
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

    # --- 既存カラム（変更なし） ---
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # OAuth時はnull
    auth_provider = Column(String(20), nullable=False, default="email")  # email, google, github
    plan = Column(String(20), nullable=False, default="free")  # free, pro
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # --- 新規カラム ---
    username = Column(String(50), nullable=True, unique=True)
    bio = Column(Text, nullable=True)
    github_url = Column(String(500), nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
    )


class Project(Base):
    """
    プロジェクトテーブル
    ユーザーが開発したプロジェクトを管理する
    """

    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, default=list)
    repository_url = Column(String(500), nullable=True)
    demo_url = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="in_progress")
    is_public = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User", back_populates="projects")
    devlog_entries = relationship(
        "DevLogEntry", back_populates="project", cascade="all, delete-orphan"
    )
    __table_args__ = (
        Index("idx_projects_user_id", "user_id"),
        Index("idx_projects_status", "status"),
        Index("idx_projects_is_public", "is_public"),
    )


class DevLogEntry(Base):
    """
    技術ドキュメント
    MCPサーバーまたは手動入力から保存される技術ドキュメント
    """

    __tablename__ = "devlog_entries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    source = Column(String(20), nullable=False, default="manual")
    entry_type = Column(String(30), nullable=False)

    summary = Column(String(500), nullable=False)
    detail = Column(Text, nullable=True)
    technologies = Column(JSON, default=list)
    ai_tool = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    # SQLAlchemyの予約語と衝突を避けるため属性名はmetadata_にする
    metadata_ = Column("metadata", JSON, default=dict)

    # pgvector: 類似検索用のembeddingベクトル（1536次元, text-embedding-3-small）
    embedding = Column(Vector(1536), nullable=True)

    # Relationships
    project = relationship("Project", back_populates="devlog_entries")
    __table_args__ = (
        Index("idx_devlog_entries_project_id", "project_id"),
        Index("idx_devlog_entries_user_id", "user_id"),
        Index("idx_devlog_entries_created_at", "created_at"),
        Index("idx_devlog_entries_entry_type", "entry_type"),
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
    user_id = Column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_subscription_id = Column(String(255), nullable=True)
    plan = Column(String(20), nullable=False, default="free")
    status = Column(String(20), nullable=False, default="active")
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    __table_args__ = (
        Index("idx_subscriptions_user_id", "user_id"),
        Index("idx_subscriptions_stripe_customer_id", "stripe_customer_id"),
    )


class MCPToken(Base):
    """
    MCPトークン管理テーブル
    MCP Server用の長寿命トークンを管理し、無効化（revoke）をサポートする
    """

    __tablename__ = "mcp_tokens"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)  # トークンの識別名（例: "MacBook Pro"）
    scope = Column(String(100), nullable=False, default="devlog:write")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_mcp_tokens_user_id", "user_id"),
        Index("idx_mcp_tokens_token_hash", "token_hash"),
    )


class StripeWebhookEvent(Base):
    """
    Stripe Webhookイベント重複排除テーブル
    同一イベントの二重処理を防止する
    """

    __tablename__ = "stripe_webhook_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    stripe_event_id = Column(String(255), nullable=False, unique=True)
    event_type = Column(String(100), nullable=False)
    processed_at = Column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (Index("idx_stripe_webhook_events_stripe_event_id", "stripe_event_id"),)
