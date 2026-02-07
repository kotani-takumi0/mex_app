"""Initial schema for mex-app

Revision ID: 001
Revises:
Create Date: 2026-02-05

タスク1.2: データベーススキーマとマイグレーションの実装
Design.mdの Physical Data Model に基づく実装
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    初期スキーマの作成
    - decision_cases: 意思決定ケーステーブル
    - failure_pattern_tags: 失敗パターンタグマスターテーブル
    - case_failure_patterns: ケースと失敗パターンの関連テーブル
    - idea_memos: アイデアメモテーブル
    """
    # Decision Cases テーブル
    op.create_table(
        "decision_cases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("target_market", sa.String(255), nullable=True),
        sa.Column("business_model", sa.Text(), nullable=True),
        sa.Column("outcome", sa.String(50), nullable=False),  # adopted, rejected, withdrawn, cancelled
        sa.Column("decision_type", sa.String(10), nullable=False),  # go, no_go
        sa.Column("decision_reason", sa.Text(), nullable=False),
        sa.Column("failed_hypotheses", postgresql.JSONB(astext_type=sa.Text()), server_default="[]"),
        sa.Column("discussions", postgresql.JSONB(astext_type=sa.Text()), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Failure Pattern Tags テーブル
    op.create_table(
        "failure_pattern_tags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),  # financial, operational, market, technical, organizational
    )

    # Case Failure Patterns 関連テーブル（多対多）
    op.create_table(
        "case_failure_patterns",
        sa.Column("case_id", sa.String(36), sa.ForeignKey("decision_cases.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.String(36), sa.ForeignKey("failure_pattern_tags.id", ondelete="CASCADE"), primary_key=True),
    )

    # Idea Memos テーブル（Go/NoGo判断がないレコード用）
    op.create_table(
        "idea_memos",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(255), nullable=True),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # インデックスの作成
    # title, purpose, target_marketへの全文検索インデックス
    op.create_index("idx_decision_cases_title", "decision_cases", ["title"])
    op.create_index("idx_decision_cases_outcome", "decision_cases", ["outcome"])
    op.create_index("idx_failure_pattern_tags_category", "failure_pattern_tags", ["category"])

    # PostgreSQL全文検索用のGINインデックス（title, purpose, target_market）
    op.execute("""
        CREATE INDEX idx_decision_cases_fulltext ON decision_cases
        USING GIN (to_tsvector('simple', title || ' ' || purpose || ' ' || COALESCE(target_market, '')))
    """)


def downgrade() -> None:
    """スキーマの削除"""
    op.execute("DROP INDEX IF EXISTS idx_decision_cases_fulltext")
    op.drop_index("idx_failure_pattern_tags_category", table_name="failure_pattern_tags")
    op.drop_index("idx_decision_cases_outcome", table_name="decision_cases")
    op.drop_index("idx_decision_cases_title", table_name="decision_cases")
    op.drop_table("idea_memos")
    op.drop_table("case_failure_patterns")
    op.drop_table("failure_pattern_tags")
    op.drop_table("decision_cases")
