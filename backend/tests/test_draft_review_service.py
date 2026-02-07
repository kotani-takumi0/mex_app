"""
TDD: 企画ドラフトレビューサービスのテスト
タスク3.1: 企画ドラフトレビューサービスの実装

Design.mdに基づく仕様:
- 企画ドラフト情報を受け取り、類似ケース検索と問い生成をオーケストレーション
- 採用案と没案の両方を提示
- 論点・懸念点を要約して返却
- レビュー進捗管理機能
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from app.application.draft_review_service import (
    DraftReviewService,
    DraftReviewRequest,
    DraftReviewResponse,
    ReviewProgress,
    AnswerProgressUpdate,
)


class TestDraftReviewRequest:
    """DraftReviewRequestのテスト"""

    def test_request_has_required_fields(self):
        """必須フィールドが含まれる"""
        request = DraftReviewRequest(
            draft_id="draft-001",
            purpose="新規事業の立ち上げ",
            target_market="日本市場",
            business_model="SaaSモデル",
        )
        assert request.draft_id == "draft-001"
        assert request.purpose == "新規事業の立ち上げ"

    def test_request_with_optional_fields(self):
        """オプションフィールドが設定できる"""
        request = DraftReviewRequest(
            draft_id="draft-001",
            purpose="目的",
            target_market="市場",
            business_model="モデル",
            additional_context="追加コンテキスト",
        )
        assert request.additional_context == "追加コンテキスト"


class TestDraftReviewResponse:
    """DraftReviewResponseのテスト"""

    def test_response_has_required_fields(self):
        """必須フィールドが含まれる"""
        from app.domain.case.case_manager import SimilarCase, CaseOutcome
        from app.domain.pattern.pattern_analyzer import ConcernPoint
        from app.domain.question.question_generator import GeneratedQuestion, QuestionCategory

        response = DraftReviewResponse(
            similar_cases=[
                SimilarCase(
                    case_id="c1",
                    title="ケース1",
                    purpose="目的",
                    outcome=CaseOutcome.REJECTED,
                    score=0.9,
                    matched_segments=[],
                )
            ],
            concern_points=[
                ConcernPoint(
                    category="financial",
                    summary="収益性の懸念",
                    frequency=3,
                    related_case_ids=["c1"],
                )
            ],
            questions=[
                GeneratedQuestion(
                    id="q1",
                    question="収益性は？",
                    rationale="過去の事例",
                    related_case_ids=["c1"],
                    related_patterns=["financial"],
                    category=QuestionCategory.FINANCIAL,
                )
            ],
            review_progress=ReviewProgress(
                total_questions=1,
                answered_questions=0,
                unanswered_question_ids=["q1"],
            ),
        )
        assert len(response.similar_cases) == 1
        assert len(response.questions) == 1


class TestReviewProgress:
    """ReviewProgressのテスト"""

    def test_review_progress_tracking(self):
        """進捗追跡が正しく動作する"""
        progress = ReviewProgress(
            total_questions=5,
            answered_questions=2,
            unanswered_question_ids=["q3", "q4", "q5"],
        )
        assert progress.total_questions == 5
        assert progress.answered_questions == 2
        assert len(progress.unanswered_question_ids) == 3


class TestDraftReviewService:
    """DraftReviewServiceのテスト"""

    @pytest.fixture
    def mock_case_manager(self):
        """モックCaseManager"""
        with patch("app.application.draft_review_service.CaseManager") as mock:
            yield mock

    @pytest.fixture
    def mock_pattern_analyzer(self):
        """モックPatternAnalyzer"""
        with patch("app.application.draft_review_service.PatternAnalyzer") as mock:
            yield mock

    @pytest.fixture
    def mock_question_generator(self):
        """モックQuestionGenerator"""
        with patch("app.application.draft_review_service.QuestionGenerator") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_review_draft_returns_response(
        self, mock_case_manager, mock_pattern_analyzer, mock_question_generator
    ):
        """ドラフトレビューがレスポンスを返す"""
        from app.domain.case.case_manager import SimilarCase, CaseOutcome
        from app.domain.pattern.pattern_analyzer import PatternSummary, ConcernPoint
        from app.domain.question.question_generator import GeneratedQuestion, QuestionCategory

        # CaseManagerのモック
        mock_cm = AsyncMock()
        mock_cm.find_similar_cases = AsyncMock(
            return_value=[
                SimilarCase(
                    case_id="c1",
                    title="過去案件",
                    purpose="目的",
                    outcome=CaseOutcome.REJECTED,
                    score=0.9,
                    matched_segments=["財務面"],
                )
            ]
        )
        mock_case_manager.return_value = mock_cm

        # PatternAnalyzerのモック
        mock_pa = AsyncMock()
        mock_pa.extract_concern_points = AsyncMock(
            return_value=PatternSummary(
                concern_points=[
                    ConcernPoint(
                        category="financial",
                        summary="収益性懸念",
                        frequency=1,
                        related_case_ids=["c1"],
                    )
                ],
                overall_summary="全体要約",
            )
        )
        mock_pattern_analyzer.return_value = mock_pa

        # QuestionGeneratorのモック
        mock_qg = AsyncMock()
        mock_qg.generate_questions = AsyncMock(
            return_value=[
                GeneratedQuestion(
                    id="q1",
                    question="収益性は？",
                    rationale="理由",
                    related_case_ids=["c1"],
                    related_patterns=["financial"],
                    category=QuestionCategory.FINANCIAL,
                )
            ]
        )
        mock_question_generator.return_value = mock_qg

        service = DraftReviewService()
        request = DraftReviewRequest(
            draft_id="draft-001",
            purpose="新規事業",
            target_market="日本",
            business_model="SaaS",
        )

        response = await service.review_draft(request)

        assert response is not None
        assert isinstance(response, DraftReviewResponse)
        assert len(response.similar_cases) == 1
        assert len(response.questions) == 1

    @pytest.mark.asyncio
    async def test_review_draft_separates_adopted_and_rejected(
        self, mock_case_manager, mock_pattern_analyzer, mock_question_generator
    ):
        """採用案と没案の両方を返す"""
        from app.domain.case.case_manager import SimilarCase, CaseOutcome
        from app.domain.pattern.pattern_analyzer import PatternSummary
        from app.domain.question.question_generator import GeneratedQuestion, QuestionCategory

        mock_cm = AsyncMock()
        mock_cm.find_similar_cases = AsyncMock(
            return_value=[
                SimilarCase(
                    case_id="c1",
                    title="採用案件",
                    purpose="目的",
                    outcome=CaseOutcome.ADOPTED,
                    score=0.9,
                    matched_segments=[],
                ),
                SimilarCase(
                    case_id="c2",
                    title="却下案件",
                    purpose="目的",
                    outcome=CaseOutcome.REJECTED,
                    score=0.8,
                    matched_segments=[],
                ),
            ]
        )
        mock_case_manager.return_value = mock_cm

        mock_pa = AsyncMock()
        mock_pa.extract_concern_points = AsyncMock(
            return_value=PatternSummary(concern_points=[], overall_summary="")
        )
        mock_pattern_analyzer.return_value = mock_pa

        mock_qg = AsyncMock()
        mock_qg.generate_questions = AsyncMock(return_value=[])
        mock_question_generator.return_value = mock_qg

        service = DraftReviewService()
        request = DraftReviewRequest(
            draft_id="draft-001",
            purpose="目的",
            target_market="市場",
            business_model="モデル",
        )

        response = await service.review_draft(request)

        # 採用案と没案の両方が含まれる
        outcomes = [c.outcome for c in response.similar_cases]
        assert CaseOutcome.ADOPTED in outcomes
        assert CaseOutcome.REJECTED in outcomes


class TestAnswerProgressUpdate:
    """AnswerProgressUpdateのテスト"""

    def test_answer_progress_update(self):
        """回答進捗更新データ"""
        update = AnswerProgressUpdate(
            draft_id="draft-001",
            question_id="q1",
            answer="回答内容",
        )
        assert update.draft_id == "draft-001"
        assert update.question_id == "q1"
        assert update.answer == "回答内容"


class TestDraftReviewServiceProgressTracking:
    """レビュー進捗管理のテスト"""

    @pytest.fixture
    def mock_dependencies(self):
        """全依存関係のモック"""
        with patch("app.application.draft_review_service.CaseManager") as cm, \
             patch("app.application.draft_review_service.PatternAnalyzer") as pa, \
             patch("app.application.draft_review_service.QuestionGenerator") as qg:
            yield cm, pa, qg

    @pytest.mark.asyncio
    async def test_update_answer_progress(self, mock_dependencies):
        """回答進捗を更新"""
        service = DraftReviewService()

        # 初期状態を設定
        service._review_states["draft-001"] = {
            "questions": {"q1": None, "q2": None, "q3": None},
        }

        update = AnswerProgressUpdate(
            draft_id="draft-001",
            question_id="q1",
            answer="回答内容",
        )

        progress = await service.update_answer_progress(update)

        assert progress.answered_questions == 1
        assert progress.total_questions == 3
        assert "q1" not in progress.unanswered_question_ids

    @pytest.mark.asyncio
    async def test_get_review_progress(self, mock_dependencies):
        """レビュー進捗を取得"""
        service = DraftReviewService()

        # 状態を設定
        service._review_states["draft-001"] = {
            "questions": {"q1": "回答1", "q2": None, "q3": None},
        }

        progress = await service.get_review_progress("draft-001")

        assert progress.total_questions == 3
        assert progress.answered_questions == 1
        assert len(progress.unanswered_question_ids) == 2
