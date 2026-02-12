"""シードデータモジュール"""

from .decision_cases import SAMPLE_DECISION_CASES
from .failure_patterns import MASTER_FAILURE_PATTERNS
from .fallback import (
    get_empty_results_message,
    get_fallback_questions,
    get_fallback_similar_cases,
)
from .loader import SeedDataLoader

__all__ = [
    "MASTER_FAILURE_PATTERNS",
    "SAMPLE_DECISION_CASES",
    "SeedDataLoader",
    "get_empty_results_message",
    "get_fallback_similar_cases",
    "get_fallback_questions",
]
