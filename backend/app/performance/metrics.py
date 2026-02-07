"""
パフォーマンスメトリクス
タスク6.3: パフォーマンス検証と最適化
"""
import time
from collections import defaultdict
from threading import Lock
from typing import Any


class PerformanceMetrics:
    """パフォーマンスメトリクス収集"""

    def __init__(self):
        self._metrics: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def record_response_time(self, operation: str, time_ms: float) -> None:
        """
        レスポンスタイムを記録

        Args:
            operation: 操作名（例: "search", "llm_call"）
            time_ms: レスポンスタイム（ミリ秒）
        """
        with self._lock:
            self._metrics[operation].append(time_ms)

    def get_stats(self, operation: str) -> dict[str, Any]:
        """
        指定した操作の統計を取得

        Args:
            operation: 操作名

        Returns:
            統計情報
        """
        with self._lock:
            times = self._metrics.get(operation, [])

        if not times:
            return {
                "count": 0,
                "avg": 0,
                "min": 0,
                "max": 0,
                "p50": 0,
                "p95": 0,
                "p99": 0,
            }

        sorted_times = sorted(times)
        count = len(sorted_times)

        return {
            "count": count,
            "avg": sum(sorted_times) / count,
            "min": sorted_times[0],
            "max": sorted_times[-1],
            "p50": self._percentile(sorted_times, 50),
            "p95": self._percentile(sorted_times, 95),
            "p99": self._percentile(sorted_times, 99),
        }

    def _percentile(self, sorted_data: list[float], percentile: int) -> float:
        """パーセンタイルを計算"""
        if not sorted_data:
            return 0

        index = (percentile / 100) * (len(sorted_data) - 1)
        lower = int(index)
        upper = lower + 1

        if upper >= len(sorted_data):
            return sorted_data[-1]

        fraction = index - lower
        return sorted_data[lower] + fraction * (sorted_data[upper] - sorted_data[lower])

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """全操作の統計を取得"""
        with self._lock:
            operations = list(self._metrics.keys())

        return {op: self.get_stats(op) for op in operations}

    def clear(self, operation: str | None = None) -> None:
        """
        メトリクスをクリア

        Args:
            operation: 操作名（Noneの場合は全てクリア）
        """
        with self._lock:
            if operation is None:
                self._metrics.clear()
            elif operation in self._metrics:
                del self._metrics[operation]


class TimingContext:
    """タイミング計測コンテキスト"""

    def __init__(self, metrics: PerformanceMetrics, operation: str):
        self.metrics = metrics
        self.operation = operation
        self.start_time: float = 0

    def __enter__(self) -> "TimingContext":
        self.start_time = time.time()
        return self

    def __exit__(self, *args: Any) -> None:
        elapsed_ms = (time.time() - self.start_time) * 1000
        self.metrics.record_response_time(self.operation, elapsed_ms)
