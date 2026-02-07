"""
TDD: 類似検索エンジンのテスト
タスク2.2: 類似検索エンジンの実装

Design.mdに基づく仕様:
- Qdrantへのベクトル類似検索機能
- PostgreSQLの全文検索（BM25相当）とベクトル検索のハイブリッド検索
- ベクトルスコアとテキストスコアの重み付け調整
- リランキング機能
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from dataclasses import dataclass

from app.domain.similarity.similarity_engine import (
    SimilarityEngine,
    SimilarityConfig,
    SimilarityResult,
    HybridSearchInput,
    VectorSearchInput,
    CaseFilter,
)


class TestSimilarityConfig:
    """類似検索設定のテスト"""

    def test_default_config_values(self):
        """デフォルト設定が正しい"""
        config = SimilarityConfig()
        assert config.vector_weight == 0.7
        assert config.text_weight == 0.3
        assert config.default_limit == 10

    def test_custom_config_values(self):
        """カスタム設定が正しく適用される"""
        config = SimilarityConfig(
            vector_weight=0.5,
            text_weight=0.5,
            default_limit=20,
        )
        assert config.vector_weight == 0.5
        assert config.text_weight == 0.5
        assert config.default_limit == 20


class TestSimilarityResult:
    """類似検索結果のテスト"""

    def test_similarity_result_has_required_fields(self):
        """結果に必須フィールドが含まれる"""
        result = SimilarityResult(
            case_id="case-001",
            score=0.85,
            vector_score=0.9,
            text_score=0.7,
            matched_segments=["セグメント1"],
        )
        assert result.case_id == "case-001"
        assert result.score == 0.85
        assert result.vector_score == 0.9
        assert result.text_score == 0.7
        assert result.matched_segments == ["セグメント1"]


class TestHybridSearchInput:
    """ハイブリッド検索入力のテスト"""

    def test_hybrid_search_input_defaults(self):
        """デフォルト値が正しい"""
        input_data = HybridSearchInput(
            query_text="テストクエリ",
            limit=10,
        )
        assert input_data.query_text == "テストクエリ"
        assert input_data.limit == 10
        assert input_data.vector_weight == 0.7
        assert input_data.text_weight == 0.3
        assert input_data.filters is None


class TestVectorSearchInput:
    """ベクトル検索入力のテスト"""

    def test_vector_search_input(self):
        """ベクトル検索入力が正しく作成できる"""
        input_data = VectorSearchInput(
            query_embedding=[0.1] * 3072,
            limit=5,
        )
        assert len(input_data.query_embedding) == 3072
        assert input_data.limit == 5


class TestCaseFilter:
    """ケースフィルターのテスト"""

    def test_case_filter_by_outcome(self):
        """outcomeでフィルタリングできる"""
        filter_data = CaseFilter(outcomes=["rejected", "withdrawn"])
        assert filter_data.outcomes == ["rejected", "withdrawn"]

    def test_case_filter_by_failure_patterns(self):
        """failure_patternsでフィルタリングできる"""
        filter_data = CaseFilter(failure_patterns=["market", "financial"])
        assert filter_data.failure_patterns == ["market", "financial"]


class TestSimilarityEngineVectorSearch:
    """SimilarityEngineのベクトル検索テスト"""

    @pytest.fixture
    def mock_qdrant_client(self):
        """モックQdrantクライアント"""
        with patch("app.domain.similarity.similarity_engine.QdrantClientWrapper") as mock:
            yield mock

    @pytest.fixture
    def mock_embedding_service(self):
        """モック埋め込みサービス"""
        with patch("app.domain.similarity.similarity_engine.EmbeddingService") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_vector_search_returns_results(self, mock_qdrant_client, mock_embedding_service):
        """ベクトル検索が結果を返す"""
        # モックの設定
        mock_client = Mock()
        mock_search_result = Mock()
        mock_search_result.id = "case-001"
        mock_search_result.score = 0.85
        mock_search_result.payload = {"case_id": "case-001"}
        mock_query_response = Mock()
        mock_query_response.points = [mock_search_result]
        mock_client.client.query_points.return_value = mock_query_response
        mock_qdrant_client.return_value = mock_client

        engine = SimilarityEngine()
        input_data = VectorSearchInput(
            query_embedding=[0.1] * 3072,
            limit=5,
        )
        results = await engine.vector_search(input_data)

        assert len(results) == 1
        assert results[0].case_id == "case-001"
        assert results[0].vector_score == 0.85

    @pytest.mark.asyncio
    async def test_vector_search_with_filters(self, mock_qdrant_client, mock_embedding_service):
        """フィルター付きベクトル検索"""
        mock_client = Mock()
        mock_query_response = Mock()
        mock_query_response.points = []
        mock_client.client.query_points.return_value = mock_query_response
        mock_qdrant_client.return_value = mock_client

        engine = SimilarityEngine()
        input_data = VectorSearchInput(
            query_embedding=[0.1] * 3072,
            limit=5,
            filters=CaseFilter(outcomes=["rejected"]),
        )
        await engine.vector_search(input_data)

        # フィルターが適用されたことを確認
        call_args = mock_client.client.query_points.call_args
        assert call_args is not None


class TestSimilarityEngineHybridSearch:
    """SimilarityEngineのハイブリッド検索テスト"""

    @pytest.fixture
    def mock_qdrant_client(self):
        """モックQdrantクライアント"""
        with patch("app.domain.similarity.similarity_engine.QdrantClientWrapper") as mock:
            yield mock

    @pytest.fixture
    def mock_embedding_service(self):
        """モック埋め込みサービス"""
        with patch("app.domain.similarity.similarity_engine.EmbeddingService") as mock:
            mock_instance = AsyncMock()
            mock_result = Mock()
            mock_result.embedding = [0.1] * 3072
            mock_instance.embed_text = AsyncMock(return_value=mock_result)
            mock.return_value = mock_instance
            yield mock

    @pytest.fixture
    def mock_db_session(self):
        """モックDBセッション"""
        with patch("app.domain.similarity.similarity_engine.get_db") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_hybrid_search_combines_scores(
        self, mock_qdrant_client, mock_embedding_service, mock_db_session
    ):
        """ハイブリッド検索がスコアを組み合わせる"""
        # ベクトル検索のモック
        mock_client = Mock()
        mock_vector_result = Mock()
        mock_vector_result.id = "case-001"
        mock_vector_result.score = 0.9
        mock_vector_result.payload = {"case_id": "case-001"}
        mock_query_response = Mock()
        mock_query_response.points = [mock_vector_result]
        mock_client.client.query_points.return_value = mock_query_response
        mock_qdrant_client.return_value = mock_client

        # テキスト検索のモック
        mock_session = MagicMock()
        mock_text_result = MagicMock()
        mock_text_result.id = "case-001"
        mock_text_result.rank = 0.7
        mock_session.execute.return_value.fetchall.return_value = [
            ("case-001", 0.7, "マッチしたテキスト")
        ]
        mock_db_session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db_session.return_value.__exit__ = Mock(return_value=None)

        engine = SimilarityEngine()
        input_data = HybridSearchInput(
            query_text="テストクエリ",
            limit=10,
            vector_weight=0.7,
            text_weight=0.3,
        )
        results = await engine.hybrid_search(input_data)

        assert len(results) >= 1
        # スコアが組み合わされていることを確認
        for result in results:
            assert result.score == result.vector_score * 0.7 + result.text_score * 0.3

    @pytest.mark.asyncio
    async def test_hybrid_search_with_custom_weights(
        self, mock_qdrant_client, mock_embedding_service, mock_db_session
    ):
        """カスタム重み付けでハイブリッド検索"""
        mock_client = Mock()
        mock_vector_result = Mock()
        mock_vector_result.id = "case-001"
        mock_vector_result.score = 0.8
        mock_vector_result.payload = {"case_id": "case-001"}
        mock_query_response = Mock()
        mock_query_response.points = [mock_vector_result]
        mock_client.client.query_points.return_value = mock_query_response
        mock_qdrant_client.return_value = mock_client

        mock_session = MagicMock()
        mock_session.execute.return_value.fetchall.return_value = [
            ("case-001", 0.6, "マッチテキスト")
        ]
        mock_db_session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db_session.return_value.__exit__ = Mock(return_value=None)

        engine = SimilarityEngine()
        input_data = HybridSearchInput(
            query_text="テストクエリ",
            limit=10,
            vector_weight=0.5,
            text_weight=0.5,
        )
        results = await engine.hybrid_search(input_data)

        # カスタム重みが適用されていることを確認
        for result in results:
            expected_score = result.vector_score * 0.5 + result.text_score * 0.5
            assert abs(result.score - expected_score) < 0.001


class TestSimilarityEngineReranking:
    """リランキング機能のテスト"""

    def test_rerank_by_score(self):
        """スコアによるリランキング"""
        results = [
            SimilarityResult(case_id="c1", score=0.5, vector_score=0.5, text_score=0.5, matched_segments=[]),
            SimilarityResult(case_id="c2", score=0.9, vector_score=0.9, text_score=0.9, matched_segments=[]),
            SimilarityResult(case_id="c3", score=0.7, vector_score=0.7, text_score=0.7, matched_segments=[]),
        ]

        engine = SimilarityEngine.__new__(SimilarityEngine)
        reranked = engine._rerank_results(results)

        assert reranked[0].case_id == "c2"
        assert reranked[1].case_id == "c3"
        assert reranked[2].case_id == "c1"
