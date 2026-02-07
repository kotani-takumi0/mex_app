"""
TDD: データベースモデルのテスト
タスク1.2: データベーススキーマとマイグレーションの実装
"""
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models import (
    Base,
    DecisionCase,
    FailurePatternTag,
    CaseFailurePattern,
    IdeaMemo,
)
from app.infrastructure.database.migration import (
    check_alembic_configuration,
    get_pending_migrations,
)


class TestDecisionCaseModel:
    """DecisionCaseモデルのテスト"""

    def test_decision_case_has_required_fields(self):
        """DecisionCaseが必須フィールドを持つ"""
        case = DecisionCase(
            title="テストケース",
            purpose="テスト目的",
            outcome="rejected",
            decision_type="no_go",
            decision_reason="テスト理由",
        )
        assert case.title == "テストケース"
        assert case.purpose == "テスト目的"
        assert case.outcome == "rejected"
        assert case.decision_type == "no_go"
        assert case.decision_reason == "テスト理由"

    def test_decision_case_has_optional_fields(self):
        """DecisionCaseがオプションフィールドを持つ"""
        case = DecisionCase(
            title="テスト",
            purpose="目的",
            target_market="日本市場",
            business_model="SaaSモデル",
            outcome="adopted",
            decision_type="go",
            decision_reason="理由",
            failed_hypotheses=[{"hypothesis": "仮説1", "reason": "理由1"}],
            discussions=[{"topic": "議論1", "summary": "要約1"}],
        )
        assert case.target_market == "日本市場"
        assert case.business_model == "SaaSモデル"
        assert case.failed_hypotheses == [{"hypothesis": "仮説1", "reason": "理由1"}]
        assert case.discussions == [{"topic": "議論1", "summary": "要約1"}]

    def test_decision_case_outcome_values(self):
        """outcomeの値が正しく設定できる"""
        valid_outcomes = ["adopted", "rejected", "withdrawn", "cancelled"]
        for outcome in valid_outcomes:
            case = DecisionCase(
                title="テスト",
                purpose="目的",
                outcome=outcome,
                decision_type="go",
                decision_reason="理由",
            )
            assert case.outcome == outcome


class TestFailurePatternTagModel:
    """FailurePatternTagモデルのテスト"""

    def test_failure_pattern_tag_has_required_fields(self):
        """FailurePatternTagが必須フィールドを持つ"""
        tag = FailurePatternTag(
            name="実行体制の不備",
            category="organizational",
        )
        assert tag.name == "実行体制の不備"
        assert tag.category == "organizational"

    def test_failure_pattern_tag_categories(self):
        """カテゴリが正しく設定できる"""
        valid_categories = ["financial", "operational", "market", "technical", "organizational"]
        for category in valid_categories:
            tag = FailurePatternTag(name=f"テスト_{category}", category=category)
            assert tag.category == category


class TestIdeaMemoModel:
    """IdeaMemoモデルのテスト"""

    def test_idea_memo_has_required_fields(self):
        """IdeaMemoが必須フィールドを持つ"""
        memo = IdeaMemo(
            project_id="project-001",
            content={"title": "アイデア", "description": "説明"},
        )
        assert memo.project_id == "project-001"
        assert memo.content == {"title": "アイデア", "description": "説明"}


class TestDatabaseSchema:
    """データベーススキーマの統合テスト（SQLite使用）"""

    @pytest.fixture
    def engine(self):
        """テスト用SQLiteエンジン"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session(self, engine):
        """テスト用セッション"""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_create_decision_case(self, session):
        """DecisionCaseを作成できる"""
        case = DecisionCase(
            title="新規事業案",
            purpose="市場拡大",
            target_market="アジア",
            business_model="サブスクリプション",
            outcome="rejected",
            decision_type="no_go",
            decision_reason="収益性の懸念",
        )
        session.add(case)
        session.commit()

        result = session.query(DecisionCase).first()
        assert result.title == "新規事業案"
        assert result.id is not None

    def test_create_failure_pattern_tag(self, session):
        """FailurePatternTagを作成できる"""
        tag = FailurePatternTag(
            name="市場規模の誤認",
            description="市場規模を過大評価したパターン",
            category="market",
        )
        session.add(tag)
        session.commit()

        result = session.query(FailurePatternTag).first()
        assert result.name == "市場規模の誤認"

    def test_case_failure_pattern_relationship(self, session):
        """CaseとFailurePatternTagの関連付け"""
        case = DecisionCase(
            title="テスト案件",
            purpose="テスト",
            outcome="rejected",
            decision_type="no_go",
            decision_reason="理由",
        )
        tag = FailurePatternTag(name="テストパターン", category="technical")
        session.add(case)
        session.add(tag)
        session.commit()

        association = CaseFailurePattern(case_id=case.id, tag_id=tag.id)
        session.add(association)
        session.commit()

        result = session.query(CaseFailurePattern).first()
        assert result.case_id == case.id
        assert result.tag_id == tag.id

    def test_create_idea_memo(self, session):
        """IdeaMemoを作成できる"""
        memo = IdeaMemo(
            project_id="proj-123",
            content={"idea": "新しいアイデア", "notes": "メモ"},
        )
        session.add(memo)
        session.commit()

        result = session.query(IdeaMemo).first()
        assert result.project_id == "proj-123"
        assert result.content["idea"] == "新しいアイデア"


class TestAlembicConfiguration:
    """Alembic設定のテスト"""

    def test_alembic_env_imports_models(self):
        """Alembic env.pyがモデルのメタデータを参照している"""
        is_configured = check_alembic_configuration()
        assert is_configured, "Alembic env.py must import Base.metadata"

    def test_get_pending_migrations_returns_list(self):
        """get_pending_migrationsがリストを返す"""
        pending = get_pending_migrations()
        assert isinstance(pending, list)


class TestDatabaseIndexes:
    """データベースインデックスのテスト"""

    @pytest.fixture
    def engine(self):
        """テスト用SQLiteエンジン"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        return engine

    def test_decision_cases_has_title_index(self, engine):
        """decision_casesテーブルにtitleインデックスがある"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes("decision_cases")
        index_names = [idx["name"] for idx in indexes]
        assert "idx_decision_cases_title" in index_names

    def test_decision_cases_has_outcome_index(self, engine):
        """decision_casesテーブルにoutcomeインデックスがある"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes("decision_cases")
        index_names = [idx["name"] for idx in indexes]
        assert "idx_decision_cases_outcome" in index_names

    def test_failure_pattern_tags_has_category_index(self, engine):
        """failure_pattern_tagsテーブルにcategoryインデックスがある"""
        inspector = inspect(engine)
        indexes = inspector.get_indexes("failure_pattern_tags")
        index_names = [idx["name"] for idx in indexes]
        assert "idx_failure_pattern_tags_category" in index_names
