"""
TDD: ゲートレビュー支援サービスのテスト
タスク3.2: ゲートレビュー支援サービスの実装

Design.mdに基づく仕様:
- 案件フェーズと仮説状況に基づき、会議のアジェンダ候補を自動生成
- 過去の類似案件で「なぜ採用/不採用になったか」の主要因を検索・表示
- 論点候補リストを整理し、会議前に参照可能な形式で出力
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from app.application.gate_review_service import (
    GateReviewService,
    AgendaRequest,
    AgendaResponse,
    AgendaItem,
    DiscussionPoint,
    DecisionReasonSearchRequest,
    DecisionReason,
    HypothesisStatus,
)
from app.domain.pattern.pattern_analyzer import ProjectPhase


class TestAgendaRequest:
    """AgendaRequestのテスト"""

    def test_agenda_request_has_required_fields(self):
        """必須フィールドが含まれる"""
        request = AgendaRequest(
            project_id="proj-001",
            current_phase=ProjectPhase.VALIDATION,
            hypothesis_status=[
                HypothesisStatus(
                    hypothesis="仮説1",
                    status="verified",
                    confidence=0.8,
                )
            ],
        )
        assert request.project_id == "proj-001"
        assert request.current_phase == ProjectPhase.VALIDATION


class TestAgendaItem:
    """AgendaItemのテスト"""

    def test_agenda_item_has_fields(self):
        """アジェンダ項目のフィールド"""
        item = AgendaItem(
            title="収益性の検証",
            description="収益モデルの妥当性を確認",
            priority=1,
            related_case_ids=["c1", "c2"],
            suggested_duration_minutes=15,
        )
        assert item.title == "収益性の検証"
        assert item.priority == 1


class TestDiscussionPoint:
    """DiscussionPointのテスト"""

    def test_discussion_point_has_fields(self):
        """論点のフィールド"""
        point = DiscussionPoint(
            topic="市場規模",
            key_questions=["市場は十分か？", "成長性は？"],
            historical_context="過去3件で議論された",
            recommended_outcome="合意形成",
        )
        assert point.topic == "市場規模"
        assert len(point.key_questions) == 2


class TestDecisionReason:
    """DecisionReasonのテスト"""

    def test_decision_reason_has_fields(self):
        """判断理由のフィールド"""
        reason = DecisionReason(
            case_id="c1",
            case_title="過去案件",
            decision="no_go",
            primary_reason="収益性の懸念",
            contributing_factors=["市場規模", "競合"],
            relevance_score=0.85,
        )
        assert reason.case_id == "c1"
        assert reason.decision == "no_go"


class TestGateReviewService:
    """GateReviewServiceのテスト"""

    @pytest.fixture
    def mock_case_manager(self):
        """モックCaseManager"""
        with patch("app.application.gate_review_service.CaseManager") as mock:
            yield mock

    @pytest.fixture
    def mock_pattern_analyzer(self):
        """モックPatternAnalyzer"""
        with patch("app.application.gate_review_service.PatternAnalyzer") as mock:
            yield mock

    @pytest.fixture
    def mock_llm_service(self):
        """モックLLMService"""
        with patch("app.application.gate_review_service.LLMService") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_generate_agenda_returns_response(
        self, mock_case_manager, mock_pattern_analyzer, mock_llm_service
    ):
        """アジェンダ生成がレスポンスを返す"""
        from app.domain.case.case_manager import SimilarCase, CaseOutcome
        from app.domain.pattern.pattern_analyzer import BottleneckAnalysis

        mock_cm = AsyncMock()
        mock_cm.find_similar_cases = AsyncMock(
            return_value=[
                SimilarCase(
                    case_id="c1",
                    title="過去案件",
                    purpose="目的",
                    outcome=CaseOutcome.REJECTED,
                    score=0.9,
                    matched_segments=[],
                )
            ]
        )
        mock_case_manager.return_value = mock_cm

        mock_pa = AsyncMock()
        mock_pa.analyze_phase_bottlenecks = AsyncMock(
            return_value=BottleneckAnalysis(
                phase=ProjectPhase.VALIDATION,
                key_bottlenecks=["仮説検証不足"],
                historical_frequency=0.7,
                recommended_focus_areas=["ユーザーリサーチ"],
            )
        )
        mock_pattern_analyzer.return_value = mock_pa

        mock_llm = AsyncMock()
        mock_llm.generate_analysis = AsyncMock(
            return_value={
                "agenda_items": [
                    {
                        "title": "仮説検証状況の確認",
                        "description": "検証済み仮説のレビュー",
                        "priority": 1,
                        "duration": 15,
                    }
                ],
                "discussion_points": [
                    {
                        "topic": "市場検証",
                        "questions": ["市場規模は？"],
                        "context": "過去に問題となった",
                        "outcome": "合意",
                    }
                ],
            }
        )
        mock_llm_service.return_value = mock_llm

        service = GateReviewService()
        request = AgendaRequest(
            project_id="proj-001",
            current_phase=ProjectPhase.VALIDATION,
            hypothesis_status=[],
        )

        response = await service.generate_agenda(request)

        assert response is not None
        assert isinstance(response, AgendaResponse)
        assert len(response.agenda_items) >= 1

    @pytest.mark.asyncio
    async def test_search_decision_reasons(
        self, mock_case_manager, mock_pattern_analyzer, mock_llm_service
    ):
        """判断理由を検索"""
        from app.domain.case.case_manager import SimilarCase, CaseOutcome

        mock_cm = AsyncMock()
        mock_cm.find_similar_cases = AsyncMock(
            return_value=[
                SimilarCase(
                    case_id="c1",
                    title="却下案件",
                    purpose="目的",
                    outcome=CaseOutcome.REJECTED,
                    score=0.9,
                    matched_segments=["収益性"],
                )
            ]
        )
        mock_cm.get_case_by_id = AsyncMock(
            return_value=Mock(
                id="c1",
                title="却下案件",
                decision=Mock(decision="no_go", reason="収益性の懸念"),
            )
        )
        mock_case_manager.return_value = mock_cm

        service = GateReviewService()
        request = DecisionReasonSearchRequest(
            query="収益性",
            limit=5,
        )

        reasons = await service.search_decision_reasons(request)

        assert len(reasons) >= 1
        assert reasons[0].case_id == "c1"
