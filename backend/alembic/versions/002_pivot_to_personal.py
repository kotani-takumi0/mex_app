"""Pivot to personal dev idea sparring app

Revision ID: 002
Revises: 001
Create Date: 2026-02-07

個人開発向けピボット:
- usersテーブル追加
- decision_cases, idea_memosにuser_idカラム追加
- usage_logsテーブル追加
- subscriptionsテーブル追加
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Users テーブル
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("auth_provider", sa.String(20), nullable=False, server_default="email"),
        sa.Column("plan", sa.String(20), nullable=False, server_default="free"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_plan", "users", ["plan"])

    # デフォルトユーザーを作成（既存データのマイグレーション用）
    op.execute("""
        INSERT INTO users (id, email, display_name, auth_provider, plan)
        VALUES ('00000000-0000-0000-0000-000000000000', 'legacy@mex.app', 'Legacy User', 'email', 'free')
    """)

    # decision_cases に user_id カラム追加
    op.add_column(
        "decision_cases",
        sa.Column("user_id", sa.String(36), nullable=True),
    )
    # 既存データにデフォルトuser_idを設定
    op.execute("""
        UPDATE decision_cases SET user_id = '00000000-0000-0000-0000-000000000000'
        WHERE user_id IS NULL
    """)
    op.alter_column("decision_cases", "user_id", nullable=False)
    op.create_foreign_key(
        "fk_decision_cases_user_id",
        "decision_cases",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("idx_decision_cases_user_id", "decision_cases", ["user_id"])

    # idea_memos に user_id カラム追加
    op.add_column(
        "idea_memos",
        sa.Column("user_id", sa.String(36), nullable=True),
    )
    op.execute("""
        UPDATE idea_memos SET user_id = '00000000-0000-0000-0000-000000000000'
        WHERE user_id IS NULL
    """)
    op.alter_column("idea_memos", "user_id", nullable=False)
    op.create_foreign_key(
        "fk_idea_memos_user_id",
        "idea_memos",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("idx_idea_memos_user_id", "idea_memos", ["user_id"])

    # Usage Logs テーブル
    op.create_table(
        "usage_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_usage_logs_user_id", "usage_logs", ["user_id"])
    op.create_index("idx_usage_logs_created_at", "usage_logs", ["created_at"])

    # Subscriptions テーブル
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("plan", sa.String(20), nullable=False, server_default="free"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("idx_subscriptions_stripe_customer_id", "subscriptions", ["stripe_customer_id"])


def downgrade() -> None:
    op.drop_table("subscriptions")
    op.drop_table("usage_logs")

    op.drop_index("idx_idea_memos_user_id", table_name="idea_memos")
    op.drop_constraint("fk_idea_memos_user_id", "idea_memos", type_="foreignkey")
    op.drop_column("idea_memos", "user_id")

    op.drop_index("idx_decision_cases_user_id", table_name="decision_cases")
    op.drop_constraint("fk_decision_cases_user_id", "decision_cases", type_="foreignkey")
    op.drop_column("decision_cases", "user_id")

    op.drop_index("idx_users_plan", table_name="users")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_table("users")
