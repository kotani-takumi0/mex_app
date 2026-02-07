"""
TDD: 問い生成エンジンのテスト
タスク2.5: 問い生成エンジンの実装

Design.mdに基づく仕様:
- 類似ケースと失敗パターンに基づき、企画の質を向上させるための「問い」を生成
- LLM（GPT-4/Claude）APIを呼び出し
- 生成された問いをカテゴリ（財務、オペレーション、市場、技術、組織）に分類
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.domain.question.question_generator import (
    QuestionGenerator,
    QuestionGenInput,
    GeneratedQuestion,
    QuestionCategory,
    DraftContext,
)


class TestQuestionCategory:
    """QuestionCategoryのテスト"""

    def test_question_category_values(self):
        """カテゴリ値が正しい"""
        assert QuestionCategory.FINANCIAL.value == "financial"
        assert QuestionCategory.OPERATIONAL.value == "operational"
        assert QuestionCategory.MARKET.value == "market"
        assert QuestionCategory.TECHNICAL.value == "technical"
        assert QuestionCategory.ORGANIZATIONAL.value == "organizational"


class TestDraftContext:
    """DraftContextのテスト"""

    def test_draft_context_has_fields(self):
        """必須フィールドが含まれる"""
        context = DraftContext(
            purpose="新規事業の立ち上げ",
            target_market="日本市場",
            business_model="SaaSモデル",
        )
        assert context.purpose == "新規事業の立ち上げ"
        assert context.target_market == "日本市場"


class TestGeneratedQuestion:
    """GeneratedQuestionのテスト"""

    def test_generated_question_has_required_fields(self):
        """必須フィールドが含まれる"""
        question = GeneratedQuestion(
            id="q-001",
            question="収益性をどのように確保しますか？",
            rationale="過去の類似案件で収益性が課題になった",
            related_case_ids=["case-001"],
            related_patterns=["financial"],
            category=QuestionCategory.FINANCIAL,
        )
        assert question.id == "q-001"
        assert question.question == "収益性をどのように確保しますか？"
        assert question.category == QuestionCategory.FINANCIAL


class TestQuestionGenInput:
    """QuestionGenInputのテスト"""

    def test_question_gen_input(self):
        """入力データが正しく作成できる"""
        context = DraftContext(
            purpose="目的",
            target_market="市場",
            business_model="モデル",
        )
        input_data = QuestionGenInput(
            draft_context=context,
            similar_cases=[],
            failure_patterns=["market"],
            question_count=5,
        )
        assert input_data.question_count == 5


class TestQuestionGenerator:
    """QuestionGeneratorのテスト"""

    @pytest.fixture
    def mock_llm_service(self):
        """モックLLMサービス"""
        with patch("app.domain.question.question_generator.LLMService") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_generate_questions_returns_list(self, mock_llm_service):
        """問いリストを生成"""
        mock_llm = AsyncMock()
        mock_llm.generate_analysis = AsyncMock(
            return_value={
                "questions": [
                    {
                        "question": "収益性をどのように確保しますか？",
                        "rationale": "過去の類似案件で課題",
                        "category": "financial",
                        "related_cases": ["c1"],
                        "related_patterns": ["financial"],
                    },
                    {
                        "question": "市場規模は十分ですか？",
                        "rationale": "市場調査が不足していた",
                        "category": "market",
                        "related_cases": ["c2"],
                        "related_patterns": ["market"],
                    },
                ]
            }
        )
        mock_llm_service.return_value = mock_llm

        generator = QuestionGenerator()
        context = DraftContext(
            purpose="新規事業",
            target_market="日本",
            business_model="SaaS",
        )
        input_data = QuestionGenInput(
            draft_context=context,
            similar_cases=[],
            failure_patterns=["financial", "market"],
            question_count=5,
        )

        questions = await generator.generate_questions(input_data)

        assert len(questions) == 2
        assert questions[0].category == QuestionCategory.FINANCIAL

    @pytest.mark.asyncio
    async def test_generate_questions_assigns_ids(self, mock_llm_service):
        """生成された問いにIDが割り当てられる"""
        mock_llm = AsyncMock()
        mock_llm.generate_analysis = AsyncMock(
            return_value={
                "questions": [
                    {
                        "question": "テスト問い",
                        "rationale": "理由",
                        "category": "market",
                        "related_cases": [],
                        "related_patterns": [],
                    }
                ]
            }
        )
        mock_llm_service.return_value = mock_llm

        generator = QuestionGenerator()
        context = DraftContext(
            purpose="目的",
            target_market="市場",
            business_model="モデル",
        )
        input_data = QuestionGenInput(
            draft_context=context,
            similar_cases=[],
            failure_patterns=[],
            question_count=1,
        )

        questions = await generator.generate_questions(input_data)

        assert questions[0].id is not None
        assert questions[0].id.startswith("q-")

    @pytest.mark.asyncio
    async def test_generate_questions_with_similar_cases(self, mock_llm_service):
        """類似ケースを考慮して問いを生成"""
        from app.domain.case.case_manager import SimilarCase, CaseOutcome

        mock_llm = AsyncMock()
        mock_llm.generate_analysis = AsyncMock(
            return_value={
                "questions": [
                    {
                        "question": "オペレーション体制は十分ですか？",
                        "rationale": "過去ケースで体制不備が指摘された",
                        "category": "operational",
                        "related_cases": ["c1"],
                        "related_patterns": ["operational"],
                    }
                ]
            }
        )
        mock_llm_service.return_value = mock_llm

        generator = QuestionGenerator()
        similar_cases = [
            SimilarCase(
                case_id="c1",
                title="過去案件",
                purpose="同様の目的",
                outcome=CaseOutcome.REJECTED,
                score=0.9,
                matched_segments=["オペレーション体制の不備"],
            )
        ]
        context = DraftContext(
            purpose="新規事業",
            target_market="日本",
            business_model="SaaS",
        )
        input_data = QuestionGenInput(
            draft_context=context,
            similar_cases=similar_cases,
            failure_patterns=["operational"],
            question_count=3,
        )

        questions = await generator.generate_questions(input_data)

        # 類似ケースの情報がプロンプトに含まれていることを確認
        mock_llm.generate_analysis.assert_called_once()
        call_args = mock_llm.generate_analysis.call_args[0][0]
        assert "過去案件" in call_args or "c1" in call_args
