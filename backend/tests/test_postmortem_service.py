"""
TDD: ポストモーテムサービスのテスト
タスク3.3: ポストモーテムサービスの実装

Design.mdに基づく仕様:
- プロジェクト撤退・中止・ペンディング時に、仮説の崩壊理由と組織内議論を入力するテンプレートを提供
- Go/NoGo判断と理由（1〜3文）の有無を検証し、ケースとアイデアメモを区別して保存
- 失敗パターンタグの候補をLLMで推定し、ユーザーに提示
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.application.postmortem_service import (
    PostmortemService,
    PostmortemTemplate,
    PostmortemSubmission,
    PostmortemResult,
    FailedHypothesis,
    DiscussionRecord,
    ProjectOutcome,
    GoNoGoDecision,
    FailurePatternSuggestion,
)


class TestProjectOutcome:
    """ProjectOutcomeのテスト"""

    def test_project_outcome_values(self):
        """outcome値が正しい"""
        assert ProjectOutcome.WITHDRAWN.value == "withdrawn"
        assert ProjectOutcome.CANCELLED.value == "cancelled"
        assert ProjectOutcome.PENDING.value == "pending"


class TestFailedHypothesis:
    """FailedHypothesisのテスト"""

    def test_failed_hypothesis_has_fields(self):
        """フィールドが含まれる"""
        hypothesis = FailedHypothesis(
            hypothesis="市場は成長する",
            failure_reason="市場調査で否定された",
        )
        assert hypothesis.hypothesis == "市場は成長する"
        assert hypothesis.failure_reason == "市場調査で否定された"


class TestDiscussionRecord:
    """DiscussionRecordのテスト"""

    def test_discussion_record_has_fields(self):
        """フィールドが含まれる"""
        record = DiscussionRecord(
            topic="収益性",
            summary="収益モデルの見直しが必要",
            discussed_at="2024-01-15",
        )
        assert record.topic == "収益性"


class TestPostmortemTemplate:
    """PostmortemTemplateのテスト"""

    def test_postmortem_template_has_sections(self):
        """テンプレートにセクションが含まれる"""
        template = PostmortemTemplate(
            project_id="proj-001",
            sections=[
                {"name": "仮説の検証結果", "description": "どの仮説が崩れたか"},
                {"name": "組織内議論", "description": "どんな議論があったか"},
                {"name": "判断理由", "description": "Go/NoGo判断とその理由"},
            ],
            outcome_options=["withdrawn", "cancelled", "pending"],
        )
        assert template.project_id == "proj-001"
        assert len(template.sections) == 3


class TestPostmortemSubmission:
    """PostmortemSubmissionのテスト"""

    def test_submission_with_decision(self):
        """判断ありの提出"""
        submission = PostmortemSubmission(
            project_id="proj-001",
            outcome=ProjectOutcome.WITHDRAWN,
            decision=GoNoGoDecision(decision="no_go", reason="収益性の懸念"),
            failed_hypotheses=[],
            discussions=[],
        )
        assert submission.decision is not None
        assert submission.decision.decision == "no_go"

    def test_submission_without_decision(self):
        """判断なしの提出（アイデアメモ）"""
        submission = PostmortemSubmission(
            project_id="proj-001",
            outcome=ProjectOutcome.PENDING,
            decision=None,
            failed_hypotheses=[],
            discussions=[],
        )
        assert submission.decision is None


class TestPostmortemResult:
    """PostmortemResultのテスト"""

    def test_result_as_decision_case(self):
        """意思決定ケースとして保存"""
        result = PostmortemResult(
            record_type="decision_case",
            record_id="case-001",
            assigned_patterns=["financial", "market"],
        )
        assert result.record_type == "decision_case"

    def test_result_as_idea_memo(self):
        """アイデアメモとして保存"""
        result = PostmortemResult(
            record_type="idea_memo",
            record_id="memo-001",
            assigned_patterns=[],
        )
        assert result.record_type == "idea_memo"


class TestPostmortemService:
    """PostmortemServiceのテスト"""

    @pytest.fixture
    def mock_case_manager(self):
        """モックCaseManager"""
        with patch("app.application.postmortem_service.CaseManager") as mock:
            yield mock

    @pytest.fixture
    def mock_llm_service(self):
        """モックLLMService"""
        with patch("app.application.postmortem_service.LLMService") as mock:
            yield mock

    @pytest.fixture
    def mock_db_session(self):
        """モックDBセッション"""
        with patch("app.application.postmortem_service.SessionLocal") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_get_template_returns_template(
        self, mock_case_manager, mock_llm_service, mock_db_session
    ):
        """テンプレートを取得"""
        service = PostmortemService()

        template = await service.get_template("proj-001")

        assert template is not None
        assert isinstance(template, PostmortemTemplate)
        assert template.project_id == "proj-001"
        assert len(template.sections) > 0

    @pytest.mark.asyncio
    async def test_submit_with_decision_saves_as_case(
        self, mock_case_manager, mock_llm_service, mock_db_session
    ):
        """判断ありの提出はケースとして保存"""
        from app.domain.case.case_manager import DecisionCase, CaseOutcome
        from datetime import datetime, timezone

        mock_cm = AsyncMock()
        mock_cm.create_case = AsyncMock(
            return_value=DecisionCase(
                id="case-001",
                title="",
                purpose="",
                target_market=None,
                business_model=None,
                outcome=CaseOutcome.WITHDRAWN,
                decision=Mock(decision="no_go", reason="理由"),
                failed_hypotheses=[],
                discussions=[],
                failure_patterns=[],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
        mock_case_manager.return_value = mock_cm

        mock_llm = AsyncMock()
        mock_llm.generate_analysis = AsyncMock(
            return_value={
                "patterns": [
                    {
                        "category": "financial",
                        "name": "収益性の懸念",
                        "confidence": 0.8,
                        "rationale": "テスト理由",
                    }
                ]
            }
        )
        mock_llm_service.return_value = mock_llm

        service = PostmortemService()
        submission = PostmortemSubmission(
            project_id="proj-001",
            outcome=ProjectOutcome.WITHDRAWN,
            decision=GoNoGoDecision(decision="no_go", reason="収益性の懸念"),
            failed_hypotheses=[],
            discussions=[],
        )

        result = await service.submit_postmortem(submission)

        assert result.record_type == "decision_case"
        mock_cm.create_case.assert_called_once()

    @pytest.mark.asyncio
    async def test_submit_without_decision_saves_as_memo(
        self, mock_case_manager, mock_llm_service, mock_db_session
    ):
        """判断なしの提出はメモとして保存"""
        mock_session = Mock()
        mock_db_session.return_value = mock_session

        service = PostmortemService()
        submission = PostmortemSubmission(
            project_id="proj-001",
            outcome=ProjectOutcome.PENDING,
            decision=None,
            failed_hypotheses=[],
            discussions=[],
        )

        result = await service.submit_postmortem(submission)

        assert result.record_type == "idea_memo"

    @pytest.mark.asyncio
    async def test_suggest_failure_patterns(
        self, mock_case_manager, mock_llm_service, mock_db_session
    ):
        """失敗パターンを推定"""
        mock_llm = AsyncMock()
        mock_llm.generate_analysis = AsyncMock(
            return_value={
                "patterns": [
                    {
                        "category": "market",
                        "name": "市場規模の誤認",
                        "confidence": 0.85,
                        "rationale": "市場調査不足による誤認",
                    },
                    {
                        "category": "financial",
                        "name": "収益性の過大評価",
                        "confidence": 0.7,
                        "rationale": "コスト見積もりの甘さ",
                    },
                ]
            }
        )
        mock_llm_service.return_value = mock_llm

        service = PostmortemService()
        submission = PostmortemSubmission(
            project_id="proj-001",
            outcome=ProjectOutcome.WITHDRAWN,
            decision=GoNoGoDecision(decision="no_go", reason="市場が小さかった"),
            failed_hypotheses=[
                FailedHypothesis(
                    hypothesis="市場は十分大きい",
                    failure_reason="実際は小さかった",
                )
            ],
            discussions=[],
        )

        suggestions = await service.suggest_failure_patterns(submission)

        assert len(suggestions) == 2
        assert suggestions[0].category == "market"
        assert suggestions[0].confidence == 0.85
