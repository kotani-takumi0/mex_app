"""
同時リクエストハンドラー
タスク6.3: パフォーマンス検証と最適化
"""
import asyncio
import time
import random
from dataclasses import dataclass
from typing import Any, Callable, Awaitable


@dataclass
class ConcurrentTestResult:
    """同時リクエストテスト結果"""

    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    max_concurrent_observed: int
    total_time_ms: float


class ConcurrentRequestHandler:
    """同時リクエストハンドラー"""

    def __init__(self, max_concurrent: int = 10):
        """
        Args:
            max_concurrent: 最大同時実行数
        """
        self.max_concurrent = max_concurrent
        self._semaphore: asyncio.Semaphore | None = None
        self._current_concurrent = 0
        self._max_observed = 0
        self._lock = asyncio.Lock()

    async def _track_concurrent(self) -> None:
        """同時実行数を追跡"""
        async with self._lock:
            self._current_concurrent += 1
            if self._current_concurrent > self._max_observed:
                self._max_observed = self._current_concurrent

    async def _untrack_concurrent(self) -> None:
        """同時実行数を減らす"""
        async with self._lock:
            self._current_concurrent -= 1

    async def _mock_request(self, request_id: int) -> dict:
        """
        モックリクエスト処理

        Args:
            request_id: リクエストID

        Returns:
            処理結果
        """
        await self._track_concurrent()
        try:
            # 処理をシミュレート（10-50ms）
            await asyncio.sleep(random.uniform(0.01, 0.05))
            return {
                "request_id": request_id,
                "status": "success",
            }
        finally:
            await self._untrack_concurrent()

    async def execute_with_limit(
        self,
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        同時実行数制限付きで関数を実行

        Args:
            func: 実行する非同期関数
            *args: 位置引数
            **kwargs: キーワード引数

        Returns:
            関数の戻り値
        """
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)

        async with self._semaphore:
            return await func(*args, **kwargs)

    async def run_concurrent_test(
        self,
        num_requests: int = 10,
    ) -> ConcurrentTestResult:
        """
        同時リクエストテストを実行

        Args:
            num_requests: リクエスト数

        Returns:
            テスト結果
        """
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        self._current_concurrent = 0
        self._max_observed = 0

        start_time = time.time()
        response_times: list[float] = []
        successful = 0
        failed = 0

        async def run_single_request(request_id: int) -> None:
            nonlocal successful, failed
            req_start = time.time()
            try:
                async with self._semaphore:
                    await self._mock_request(request_id)
                elapsed = (time.time() - req_start) * 1000
                response_times.append(elapsed)
                successful += 1
            except Exception:
                failed += 1

        # 全リクエストを同時に開始
        tasks = [run_single_request(i) for i in range(num_requests)]
        await asyncio.gather(*tasks)

        total_time = (time.time() - start_time) * 1000

        return ConcurrentTestResult(
            total_requests=num_requests,
            successful_requests=successful,
            failed_requests=failed,
            avg_response_time_ms=sum(response_times) / len(response_times) if response_times else 0,
            max_concurrent_observed=self._max_observed,
            total_time_ms=total_time,
        )
