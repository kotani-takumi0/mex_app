"""pgvector移行 + MCPトークン管理テーブル

Revision ID: 004
Revises: 003
Create Date: 2026-02-09

変更内容:
- pgvector拡張を有効化
- devlog_entries に embedding カラム追加（vector(1536)）
- IVFFlat インデックス作成（コサイン距離）
- mcp_tokens テーブル新規作成（トークン無効化対応）
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector 拡張を有効化
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # devlog_entries に embedding カラム追加
    op.execute("ALTER TABLE devlog_entries ADD COLUMN embedding vector(1536)")

    # IVFFlat インデックス作成（コサイン距離検索用）
    # rows < 1000 の場合は lists=1 で十分。データ増加時に再構築する。
    op.execute("""
        CREATE INDEX idx_devlog_entries_embedding
        ON devlog_entries
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 10)
    """)

    # mcp_tokens テーブル
    op.create_table(
        "mcp_tokens",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("scope", sa.String(100), nullable=False, server_default="devlog:write"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_mcp_tokens_user_id", "mcp_tokens", ["user_id"])
    op.create_index("idx_mcp_tokens_token_hash", "mcp_tokens", ["token_hash"])


def downgrade() -> None:
    op.drop_table("mcp_tokens")
    op.execute("DROP INDEX IF EXISTS idx_devlog_entries_embedding")
    op.execute("ALTER TABLE devlog_entries DROP COLUMN IF EXISTS embedding")
    op.execute("DROP EXTENSION IF EXISTS vector")
