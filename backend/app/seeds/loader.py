"""
シードデータローダー
タスク6.2: サンプルデータ投入とコールドスタート対応
"""

import uuid
from datetime import datetime
from typing import Any

from .decision_cases import SAMPLE_DECISION_CASES
from .failure_patterns import MASTER_FAILURE_PATTERNS


class SeedDataLoader:
    """シードデータローダー"""

    def __init__(self):
        self._loaded_patterns: list[dict] = []
        self._loaded_cases: list[dict] = []

    def load_failure_patterns(self) -> list[dict]:
        """
        失敗パターンマスターデータを読み込む

        Returns:
            失敗パターンのリスト（IDを付与）
        """
        self._loaded_patterns = []
        for pattern in MASTER_FAILURE_PATTERNS:
            loaded = {
                "id": str(uuid.uuid4()),
                "name": pattern["name"],
                "description": pattern["description"],
                "category": pattern["category"],
                "created_at": datetime.now().isoformat(),
            }
            self._loaded_patterns.append(loaded)
        return self._loaded_patterns

    def load_decision_cases(self) -> list[dict]:
        """
        サンプル意思決定ケースを読み込む

        Returns:
            意思決定ケースのリスト（IDを付与）
        """
        self._loaded_cases = []
        for case in SAMPLE_DECISION_CASES:
            loaded = {
                "id": str(uuid.uuid4()),
                "title": case["title"],
                "purpose": case["purpose"],
                "target_market": case["target_market"],
                "business_model": case["business_model"],
                "outcome": case["outcome"],
                "decision_type": case["decision_type"],
                "decision_reason": case["decision_reason"],
                "failed_hypotheses": case.get("failed_hypotheses", []),
                "discussions": case.get("discussions", []),
                "failure_patterns": case.get("failure_patterns", []),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            self._loaded_cases.append(loaded)
        return self._loaded_cases

    def get_loaded_patterns(self) -> list[dict]:
        """読み込み済みパターンを取得"""
        return self._loaded_patterns

    def get_loaded_cases(self) -> list[dict]:
        """読み込み済みケースを取得"""
        return self._loaded_cases

    async def seed_to_database(self, db_session: Any) -> dict:
        """
        データベースにシードデータを投入

        Args:
            db_session: データベースセッション

        Returns:
            投入結果（件数など）
        """
        patterns = self.load_failure_patterns()
        cases = self.load_decision_cases()

        # 実際のDB投入は呼び出し側で実装
        return {
            "patterns_count": len(patterns),
            "cases_count": len(cases),
            "status": "prepared",
        }
