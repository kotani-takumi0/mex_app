"""
TDD: 意思決定ケースマネージャーのテスト
タスク2.3: 意思決定ケースマネージャーの実装

Design.mdに基づく仕様:
- 意思決定ケースのCRUD操作
- PostgreSQLへのメタデータ保存とQdrantへのベクトル保存の連携
- 類似ケース検索のファサード
- 失敗パターンタグの管理
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timezone

from app.domain.case.case_manager import (
    CaseManager,
    CaseCreateInput,
    DecisionCase,
    SimilarCase,
    FailurePatternTag,
    CaseOutcome,
    GoNoGoDecision,
)


class TestCaseCreateInput:
    """ケース作成入力のテスト"""

    def test_case_create_input_has_required_fields(self):
        """必須フィールドが含まれる"""
        input_data = CaseCreateInput(
            title="テストケース",
            purpose="テスト目的",
            outcome=CaseOutcome.REJECTED,
            decision=GoNoGoDecision(decision="no_go", reason="収益性の懸念"),
        )
        assert input_data.title == "テストケース"
        assert input_data.purpose == "テスト目的"
        assert input_data.outcome == CaseOutcome.REJECTED

    def test_case_create_input_with_optional_fields(self):
        """オプションフィールドが設定できる"""
        input_data = CaseCreateInput(
            title="テストケース",
            purpose="テスト目的",
            target_market="日本市場",
            business_model="SaaSモデル",
            outcome=CaseOutcome.ADOPTED,
            decision=GoNoGoDecision(decision="go", reason="収益性が高い"),
            failed_hypotheses=[{"hypothesis": "仮説1", "reason": "理由1"}],
            discussions=[{"topic": "議論1", "summary": "要約1"}],
        )
        assert input_data.target_market == "日本市場"
        assert input_data.business_model == "SaaSモデル"


class TestDecisionCase:
    """DecisionCaseのテスト"""

    def test_decision_case_has_all_fields(self):
        """全フィールドが含まれる"""
        case = DecisionCase(
            id="case-001",
            title="テストケース",
            purpose="テスト目的",
            target_market="日本",
            business_model="SaaS",
            outcome=CaseOutcome.REJECTED,
            decision=GoNoGoDecision(decision="no_go", reason="理由"),
            failed_hypotheses=[],
            discussions=[],
            failure_patterns=[],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        assert case.id == "case-001"
        assert case.title == "テストケース"


class TestCaseManager:
    """CaseManagerのテスト"""

    @pytest.fixture
    def mock_db_session(self):
        """モックDBセッション"""
        with patch("app.domain.case.case_manager.SessionLocal") as mock:
            session = MagicMock()
            mock.return_value = session
            yield session

    @pytest.fixture
    def mock_qdrant_client(self):
        """モックQdrantクライアント"""
        with patch("app.domain.case.case_manager.QdrantClientWrapper") as mock:
            yield mock

    @pytest.fixture
    def mock_embedding_service(self):
        """モック埋め込みサービス"""
        with patch("app.domain.case.case_manager.EmbeddingService") as mock:
            mock_instance = AsyncMock()
            mock_result = Mock()
            mock_result.embedding = [0.1] * 3072
            mock_instance.embed_text = AsyncMock(return_value=mock_result)
            mock.return_value = mock_instance
            yield mock

    @pytest.fixture
    def mock_similarity_engine(self):
        """モック類似検索エンジン"""
        with patch("app.domain.case.case_manager.SimilarityEngine") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_create_case_saves_to_db(
        self, mock_db_session, mock_qdrant_client, mock_embedding_service, mock_similarity_engine
    ):
        """ケース作成がDBに保存される"""
        manager = CaseManager()
        input_data = CaseCreateInput(
            title="テストケース",
            purpose="テスト目的",
            outcome=CaseOutcome.REJECTED,
            decision=GoNoGoDecision(decision="no_go", reason="理由"),
        )

        result = await manager.create_case(input_data)

        assert result is not None
        assert result.title == "テストケース"
        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_called()

    @pytest.mark.asyncio
    async def test_create_case_saves_embedding_to_qdrant(
        self, mock_db_session, mock_qdrant_client, mock_embedding_service, mock_similarity_engine
    ):
        """ケース作成がQdrantにベクトルを保存する"""
        mock_client = Mock()
        mock_qdrant_client.return_value = mock_client

        manager = CaseManager()
        input_data = CaseCreateInput(
            title="テストケース",
            purpose="テスト目的",
            outcome=CaseOutcome.REJECTED,
            decision=GoNoGoDecision(decision="no_go", reason="理由"),
        )

        await manager.create_case(input_data)

        # Qdrantへのupsertが呼ばれることを確認
        mock_client.client.upsert.assert_called()

    @pytest.mark.asyncio
    async def test_get_case_by_id(
        self, mock_db_session, mock_qdrant_client, mock_embedding_service, mock_similarity_engine
    ):
        """IDでケースを取得"""
        from app.infrastructure.database.models import DecisionCase as DBDecisionCase

        mock_case = Mock(spec=DBDecisionCase)
        mock_case.id = "case-001"
        mock_case.title = "テストケース"
        mock_case.purpose = "目的"
        mock_case.target_market = None
        mock_case.business_model = None
        mock_case.outcome = "rejected"
        mock_case.decision_type = "no_go"
        mock_case.decision_reason = "理由"
        mock_case.failed_hypotheses = []
        mock_case.discussions = []
        mock_case.failure_patterns = []
        mock_case.created_at = datetime.now(timezone.utc)
        mock_case.updated_at = datetime.now(timezone.utc)

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_case

        manager = CaseManager()
        result = await manager.get_case_by_id("case-001")

        assert result is not None
        assert result.id == "case-001"

    @pytest.mark.asyncio
    async def test_find_similar_cases(
        self, mock_db_session, mock_qdrant_client, mock_embedding_service, mock_similarity_engine
    ):
        """類似ケース検索"""
        from app.domain.similarity.similarity_engine import SimilarityResult
        from app.infrastructure.database.models import DecisionCase as DBDecisionCase

        # 類似検索エンジンのモック
        mock_engine = AsyncMock()
        mock_engine.hybrid_search = AsyncMock(
            return_value=[
                SimilarityResult(
                    case_id="case-001",
                    score=0.9,
                    vector_score=0.9,
                    text_score=0.8,
                    matched_segments=["マッチ"],
                )
            ]
        )
        mock_similarity_engine.return_value = mock_engine

        # DBからのケース取得のモック
        mock_case = Mock(spec=DBDecisionCase)
        mock_case.id = "case-001"
        mock_case.title = "テストケース"
        mock_case.purpose = "目的"
        mock_case.target_market = None
        mock_case.business_model = None
        mock_case.outcome = "rejected"
        mock_case.decision_type = "no_go"
        mock_case.decision_reason = "理由"
        mock_case.failed_hypotheses = []
        mock_case.discussions = []
        mock_case.failure_patterns = []
        mock_case.created_at = datetime.now(timezone.utc)
        mock_case.updated_at = datetime.now(timezone.utc)

        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_case

        manager = CaseManager()
        results = await manager.find_similar_cases(
            query_text="テストクエリ",
            limit=5,
        )

        assert len(results) == 1
        assert results[0].case_id == "case-001"

    @pytest.mark.asyncio
    async def test_add_failure_pattern_tag(
        self, mock_db_session, mock_qdrant_client, mock_embedding_service, mock_similarity_engine
    ):
        """失敗パターンタグの追加"""
        from app.infrastructure.database.models import (
            DecisionCase as DBDecisionCase,
            FailurePatternTag as DBFailurePatternTag,
            CaseFailurePattern,
        )

        mock_case = Mock(spec=DBDecisionCase)
        mock_case.id = "case-001"
        mock_case.failure_patterns = []

        mock_tag = Mock(spec=DBFailurePatternTag)
        mock_tag.id = "tag-001"
        mock_tag.name = "市場規模の誤認"
        mock_tag.category = "market"

        mock_db_session.query.return_value.filter.return_value.first.side_effect = [
            mock_case,
            mock_tag,
        ]

        manager = CaseManager()
        tag = FailurePatternTag(
            id="tag-001",
            name="市場規模の誤認",
            description="市場規模を過大評価",
            category="market",
        )
        await manager.add_failure_pattern_tag("case-001", tag)

        mock_db_session.add.assert_called()
        mock_db_session.commit.assert_called()


class TestCaseOutcome:
    """CaseOutcomeのテスト"""

    def test_case_outcome_values(self):
        """全outcomeの値が正しい"""
        assert CaseOutcome.ADOPTED.value == "adopted"
        assert CaseOutcome.REJECTED.value == "rejected"
        assert CaseOutcome.WITHDRAWN.value == "withdrawn"
        assert CaseOutcome.CANCELLED.value == "cancelled"


class TestGoNoGoDecision:
    """GoNoGoDecisionのテスト"""

    def test_go_decision(self):
        """Go判断"""
        decision = GoNoGoDecision(decision="go", reason="収益性が高い")
        assert decision.decision == "go"
        assert decision.reason == "収益性が高い"

    def test_no_go_decision(self):
        """NoGo判断"""
        decision = GoNoGoDecision(decision="no_go", reason="リスクが高い")
        assert decision.decision == "no_go"
