"""
TDD: 失敗パターン分析エンジンのテスト
タスク2.4: 失敗パターン分析エンジンの実装

Design.mdに基づく仕様:
- 過去の意思決定ケースから論点・懸念点を抽出
- カテゴリ別に要約
- プロジェクトフェーズに基づいてボトルネックとなった論点を特定
- LLMを活用したパターン要約生成
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

from app.domain.pattern.pattern_analyzer import (
    PatternAnalyzer,
    PatternSummary,
    ConcernPoint,
    ProjectPhase,
    BottleneckAnalysis,
)


class TestConcernPoint:
    """ConcernPointのテスト"""

    def test_concern_point_has_required_fields(self):
        """必須フィールドが含まれる"""
        point = ConcernPoint(
            category="financial",
            summary="収益性に関する懸念",
            frequency=5,
            related_case_ids=["case-001", "case-002"],
        )
        assert point.category == "financial"
        assert point.summary == "収益性に関する懸念"
        assert point.frequency == 5


class TestPatternSummary:
    """PatternSummaryのテスト"""

    def test_pattern_summary_has_concern_points(self):
        """懸念点リストが含まれる"""
        summary = PatternSummary(
            concern_points=[
                ConcernPoint(
                    category="market",
                    summary="市場規模の懸念",
                    frequency=3,
                    related_case_ids=["c1"],
                )
            ],
            overall_summary="全体的な要約",
        )
        assert len(summary.concern_points) == 1
        assert summary.overall_summary == "全体的な要約"


class TestProjectPhase:
    """ProjectPhaseのテスト"""

    def test_project_phase_values(self):
        """フェーズ値が正しい"""
        assert ProjectPhase.IDEATION.value == "ideation"
        assert ProjectPhase.VALIDATION.value == "validation"
        assert ProjectPhase.DEVELOPMENT.value == "development"
        assert ProjectPhase.LAUNCH.value == "launch"


class TestBottleneckAnalysis:
    """BottleneckAnalysisのテスト"""

    def test_bottleneck_analysis_has_fields(self):
        """必須フィールドが含まれる"""
        analysis = BottleneckAnalysis(
            phase=ProjectPhase.VALIDATION,
            key_bottlenecks=["仮説検証の不足"],
            historical_frequency=0.7,
            recommended_focus_areas=["ユーザーインタビュー"],
        )
        assert analysis.phase == ProjectPhase.VALIDATION
        assert "仮説検証の不足" in analysis.key_bottlenecks


class TestPatternAnalyzer:
    """PatternAnalyzerのテスト"""

    @pytest.fixture
    def mock_case_manager(self):
        """モックCaseManager"""
        with patch("app.domain.pattern.pattern_analyzer.CaseManager") as mock:
            yield mock

    @pytest.fixture
    def mock_llm_service(self):
        """モックLLMサービス"""
        with patch("app.domain.pattern.pattern_analyzer.LLMService") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_extract_concern_points(self, mock_case_manager, mock_llm_service):
        """懸念点を抽出"""
        from app.domain.case.case_manager import SimilarCase, CaseOutcome

        mock_manager = AsyncMock()
        mock_manager.find_similar_cases = AsyncMock(
            return_value=[
                SimilarCase(
                    case_id="c1",
                    title="ケース1",
                    purpose="目的1",
                    outcome=CaseOutcome.REJECTED,
                    score=0.9,
                    matched_segments=["財務面の懸念"],
                )
            ]
        )
        mock_case_manager.return_value = mock_manager

        mock_llm = AsyncMock()
        mock_llm.generate_summary = AsyncMock(
            return_value="財務面での収益性に懸念があります"
        )
        mock_llm_service.return_value = mock_llm

        analyzer = PatternAnalyzer()
        summary = await analyzer.extract_concern_points(
            similar_cases=[
                SimilarCase(
                    case_id="c1",
                    title="ケース1",
                    purpose="目的1",
                    outcome=CaseOutcome.REJECTED,
                    score=0.9,
                    matched_segments=["財務面の懸念"],
                )
            ]
        )

        assert summary is not None
        assert isinstance(summary, PatternSummary)

    @pytest.mark.asyncio
    async def test_analyze_phase_bottlenecks(self, mock_case_manager, mock_llm_service):
        """フェーズ別ボトルネック分析"""
        mock_manager = AsyncMock()
        mock_case_manager.return_value = mock_manager

        mock_llm = AsyncMock()
        mock_llm.generate_analysis = AsyncMock(
            return_value={
                "bottlenecks": ["仮説検証不足"],
                "focus_areas": ["ユーザーリサーチ"],
            }
        )
        mock_llm_service.return_value = mock_llm

        analyzer = PatternAnalyzer()
        analysis = await analyzer.analyze_phase_bottlenecks(
            phase=ProjectPhase.VALIDATION
        )

        assert analysis is not None
        assert analysis.phase == ProjectPhase.VALIDATION

    @pytest.mark.asyncio
    async def test_generate_pattern_summary_with_llm(
        self, mock_case_manager, mock_llm_service
    ):
        """LLMを使用したパターン要約生成"""
        mock_llm = AsyncMock()
        mock_llm.generate_summary = AsyncMock(
            return_value="過去の失敗パターンから、市場規模の誤認が主な原因です"
        )
        mock_llm_service.return_value = mock_llm

        analyzer = PatternAnalyzer()
        summary = await analyzer.generate_pattern_summary(
            failure_patterns=["market", "financial"],
            context="新規事業企画",
        )

        assert summary is not None
        mock_llm.generate_summary.assert_called()
