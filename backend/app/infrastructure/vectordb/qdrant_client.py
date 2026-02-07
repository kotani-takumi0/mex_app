"""
Qdrantベクトルデータベースクライアント

ピボット後:
- 1536次元のCosine距離でdecision_casesコレクションを作成（text-embedding-3-small）
- case_id, outcome, failure_patterns, user_idのペイロードスキーマを定義
- ローカル（host/port）とQdrant Cloud（url/api_key）の両方に対応
"""
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PayloadSchemaType

from app.config import get_settings


# 定数: ピボット後はtext-embedding-3-small (1536次元) を使用
COLLECTION_NAME = "decision_cases"
VECTOR_SIZE = 1536  # OpenAI text-embedding-3-small
DISTANCE_METRIC = "Cosine"

# ペイロードスキーマ
PAYLOAD_SCHEMA: dict[str, str] = {
    "case_id": "keyword",
    "outcome": "keyword",
    "failure_patterns": "keyword[]",
    "user_id": "keyword",
}


@dataclass
class QdrantConfig:
    """Qdrant接続設定"""
    host: str = "localhost"
    port: int = 6333
    url: str | None = None  # Qdrant Cloud URL
    api_key: str | None = None  # Qdrant Cloud APIキー
    collection_name: str = COLLECTION_NAME
    vector_size: int = VECTOR_SIZE
    distance: str = DISTANCE_METRIC

    @classmethod
    def from_settings(cls) -> "QdrantConfig":
        """アプリケーション設定から生成"""
        settings = get_settings()
        return cls(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )


class QdrantClientWrapper:
    """
    Qdrantクライアントのラッパー

    ローカル（host/port）とQdrant Cloud（url/api_key）の両方に対応。
    url が設定されている場合はCloud接続を優先する。
    """

    def __init__(self, config: QdrantConfig | None = None):
        """
        クライアントの初期化

        Args:
            config: Qdrant設定。Noneの場合はデフォルト設定を使用
        """
        self.config = config or QdrantConfig()
        # Qdrant Cloud（URL+APIキー）が設定されている場合はそちらを使用
        if self.config.url:
            self._client = QdrantClient(
                url=self.config.url,
                api_key=self.config.api_key,
            )
        else:
            self._client = QdrantClient(
                host=self.config.host,
                port=self.config.port,
            )

    @property
    def client(self) -> QdrantClient:
        """内部クライアントへのアクセス"""
        return self._client

    def collection_exists(self) -> bool:
        """
        コレクションが存在するかチェック

        Returns:
            bool: コレクションが存在する場合True
        """
        return self._client.collection_exists(self.config.collection_name)

    def create_collection(self) -> None:
        """
        コレクションを作成

        Design.mdの仕様に基づく:
        - 3072次元ベクトル
        - Cosine距離
        - HNSWインデックス（デフォルトパラメータ）
        """
        self._client.create_collection(
            collection_name=self.config.collection_name,
            vectors_config=VectorParams(
                size=self.config.vector_size,
                distance=Distance.COSINE,
            ),
            # HNSWインデックスの初期パラメータ
            hnsw_config=models.HnswConfigDiff(
                m=16,  # 各ノードの接続数
                ef_construct=100,  # インデックス構築時の探索幅
            ),
        )

    def ensure_collection(self) -> bool:
        """
        コレクションが存在しない場合に作成

        Returns:
            bool: 新しく作成された場合True、既存の場合False
        """
        if not self.collection_exists():
            self.create_collection()
            return True
        return False

    def get_collection_info(self) -> Any:
        """
        コレクション情報を取得

        Returns:
            コレクションの詳細情報
        """
        return self._client.get_collection(self.config.collection_name)

    def delete_collection(self) -> bool:
        """
        コレクションを削除

        Returns:
            bool: 削除成功の場合True
        """
        return self._client.delete_collection(self.config.collection_name)


@lru_cache
def get_qdrant_client() -> QdrantClientWrapper:
    """
    Qdrantクライアントのシングルトンインスタンスを取得

    Returns:
        QdrantClientWrapper: 設定済みのクライアント
    """
    config = QdrantConfig.from_settings()
    return QdrantClientWrapper(config)
