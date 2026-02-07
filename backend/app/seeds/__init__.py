"""シードデータモジュール"""
from .failure_patterns import MASTER_FAILURE_PATTERNS
from .decision_cases import SAMPLE_DECISION_CASES
from .loader import SeedDataLoader
from .fallback import (
    get_empty_results_message,
    get_fallback_similar_cases,
    get_fallback_questions,
)

__all__ = [
    "MASTER_FAILURE_PATTERNS",
    "SAMPLE_DECISION_CASES",
    "SeedDataLoader",
    "get_empty_results_message",
    "get_fallback_similar_cases",
    "get_fallback_questions",
]
