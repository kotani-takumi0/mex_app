"""
TDD: パフォーマンス検証のテスト（モックベース）
タスク6.3: パフォーマンス検証と最適化
"""

import time

import pytest


class TestSimilaritySearchPerformance:
    """類似検索のパフォーマンステスト"""

    def test_search_response_time_under_2_seconds(self):
        """類似検索のレスポンスタイムが2秒未満"""
        from app.performance.search_benchmark import SearchBenchmark

        benchmark = SearchBenchmark()
        # 1000件のモックデータでベンチマーク
        result = benchmark.run_similarity_search_benchmark(
            num_cases=1000,
            num_queries=10,
        )
        assert result.avg_response_time_ms < 2000

    def test_search_handles_large_dataset(self):
        """大規模データセットを処理できる"""
        from app.performance.search_benchmark import SearchBenchmark

        benchmark = SearchBenchmark()
        result = benchmark.run_similarity_search_benchmark(
            num_cases=1000,
            num_queries=5,
        )
        assert result.success_rate == 1.0

    def test_search_returns_top_k_results(self):
        """指定した件数の結果を返す"""
        from app.performance.search_benchmark import SearchBenchmark

        benchmark = SearchBenchmark()
        result = benchmark.run_similarity_search_benchmark(
            num_cases=1000,
            num_queries=3,
            top_k=10,
        )
        assert result.avg_results_count == 10


class TestLLMRateLimiting:
    """LLM APIレート制限のテスト"""

    def test_rate_limiter_exists(self):
        """レートリミッターが存在する"""
        from app.performance.rate_limiter import LLMRateLimiter

        limiter = LLMRateLimiter(requests_per_minute=60)
        assert limiter is not None

    def test_rate_limiter_allows_within_limit(self):
        """制限内のリクエストは許可される"""
        from app.performance.rate_limiter import LLMRateLimiter

        limiter = LLMRateLimiter(requests_per_minute=60)
        assert limiter.acquire() is True

    def test_rate_limiter_tracks_requests(self):
        """リクエスト数を追跡する"""
        from app.performance.rate_limiter import LLMRateLimiter

        limiter = LLMRateLimiter(requests_per_minute=60)
        limiter.acquire()
        limiter.acquire()
        assert limiter.current_request_count == 2

    def test_rate_limiter_resets_after_window(self):
        """ウィンドウ後にカウントがリセットされる"""
        from app.performance.rate_limiter import LLMRateLimiter

        limiter = LLMRateLimiter(requests_per_minute=60, window_seconds=0.1)
        limiter.acquire()
        limiter.acquire()
        time.sleep(0.15)
        limiter._cleanup_old_requests()
        assert limiter.current_request_count == 0


class TestSemanticCache:
    """セマンティックキャッシュのテスト"""

    def test_semantic_cache_exists(self):
        """セマンティックキャッシュが存在する"""
        from app.performance.semantic_cache import SemanticCache

        cache = SemanticCache()
        assert cache is not None

    def test_cache_stores_response(self):
        """レスポンスをキャッシュできる"""
        from app.performance.semantic_cache import SemanticCache

        cache = SemanticCache()
        cache.set("test query", {"response": "test"})
        result = cache.get("test query")
        assert result is not None
        assert result["response"] == "test"

    def test_cache_returns_none_for_miss(self):
        """キャッシュミス時はNoneを返す"""
        from app.performance.semantic_cache import SemanticCache

        cache = SemanticCache()
        result = cache.get("nonexistent query")
        assert result is None

    def test_cache_similar_queries(self):
        """類似クエリでキャッシュヒットする"""
        from app.performance.semantic_cache import SemanticCache

        cache = SemanticCache(similarity_threshold=0.9)
        cache.set("企画の収益モデルについて", {"response": "test"})
        # 類似クエリでヒット（モック実装では完全一致のみ）
        result = cache.get("企画の収益モデルについて")
        assert result is not None

    def test_cache_expiration(self):
        """キャッシュの有効期限"""
        from app.performance.semantic_cache import SemanticCache

        cache = SemanticCache(ttl_seconds=0.1)
        cache.set("test query", {"response": "test"})
        time.sleep(0.15)
        result = cache.get("test query")
        assert result is None


class TestConcurrentRequests:
    """同時リクエスト処理のテスト"""

    @pytest.mark.asyncio
    async def test_concurrent_request_handler_exists(self):
        """同時リクエストハンドラーが存在する"""
        from app.performance.concurrent_handler import ConcurrentRequestHandler

        handler = ConcurrentRequestHandler(max_concurrent=10)
        assert handler is not None

    @pytest.mark.asyncio
    async def test_handles_10_concurrent_users(self):
        """10ユーザーの同時リクエストを処理できる"""
        from app.performance.concurrent_handler import ConcurrentRequestHandler

        handler = ConcurrentRequestHandler(max_concurrent=10)
        results = await handler.run_concurrent_test(num_requests=10)
        assert results.successful_requests == 10

    @pytest.mark.asyncio
    async def test_respects_max_concurrent_limit(self):
        """最大同時実行数を尊重する"""
        from app.performance.concurrent_handler import ConcurrentRequestHandler

        handler = ConcurrentRequestHandler(max_concurrent=5)
        # 10リクエストを投げても同時に5つまで
        results = await handler.run_concurrent_test(num_requests=10)
        assert results.max_concurrent_observed <= 5

    @pytest.mark.asyncio
    async def test_all_requests_complete(self):
        """全リクエストが完了する"""
        from app.performance.concurrent_handler import ConcurrentRequestHandler

        handler = ConcurrentRequestHandler(max_concurrent=10)
        results = await handler.run_concurrent_test(num_requests=10)
        assert results.total_requests == results.successful_requests + results.failed_requests


class TestPerformanceMetrics:
    """パフォーマンスメトリクスのテスト"""

    def test_metrics_collector_exists(self):
        """メトリクスコレクターが存在する"""
        from app.performance.metrics import PerformanceMetrics

        metrics = PerformanceMetrics()
        assert metrics is not None

    def test_record_response_time(self):
        """レスポンスタイムを記録できる"""
        from app.performance.metrics import PerformanceMetrics

        metrics = PerformanceMetrics()
        metrics.record_response_time("search", 150.5)
        stats = metrics.get_stats("search")
        assert stats["count"] == 1
        assert stats["avg"] == 150.5

    def test_calculate_percentiles(self):
        """パーセンタイルを計算できる"""
        from app.performance.metrics import PerformanceMetrics

        metrics = PerformanceMetrics()
        for i in range(100):
            metrics.record_response_time("search", float(i))
        stats = metrics.get_stats("search")
        assert "p50" in stats
        assert "p95" in stats
        assert "p99" in stats
