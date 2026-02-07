"""
TDD: Qdrantベクトルデータベースのテスト
タスク1.3: Qdrantベクトルデータベースのセットアップ
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.infrastructure.vectordb.qdrant_client import (
    QdrantClientWrapper,
    QdrantConfig,
    COLLECTION_NAME,
    VECTOR_SIZE,
    DISTANCE_METRIC,
)


class TestQdrantConfig:
    """Qdrant設定のテスト"""

    def test_default_config_values(self):
        """デフォルト設定が正しい"""
        config = QdrantConfig()
        assert config.host == "localhost"
        assert config.port == 6333
        assert config.collection_name == "decision_cases"
        assert config.vector_size == 3072
        assert config.distance == "Cosine"

    def test_custom_config_values(self):
        """カスタム設定が正しく適用される"""
        config = QdrantConfig(
            host="qdrant.example.com",
            port=6334,
            collection_name="custom_cases",
            vector_size=1536,
            distance="Euclid",
        )
        assert config.host == "qdrant.example.com"
        assert config.port == 6334
        assert config.collection_name == "custom_cases"
        assert config.vector_size == 1536
        assert config.distance == "Euclid"


class TestQdrantConstants:
    """Qdrant定数のテスト"""

    def test_collection_name(self):
        """コレクション名が正しい"""
        assert COLLECTION_NAME == "decision_cases"

    def test_vector_size(self):
        """ベクトルサイズが3072次元"""
        assert VECTOR_SIZE == 3072

    def test_distance_metric(self):
        """距離メトリックがCosine"""
        assert DISTANCE_METRIC == "Cosine"


class TestQdrantClientWrapper:
    """QdrantClientWrapperのテスト"""

    @pytest.fixture
    def mock_qdrant_client(self):
        """モックQdrantクライアント"""
        with patch("app.infrastructure.vectordb.qdrant_client.QdrantClient") as mock:
            yield mock

    def test_wrapper_initialization(self, mock_qdrant_client):
        """ラッパーが正しく初期化される"""
        config = QdrantConfig()
        wrapper = QdrantClientWrapper(config)

        mock_qdrant_client.assert_called_once_with(
            host=config.host,
            port=config.port,
        )
        assert wrapper.config == config

    def test_collection_exists_returns_true(self, mock_qdrant_client):
        """コレクションが存在する場合Trueを返す"""
        mock_client = Mock()
        mock_client.collection_exists.return_value = True
        mock_qdrant_client.return_value = mock_client

        config = QdrantConfig()
        wrapper = QdrantClientWrapper(config)

        assert wrapper.collection_exists() is True
        mock_client.collection_exists.assert_called_once_with(config.collection_name)

    def test_collection_exists_returns_false(self, mock_qdrant_client):
        """コレクションが存在しない場合Falseを返す"""
        mock_client = Mock()
        mock_client.collection_exists.return_value = False
        mock_qdrant_client.return_value = mock_client

        config = QdrantConfig()
        wrapper = QdrantClientWrapper(config)

        assert wrapper.collection_exists() is False

    def test_create_collection_with_correct_params(self, mock_qdrant_client):
        """正しいパラメータでコレクションを作成"""
        mock_client = Mock()
        mock_qdrant_client.return_value = mock_client

        config = QdrantConfig()
        wrapper = QdrantClientWrapper(config)
        wrapper.create_collection()

        mock_client.create_collection.assert_called_once()
        call_args = mock_client.create_collection.call_args

        assert call_args.kwargs["collection_name"] == "decision_cases"
        # VectorParams の検証
        vectors_config = call_args.kwargs["vectors_config"]
        assert vectors_config.size == 3072
        assert vectors_config.distance.name == "COSINE"

    def test_ensure_collection_creates_if_not_exists(self, mock_qdrant_client):
        """コレクションが存在しない場合に作成する"""
        mock_client = Mock()
        mock_client.collection_exists.return_value = False
        mock_qdrant_client.return_value = mock_client

        config = QdrantConfig()
        wrapper = QdrantClientWrapper(config)
        result = wrapper.ensure_collection()

        assert result is True
        mock_client.create_collection.assert_called_once()

    def test_ensure_collection_skips_if_exists(self, mock_qdrant_client):
        """コレクションが既に存在する場合は作成しない"""
        mock_client = Mock()
        mock_client.collection_exists.return_value = True
        mock_qdrant_client.return_value = mock_client

        config = QdrantConfig()
        wrapper = QdrantClientWrapper(config)
        result = wrapper.ensure_collection()

        assert result is False
        mock_client.create_collection.assert_not_called()

    def test_get_collection_info(self, mock_qdrant_client):
        """コレクション情報を取得できる"""
        mock_client = Mock()
        mock_info = Mock()
        mock_info.points_count = 100
        mock_info.vectors_count = 100
        mock_client.get_collection.return_value = mock_info
        mock_qdrant_client.return_value = mock_client

        config = QdrantConfig()
        wrapper = QdrantClientWrapper(config)
        info = wrapper.get_collection_info()

        assert info.points_count == 100
        mock_client.get_collection.assert_called_once_with(config.collection_name)


class TestQdrantPayloadSchema:
    """Qdrantペイロードスキーマのテスト"""

    @pytest.fixture
    def mock_qdrant_client(self):
        """モックQdrantクライアント"""
        with patch("app.infrastructure.vectordb.qdrant_client.QdrantClient") as mock:
            yield mock

    def test_payload_schema_has_case_id(self, mock_qdrant_client):
        """ペイロードスキーマにcase_idがある"""
        from app.infrastructure.vectordb.qdrant_client import PAYLOAD_SCHEMA
        assert "case_id" in PAYLOAD_SCHEMA
        assert PAYLOAD_SCHEMA["case_id"] == "keyword"

    def test_payload_schema_has_outcome(self, mock_qdrant_client):
        """ペイロードスキーマにoutcomeがある"""
        from app.infrastructure.vectordb.qdrant_client import PAYLOAD_SCHEMA
        assert "outcome" in PAYLOAD_SCHEMA
        assert PAYLOAD_SCHEMA["outcome"] == "keyword"

    def test_payload_schema_has_failure_patterns(self, mock_qdrant_client):
        """ペイロードスキーマにfailure_patternsがある"""
        from app.infrastructure.vectordb.qdrant_client import PAYLOAD_SCHEMA
        assert "failure_patterns" in PAYLOAD_SCHEMA
        assert PAYLOAD_SCHEMA["failure_patterns"] == "keyword[]"
