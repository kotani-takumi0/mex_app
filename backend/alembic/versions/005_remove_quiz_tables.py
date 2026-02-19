"""クイズ機能廃止: quiz_attempts, quiz_questions, skill_scores テーブルを削除

NotebookLM MCP連携への移行に伴い、自前クイズ機能を廃止する。
学習コンテンツ管理は既存の DevLogEntry + metadata JSON で行う。

Revision ID: 005
Revises: 004
Create Date: 2026-02-19
"""

from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # FK制約の依存関係を考慮した順序で削除
    # quiz_attempts → quiz_questions を参照
    op.drop_index("idx_quiz_attempts_question_id", table_name="quiz_attempts", if_exists=True)
    op.drop_index("idx_quiz_attempts_user_id", table_name="quiz_attempts", if_exists=True)
    op.drop_table("quiz_attempts")

    op.drop_index("idx_quiz_questions_technology", table_name="quiz_questions", if_exists=True)
    op.drop_index("idx_quiz_questions_user_id", table_name="quiz_questions", if_exists=True)
    op.drop_index("idx_quiz_questions_project_id", table_name="quiz_questions", if_exists=True)
    op.drop_table("quiz_questions")

    op.drop_index("uq_skill_scores_user_tech", table_name="skill_scores", if_exists=True)
    op.drop_index("idx_skill_scores_technology", table_name="skill_scores", if_exists=True)
    op.drop_index("idx_skill_scores_user_id", table_name="skill_scores", if_exists=True)
    op.drop_table("skill_scores")


def downgrade() -> None:
    import sqlalchemy as sa

    op.create_table(
        "skill_scores",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("technology", sa.String(100), nullable=False),
        sa.Column("score", sa.Float, nullable=False, server_default="0.0"),
        sa.Column("total_questions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("correct_answers", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_assessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_skill_scores_user_id", "skill_scores", ["user_id"])
    op.create_index("idx_skill_scores_technology", "skill_scores", ["technology"])
    op.create_index("uq_skill_scores_user_tech", "skill_scores", ["user_id", "technology"], unique=True)

    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("devlog_entry_id", sa.String(36), sa.ForeignKey("devlog_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("technology", sa.String(100), nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("options", sa.JSON, nullable=False),
        sa.Column("correct_answer", sa.Integer, nullable=False),
        sa.Column("explanation", sa.Text, nullable=False),
        sa.Column("difficulty", sa.String(10), nullable=False, server_default="medium"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_quiz_questions_project_id", "quiz_questions", ["project_id"])
    op.create_index("idx_quiz_questions_user_id", "quiz_questions", ["user_id"])
    op.create_index("idx_quiz_questions_technology", "quiz_questions", ["technology"])

    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("quiz_question_id", sa.String(36), sa.ForeignKey("quiz_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("selected_answer", sa.Integer, nullable=False),
        sa.Column("is_correct", sa.Boolean, nullable=False),
        sa.Column("time_spent_seconds", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_quiz_attempts_user_id", "quiz_attempts", ["user_id"])
    op.create_index("idx_quiz_attempts_question_id", "quiz_attempts", ["quiz_question_id"])
