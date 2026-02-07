"""Pivot to portfolio schema

Revision ID: 003
Revises: 002
Create Date: 2026-02-07

AI開発ポートフォリオ向けピボット:
- projects, devlog_entries, quiz_questions, quiz_attempts, skill_scores を追加
- users に username, bio, github_url を追加
- decision_cases, failure_pattern_tags, case_failure_patterns, idea_memos を削除
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users にプロフィール項目を追加
    op.add_column("users", sa.Column("username", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("github_url", sa.String(500), nullable=True))
    op.create_index("idx_users_username", "users", ["username"])
    op.create_unique_constraint("uq_users_username", "users", ["username"])

    # projects テーブル
    op.create_table(
        "projects",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("technologies", sa.JSON(), nullable=True),
        sa.Column("repository_url", sa.String(500), nullable=True),
        sa.Column("demo_url", sa.String(500), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_progress"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_projects_user_id", "projects", ["user_id"])
    op.create_index("idx_projects_status", "projects", ["status"])
    op.create_index("idx_projects_is_public", "projects", ["is_public"])

    # devlog_entries テーブル
    op.create_table(
        "devlog_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source", sa.String(20), nullable=False, server_default="manual"),
        sa.Column("entry_type", sa.String(30), nullable=False),
        sa.Column("summary", sa.String(500), nullable=False),
        sa.Column("detail", sa.Text(), nullable=True),
        sa.Column("technologies", sa.JSON(), nullable=True),
        sa.Column("ai_tool", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("metadata", sa.JSON(), nullable=True),
    )
    op.create_index("idx_devlog_entries_project_id", "devlog_entries", ["project_id"])
    op.create_index("idx_devlog_entries_user_id", "devlog_entries", ["user_id"])
    op.create_index("idx_devlog_entries_created_at", "devlog_entries", ["created_at"])
    op.create_index("idx_devlog_entries_entry_type", "devlog_entries", ["entry_type"])

    # quiz_questions テーブル
    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("devlog_entry_id", sa.String(36), sa.ForeignKey("devlog_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("technology", sa.String(100), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("correct_answer", sa.Integer(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(10), nullable=False, server_default="medium"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_quiz_questions_project_id", "quiz_questions", ["project_id"])
    op.create_index("idx_quiz_questions_user_id", "quiz_questions", ["user_id"])
    op.create_index("idx_quiz_questions_technology", "quiz_questions", ["technology"])

    # quiz_attempts テーブル
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("quiz_question_id", sa.String(36), sa.ForeignKey("quiz_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("selected_answer", sa.Integer(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_quiz_attempts_user_id", "quiz_attempts", ["user_id"])
    op.create_index("idx_quiz_attempts_question_id", "quiz_attempts", ["quiz_question_id"])

    # skill_scores テーブル
    op.create_table(
        "skill_scores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("technology", sa.String(100), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_questions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_answers", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_assessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_skill_scores_user_id", "skill_scores", ["user_id"])
    op.create_index("idx_skill_scores_technology", "skill_scores", ["technology"])
    op.create_index(
        "uq_skill_scores_user_tech",
        "skill_scores",
        ["user_id", "technology"],
        unique=True,
    )

    # 旧テーブルを削除
    op.drop_table("case_failure_patterns")
    op.drop_table("failure_pattern_tags")
    op.drop_table("decision_cases")
    op.drop_table("idea_memos")


def downgrade() -> None:
    # 旧テーブルの復元（簡略）
    op.create_table(
        "decision_cases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("target_market", sa.String(255), nullable=True),
        sa.Column("business_model", sa.Text(), nullable=True),
        sa.Column("outcome", sa.String(50), nullable=False),
        sa.Column("decision_type", sa.String(10), nullable=False),
        sa.Column("decision_reason", sa.Text(), nullable=False),
        sa.Column("failed_hypotheses", sa.JSON(), nullable=True),
        sa.Column("discussions", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_decision_cases_title", "decision_cases", ["title"])
    op.create_index("idx_decision_cases_outcome", "decision_cases", ["outcome"])
    op.create_index("idx_decision_cases_user_id", "decision_cases", ["user_id"])

    op.create_table(
        "failure_pattern_tags",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
    )
    op.create_index("idx_failure_pattern_tags_category", "failure_pattern_tags", ["category"])

    op.create_table(
        "case_failure_patterns",
        sa.Column("case_id", sa.String(36), primary_key=True),
        sa.Column("tag_id", sa.String(36), primary_key=True),
    )

    op.create_table(
        "idea_memos",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("project_id", sa.String(255), nullable=True),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_idea_memos_user_id", "idea_memos", ["user_id"])

    # 新テーブル削除
    op.drop_table("skill_scores")
    op.drop_table("quiz_attempts")
    op.drop_table("quiz_questions")
    op.drop_table("devlog_entries")
    op.drop_table("projects")

    # users カラム削除
    op.drop_constraint("uq_users_username", "users", type_="unique")
    op.drop_index("idx_users_username", table_name="users")
    op.drop_column("users", "github_url")
    op.drop_column("users", "bio")
    op.drop_column("users", "username")
