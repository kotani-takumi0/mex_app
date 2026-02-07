"""
埋め込み生成サービス

ピボット後:
- OpenAI text-embedding-3-small APIを使用（コスト最適化）
- 1536次元のベクトルを生成
- APIキー管理とレート制限対応
- リトライロジックとフォールバック処理
"""
import asyncio
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI, RateLimitError as OpenAIRateLimitError, APIError

from app.config import get_settings


class EmbeddingError(Exception):
    """埋め込み生成エラー"""
    pass


class RateLimitError(EmbeddingError):
    """レート制限エラー"""
    pass


@dataclass
class EmbeddingConfig:
    """埋め込み生成設定"""
    model: str = "text-embedding-3-small"
    dimensions: int = 1536
    max_retries: int = 3
    retry_delay: float = 1.0  # 秒


@dataclass
class EmbeddingResult:
    """埋め込み生成結果"""
    text: str
    embedding: list[float]
    model: str
    usage_tokens: int


class EmbeddingService:
    """
    埋め込み生成サービス

    OpenAI text-embedding-3-large APIを使用してテキストから
    3072次元のベクトルを生成する。
    """

    def __init__(
        self,
        api_key: str | None = None,
        config: EmbeddingConfig | None = None,
    ):
        """
        初期化

        Args:
            api_key: OpenAI APIキー。Noneの場合は環境変数から取得
            config: 埋め込み設定
        """
        self.config = config or EmbeddingConfig()

        if api_key is None:
            settings = get_settings()
            api_key = settings.openai_api_key

        self._client = AsyncOpenAI(api_key=api_key)

    async def embed_text(self, text: str) -> EmbeddingResult:
        """
        単一テキストの埋め込みを生成

        Args:
            text: 埋め込み対象のテキスト

        Returns:
            EmbeddingResult: 生成された埋め込み結果

        Raises:
            ValueError: テキストが空の場合
            RateLimitError: レート制限に達した場合（リトライ後も失敗）
            EmbeddingError: その他のAPIエラー
        """
        if not text:
            raise ValueError("text cannot be empty")

        return await self._embed_with_retry(text)

    async def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """
        複数テキストの埋め込みを一括生成

        Args:
            texts: 埋め込み対象のテキストリスト

        Returns:
            list[EmbeddingResult]: 生成された埋め込み結果のリスト
        """
        if not texts:
            return []

        for text in texts:
            if not text:
                raise ValueError("text cannot be empty")

        return await self._embed_batch_with_retry(texts)

    async def _embed_with_retry(self, text: str) -> EmbeddingResult:
        """リトライロジック付きで埋め込み生成"""
        last_error: Exception | None = None

        for attempt in range(self.config.max_retries):
            try:
                response = await self._client.embeddings.create(
                    input=text,
                    model=self.config.model,
                    dimensions=self.config.dimensions,
                )

                return EmbeddingResult(
                    text=text,
                    embedding=response.data[0].embedding,
                    model=self.config.model,
                    usage_tokens=response.usage.total_tokens,
                )

            except OpenAIRateLimitError as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    # エクスポネンシャルバックオフ
                    delay = self.config.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                continue

            except APIError as e:
                raise EmbeddingError(f"OpenAI API error: {e}") from e

        raise RateLimitError(
            f"Rate limit exceeded after {self.config.max_retries} retries"
        ) from last_error

    async def _embed_batch_with_retry(self, texts: list[str]) -> list[EmbeddingResult]:
        """リトライロジック付きで一括埋め込み生成"""
        last_error: Exception | None = None

        for attempt in range(self.config.max_retries):
            try:
                response = await self._client.embeddings.create(
                    input=texts,
                    model=self.config.model,
                    dimensions=self.config.dimensions,
                )

                results = []
                tokens_per_text = response.usage.total_tokens // len(texts)

                for i, text in enumerate(texts):
                    results.append(
                        EmbeddingResult(
                            text=text,
                            embedding=response.data[i].embedding,
                            model=self.config.model,
                            usage_tokens=tokens_per_text,
                        )
                    )

                return results

            except OpenAIRateLimitError as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                continue

            except APIError as e:
                raise EmbeddingError(f"OpenAI API error: {e}") from e

        raise RateLimitError(
            f"Rate limit exceeded after {self.config.max_retries} retries"
        ) from last_error
