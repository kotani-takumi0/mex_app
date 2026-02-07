"""
セマンティックキャッシュ
タスク6.3: パフォーマンス検証と最適化
"""
import time
from typing import Any
from dataclasses import dataclass
from threading import Lock


@dataclass
class CacheEntry:
    """キャッシュエントリ"""

    query: str
    response: Any
    created_at: float
    hit_count: int = 0


class SemanticCache:
    """セマンティックキャッシュ（LLMレスポンスのキャッシュ）"""

    def __init__(
        self,
        similarity_threshold: float = 0.9,
        ttl_seconds: float = 3600.0,
        max_entries: int = 1000,
    ):
        """
        Args:
            similarity_threshold: 類似度閾値
            ttl_seconds: キャッシュの有効期限（秒）
            max_entries: 最大エントリ数
        """
        self.similarity_threshold = similarity_threshold
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._cache: dict[str, CacheEntry] = {}
        self._lock = Lock()

    def _is_expired(self, entry: CacheEntry) -> bool:
        """エントリが期限切れかチェック"""
        return (time.time() - entry.created_at) > self.ttl_seconds

    def _compute_similarity(self, query1: str, query2: str) -> float:
        """
        クエリ間の類似度を計算（簡易実装）

        実際の実装では埋め込みベクトルのコサイン類似度を使用
        """
        # 簡易実装: 完全一致のみ
        if query1 == query2:
            return 1.0
        # 部分一致
        common = set(query1) & set(query2)
        total = set(query1) | set(query2)
        return len(common) / len(total) if total else 0.0

    def get(self, query: str) -> Any | None:
        """
        キャッシュからレスポンスを取得

        Args:
            query: クエリ文字列

        Returns:
            キャッシュされたレスポンス、またはNone
        """
        with self._lock:
            # 完全一致チェック
            if query in self._cache:
                entry = self._cache[query]
                if self._is_expired(entry):
                    del self._cache[query]
                    return None
                entry.hit_count += 1
                return entry.response

            # 類似クエリ検索（簡易実装）
            for cached_query, entry in list(self._cache.items()):
                if self._is_expired(entry):
                    del self._cache[cached_query]
                    continue

                similarity = self._compute_similarity(query, cached_query)
                if similarity >= self.similarity_threshold:
                    entry.hit_count += 1
                    return entry.response

            return None

    def set(self, query: str, response: Any) -> None:
        """
        レスポンスをキャッシュに保存

        Args:
            query: クエリ文字列
            response: レスポンス
        """
        with self._lock:
            # 最大エントリ数チェック
            if len(self._cache) >= self.max_entries:
                self._evict_oldest()

            self._cache[query] = CacheEntry(
                query=query,
                response=response,
                created_at=time.time(),
            )

    def _evict_oldest(self) -> None:
        """最も古いエントリを削除"""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at,
        )
        del self._cache[oldest_key]

    def clear(self) -> None:
        """キャッシュをクリア"""
        with self._lock:
            self._cache.clear()

    def get_stats(self) -> dict:
        """キャッシュ統計を取得"""
        with self._lock:
            total_hits = sum(e.hit_count for e in self._cache.values())
            return {
                "entries": len(self._cache),
                "total_hits": total_hits,
                "max_entries": self.max_entries,
            }
