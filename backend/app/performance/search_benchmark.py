"""
類似検索ベンチマーク
タスク6.3: パフォーマンス検証と最適化
"""
import time
import random
from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkResult:
    """ベンチマーク結果"""

    num_cases: int
    num_queries: int
    top_k: int
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    success_rate: float
    avg_results_count: float


class SearchBenchmark:
    """類似検索ベンチマーク"""

    def __init__(self):
        self._mock_cases: list[dict] = []

    def _generate_mock_cases(self, num_cases: int) -> list[dict]:
        """モックケースデータを生成"""
        cases = []
        for i in range(num_cases):
            cases.append({
                "id": f"case-{i}",
                "title": f"テストケース {i}",
                "purpose": f"テスト目的 {i}",
                "embedding": [random.random() for _ in range(128)],  # 簡略化
            })
        return cases

    def _mock_similarity_search(
        self,
        query: str,
        cases: list[dict],
        top_k: int,
    ) -> list[dict]:
        """モック類似検索（実際のベクトル検索をシミュレート）"""
        # 検索処理のシミュレーション（軽量な処理）
        # 実際のベクトル計算を模倣するため少しだけ待機
        time.sleep(random.uniform(0.001, 0.005))

        # ランダムにtop_k件選択
        results = random.sample(cases, min(top_k, len(cases)))
        return [
            {
                "case_id": r["id"],
                "score": random.uniform(0.5, 1.0),
            }
            for r in results
        ]

    def run_similarity_search_benchmark(
        self,
        num_cases: int = 1000,
        num_queries: int = 10,
        top_k: int = 10,
    ) -> BenchmarkResult:
        """
        類似検索のベンチマークを実行

        Args:
            num_cases: テストケース数
            num_queries: クエリ数
            top_k: 取得件数

        Returns:
            BenchmarkResult: ベンチマーク結果
        """
        # モックデータ生成
        cases = self._generate_mock_cases(num_cases)

        response_times: list[float] = []
        results_counts: list[int] = []
        successful = 0

        for i in range(num_queries):
            query = f"テストクエリ {i}"

            start_time = time.time()
            try:
                results = self._mock_similarity_search(query, cases, top_k)
                elapsed_ms = (time.time() - start_time) * 1000

                response_times.append(elapsed_ms)
                results_counts.append(len(results))
                successful += 1
            except Exception:
                response_times.append(0)
                results_counts.append(0)

        return BenchmarkResult(
            num_cases=num_cases,
            num_queries=num_queries,
            top_k=top_k,
            avg_response_time_ms=sum(response_times) / len(response_times) if response_times else 0,
            min_response_time_ms=min(response_times) if response_times else 0,
            max_response_time_ms=max(response_times) if response_times else 0,
            success_rate=successful / num_queries if num_queries > 0 else 0,
            avg_results_count=sum(results_counts) / len(results_counts) if results_counts else 0,
        )
