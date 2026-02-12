"""
TDD: 埋め込み生成サービスのテスト

ピボット後:
- OpenAI text-embedding-3-small APIを使用（コスト最適化）
- 1536次元のベクトルを生成
- APIキー管理とレート制限対応
- リトライロジックとフォールバック処理
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.domain.embedding.embedding_service import (
    EmbeddingConfig,
    EmbeddingError,
    EmbeddingResult,
    EmbeddingService,
    RateLimitError,
)


class TestEmbeddingConfig:
    """埋め込み設定のテスト"""

    def test_default_config_values(self):
        """デフォルト設定が正しい"""
        config = EmbeddingConfig()
        assert config.model == "text-embedding-3-small"
        assert config.dimensions == 1536
        assert config.max_retries == 3
        assert config.retry_delay == 1.0

    def test_custom_config_values(self):
        """カスタム設定が正しく適用される"""
        config = EmbeddingConfig(
            model="text-embedding-3-small",
            dimensions=1536,
            max_retries=5,
            retry_delay=2.0,
        )
        assert config.model == "text-embedding-3-small"
        assert config.dimensions == 1536
        assert config.max_retries == 5
        assert config.retry_delay == 2.0


class TestEmbeddingResult:
    """埋め込み結果のテスト"""

    def test_embedding_result_has_vector(self):
        """結果にベクトルが含まれる"""
        vector = [0.1] * 3072
        result = EmbeddingResult(
            text="テストテキスト",
            embedding=vector,
            model="text-embedding-3-large",
            usage_tokens=10,
        )
        assert result.embedding == vector
        assert len(result.embedding) == 3072

    def test_embedding_result_has_metadata(self):
        """結果にメタデータが含まれる"""
        result = EmbeddingResult(
            text="テストテキスト",
            embedding=[0.1] * 3072,
            model="text-embedding-3-large",
            usage_tokens=10,
        )
        assert result.text == "テストテキスト"
        assert result.model == "text-embedding-3-large"
        assert result.usage_tokens == 10


class TestEmbeddingService:
    """EmbeddingServiceのテスト"""

    @pytest.fixture
    def mock_openai_client(self):
        """モックOpenAIクライアント"""
        with patch("app.domain.embedding.embedding_service.AsyncOpenAI") as mock:
            yield mock

    @pytest.fixture
    def embedding_service(self, mock_openai_client):
        """テスト用EmbeddingService"""
        mock_client = AsyncMock()
        mock_openai_client.return_value = mock_client
        return EmbeddingService(api_key="test-key")

    @pytest.mark.asyncio
    async def test_embed_text_returns_vector(self, mock_openai_client):
        """テキストからベクトルを生成"""
        # モックのセットアップ
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_embedding = Mock()
        mock_embedding.embedding = [0.1] * 3072
        mock_response.data = [mock_embedding]
        mock_response.usage.total_tokens = 10
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client

        service = EmbeddingService(api_key="test-key")
        result = await service.embed_text("テストテキスト")

        assert isinstance(result, EmbeddingResult)
        assert len(result.embedding) == 3072

    @pytest.mark.asyncio
    async def test_embed_text_calls_openai_with_correct_params(self, mock_openai_client):
        """OpenAI APIが正しいパラメータで呼び出される"""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_embedding = Mock()
        mock_embedding.embedding = [0.1] * 3072
        mock_response.data = [mock_embedding]
        mock_response.usage.total_tokens = 10
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client

        config = EmbeddingConfig(model="text-embedding-3-large", dimensions=3072)
        service = EmbeddingService(api_key="test-key", config=config)
        await service.embed_text("テストテキスト")

        mock_client.embeddings.create.assert_called_once_with(
            input="テストテキスト",
            model="text-embedding-3-large",
            dimensions=3072,
        )

    @pytest.mark.asyncio
    async def test_embed_batch_returns_multiple_vectors(self, mock_openai_client):
        """複数テキストからベクトルを一括生成"""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_embeddings = [Mock(embedding=[0.1] * 3072) for _ in range(3)]
        mock_response.data = mock_embeddings
        mock_response.usage.total_tokens = 30
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)
        mock_openai_client.return_value = mock_client

        service = EmbeddingService(api_key="test-key")
        texts = ["テキスト1", "テキスト2", "テキスト3"]
        results = await service.embed_batch(texts)

        assert len(results) == 3
        for result in results:
            assert len(result.embedding) == 3072


class TestEmbeddingServiceRetry:
    """リトライロジックのテスト"""

    @pytest.fixture
    def mock_openai_client(self):
        """モックOpenAIクライアント"""
        with patch("app.domain.embedding.embedding_service.AsyncOpenAI") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_retry_on_rate_limit(self, mock_openai_client):
        """レート制限時にリトライする"""
        mock_client = AsyncMock()

        # 最初の2回は失敗、3回目で成功
        mock_response = Mock()
        mock_embedding = Mock()
        mock_embedding.embedding = [0.1] * 3072
        mock_response.data = [mock_embedding]
        mock_response.usage.total_tokens = 10

        from openai import RateLimitError as OpenAIRateLimitError

        mock_client.embeddings.create = AsyncMock(
            side_effect=[
                OpenAIRateLimitError(
                    message="Rate limit exceeded",
                    response=Mock(status_code=429),
                    body=None,
                ),
                OpenAIRateLimitError(
                    message="Rate limit exceeded",
                    response=Mock(status_code=429),
                    body=None,
                ),
                mock_response,
            ]
        )
        mock_openai_client.return_value = mock_client

        config = EmbeddingConfig(max_retries=3, retry_delay=0.01)
        service = EmbeddingService(api_key="test-key", config=config)
        result = await service.embed_text("テスト")

        assert result is not None
        assert mock_client.embeddings.create.call_count == 3

    @pytest.mark.asyncio
    async def test_raises_after_max_retries(self, mock_openai_client):
        """最大リトライ回数を超えるとエラー"""
        mock_client = AsyncMock()

        from openai import RateLimitError as OpenAIRateLimitError

        mock_client.embeddings.create = AsyncMock(
            side_effect=OpenAIRateLimitError(
                message="Rate limit exceeded",
                response=Mock(status_code=429),
                body=None,
            )
        )
        mock_openai_client.return_value = mock_client

        config = EmbeddingConfig(max_retries=2, retry_delay=0.01)
        service = EmbeddingService(api_key="test-key", config=config)

        with pytest.raises(RateLimitError):
            await service.embed_text("テスト")

        assert mock_client.embeddings.create.call_count == 2


class TestEmbeddingServiceErrorHandling:
    """エラーハンドリングのテスト"""

    @pytest.fixture
    def mock_openai_client(self):
        """モックOpenAIクライアント"""
        with patch("app.domain.embedding.embedding_service.AsyncOpenAI") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_raises_embedding_error_on_api_error(self, mock_openai_client):
        """APIエラー時にEmbeddingErrorを発生"""
        mock_client = AsyncMock()

        from openai import APIError

        mock_client.embeddings.create = AsyncMock(
            side_effect=APIError(
                message="API Error",
                request=Mock(),
                body=None,
            )
        )
        mock_openai_client.return_value = mock_client

        service = EmbeddingService(api_key="test-key")

        with pytest.raises(EmbeddingError):
            await service.embed_text("テスト")

    @pytest.mark.asyncio
    async def test_empty_text_raises_error(self, mock_openai_client):
        """空テキストでエラー"""
        mock_client = AsyncMock()
        mock_openai_client.return_value = mock_client

        service = EmbeddingService(api_key="test-key")

        with pytest.raises(ValueError, match="text cannot be empty"):
            await service.embed_text("")
