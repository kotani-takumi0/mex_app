"""
類似検索エンジンのテスト（pgvector版）

pgvectorを使用したベクトル類似検索のテスト。
実際のDBテストはインテグレーションテストで実施。
ここではデータクラスとエンジンの初期化をテスト。
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.domain.similarity.similarity_engine import (
    SimilarityEngine,
    SimilarityConfig,
    SimilarityResult,
    DevLogFilter,
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
            devlog_id="log-001",
            project_id="proj-001",
            score=0.85,
            summary="React Routerの設定を実装",
            entry_type="code_generation",
        )
        assert result.devlog_id == "log-001"
        assert result.project_id == "proj-001"
        assert result.score == 0.85
        assert result.summary == "React Routerの設定を実装"
        assert result.entry_type == "code_generation"


class TestDevLogFilter:
    """開発ログフィルターのテスト"""

    def test_filter_by_entry_types(self):
        """entry_typesでフィルタリングできる"""
        f = DevLogFilter(entry_types=["code_generation", "debug"])
        assert f.entry_types == ["code_generation", "debug"]

    def test_filter_by_technologies(self):
        """technologiesでフィルタリングできる"""
        f = DevLogFilter(technologies=["React", "TypeScript"])
        assert f.technologies == ["React", "TypeScript"]

    def test_empty_filter(self):
        """空フィルター"""
        f = DevLogFilter()
        assert f.entry_types is None
        assert f.technologies is None


class TestSimilarityEngineInit:
    """SimilarityEngineの初期化テスト"""

    @patch("app.domain.similarity.similarity_engine.EmbeddingService")
    def test_engine_initialization(self, mock_embedding):
        """エンジンが正しく初期化される"""
        engine = SimilarityEngine()
        assert engine.config.vector_weight == 0.7
        assert engine.config.default_limit == 10

    @patch("app.domain.similarity.similarity_engine.EmbeddingService")
    def test_engine_with_custom_config(self, mock_embedding):
        """カスタム設定でエンジンが初期化される"""
        config = SimilarityConfig(vector_weight=0.5, default_limit=20)
        engine = SimilarityEngine(config=config)
        assert engine.config.vector_weight == 0.5
        assert engine.config.default_limit == 20
