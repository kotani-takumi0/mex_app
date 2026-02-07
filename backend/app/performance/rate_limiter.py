"""
LLM APIレートリミッター
タスク6.3: パフォーマンス検証と最適化
"""
import time
from collections import deque
from threading import Lock


class LLMRateLimiter:
    """LLM APIのレートリミッター"""

    def __init__(
        self,
        requests_per_minute: int = 60,
        window_seconds: float = 60.0,
    ):
        """
        Args:
            requests_per_minute: 1分あたりの最大リクエスト数
            window_seconds: ウィンドウサイズ（秒）
        """
        self.requests_per_minute = requests_per_minute
        self.window_seconds = window_seconds
        self._requests: deque = deque()
        self._lock = Lock()

    @property
    def current_request_count(self) -> int:
        """現在のウィンドウ内のリクエスト数"""
        self._cleanup_old_requests()
        return len(self._requests)

    def _cleanup_old_requests(self) -> None:
        """古いリクエストを削除"""
        current_time = time.time()
        with self._lock:
            while self._requests and (current_time - self._requests[0]) > self.window_seconds:
                self._requests.popleft()

    def acquire(self) -> bool:
        """
        リクエスト許可を取得

        Returns:
            True: 許可された
            False: レート制限により拒否
        """
        self._cleanup_old_requests()

        with self._lock:
            if len(self._requests) >= self.requests_per_minute:
                return False

            self._requests.append(time.time())
            return True

    def wait_and_acquire(self, timeout: float = 60.0) -> bool:
        """
        許可が得られるまで待機

        Args:
            timeout: 最大待機時間（秒）

        Returns:
            True: 許可された
            False: タイムアウト
        """
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            if self.acquire():
                return True
            time.sleep(0.1)

        return False

    def get_wait_time(self) -> float:
        """
        次のリクエストまでの待機時間を取得

        Returns:
            待機時間（秒）、即座に実行可能な場合は0
        """
        self._cleanup_old_requests()

        with self._lock:
            if len(self._requests) < self.requests_per_minute:
                return 0.0

            oldest = self._requests[0]
            return max(0, self.window_seconds - (time.time() - oldest))
