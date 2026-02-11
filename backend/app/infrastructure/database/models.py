"""
データベースモデル定義
MEX App（AI開発ポートフォリオ）向けスキーマ
"""
import uuid
from datetime import datetime, timezone

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
)
from sqlalchemy.orm import DeclarativeBase, relationship

from pgvector.sqlalchemy import Vector


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
    devlog_entries = relationship("DevLogEntry", back_populates="project", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="project", cascade="all, delete-orphan")

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
    quiz_questions = relationship("QuizQuestion", back_populates="devlog_entry")

    __table_args__ = (
        Index("idx_devlog_entries_project_id", "project_id"),
        Index("idx_devlog_entries_user_id", "user_id"),
        Index("idx_devlog_entries_created_at", "created_at"),
        Index("idx_devlog_entries_entry_type", "entry_type"),
    )


class QuizQuestion(Base):
    """
    理解度チェック問題
    開発ログからLLMが自動生成する4択クイズ
    """
    __tablename__ = "quiz_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    devlog_entry_id = Column(String(36), ForeignKey("devlog_entries.id", ondelete="SET NULL"), nullable=True)

    technology = Column(String(100), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)
    difficulty = Column(String(10), nullable=False, default="medium")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    project = relationship("Project", back_populates="quiz_questions")
    devlog_entry = relationship("DevLogEntry", back_populates="quiz_questions")
    attempts = relationship("QuizAttempt", back_populates="question", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_quiz_questions_project_id", "project_id"),
        Index("idx_quiz_questions_user_id", "user_id"),
        Index("idx_quiz_questions_technology", "technology"),
    )


class QuizAttempt(Base):
    """
    クイズ回答記録
    ユーザーの各回答を記録し、スコア計算に使用
    """
    __tablename__ = "quiz_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quiz_question_id = Column(String(36), ForeignKey("quiz_questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    selected_answer = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_spent_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    question = relationship("QuizQuestion", back_populates="attempts")

    __table_args__ = (
        Index("idx_quiz_attempts_user_id", "user_id"),
        Index("idx_quiz_attempts_question_id", "quiz_question_id"),
    )


class SkillScore(Base):
    """
    技術別理解度スコア
    クイズ結果から集計される技術別のスコア
    """
    __tablename__ = "skill_scores"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    technology = Column(String(100), nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    total_questions = Column(Integer, nullable=False, default=0)
    correct_answers = Column(Integer, nullable=False, default=0)
    last_assessed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    __table_args__ = (
        Index("idx_skill_scores_user_id", "user_id"),
        Index("idx_skill_scores_technology", "technology"),
        Index("uq_skill_scores_user_tech", "user_id", "technology", unique=True),
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
