"""
企画ドラフトレビューサービス
タスク3.1: 企画ドラフトレビューサービスの実装

Design.mdに基づく仕様:
- 企画ドラフト情報を受け取り、類似ケース検索と問い生成をオーケストレーション
- 採用案と没案の両方を提示
- 論点・懸念点を要約して返却
- レビュー進捗管理機能
"""
from dataclasses import dataclass, field
from typing import Any

from app.domain.case.case_manager import CaseManager, SimilarCase
from app.domain.pattern.pattern_analyzer import PatternAnalyzer, ConcernPoint
from app.domain.question.question_generator import (
    QuestionGenerator,
    QuestionGenInput,
    GeneratedQuestion,
    DraftContext,
)


@dataclass
class DraftReviewRequest:
    """ドラフトレビューリクエスト"""
    draft_id: str
    purpose: str
    target_market: str
    business_model: str
    additional_context: str | None = None


@dataclass
class ReviewProgress:
    """レビュー進捗"""
    total_questions: int
    answered_questions: int
    unanswered_question_ids: list[str]


@dataclass
class DraftReviewResponse:
    """ドラフトレビューレスポンス"""
    similar_cases: list[SimilarCase]
    concern_points: list[ConcernPoint]
    questions: list[GeneratedQuestion]
    review_progress: ReviewProgress


@dataclass
class AnswerProgressUpdate:
    """回答進捗更新"""
    draft_id: str
    question_id: str
    answer: str


class DraftReviewService:
    """
    企画ドラフトレビューサービス

    類似ケース検索、懸念点抽出、問い生成をオーケストレーションし、
    レビュー進捗を管理する
    """

    def __init__(
        self,
        case_manager: CaseManager | None = None,
        pattern_analyzer: PatternAnalyzer | None = None,
        question_generator: QuestionGenerator | None = None,
    ):
        """
        初期化

        Args:
            case_manager: ケースマネージャー
            pattern_analyzer: パターン分析エンジン
            question_generator: 問い生成エンジン
        """
        self._case_manager = case_manager or CaseManager()
        self._pattern_analyzer = pattern_analyzer or PatternAnalyzer()
        self._question_generator = question_generator or QuestionGenerator()

        # レビュー状態の管理（本番ではRedis等を使用）
        self._review_states: dict[str, dict[str, Any]] = {}

    async def review_draft(self, request: DraftReviewRequest) -> DraftReviewResponse:
        """
        ドラフトをレビュー

        Args:
            request: ドラフトレビューリクエスト

        Returns:
            DraftReviewResponse: レビュー結果
        """
        # 1. 類似ケース検索
        query_text = f"{request.purpose} {request.target_market} {request.business_model}"
        similar_cases = await self._case_manager.find_similar_cases(
            query_text=query_text,
            limit=10,
        )

        # 2. 懸念点抽出
        pattern_summary = await self._pattern_analyzer.extract_concern_points(
            similar_cases=similar_cases
        )

        # 3. 失敗パターンを収集
        failure_patterns = list(set(
            cp.category for cp in pattern_summary.concern_points
        ))

        # 4. 問い生成
        draft_context = DraftContext(
            purpose=request.purpose,
            target_market=request.target_market,
            business_model=request.business_model,
            additional_context=request.additional_context,
        )

        question_input = QuestionGenInput(
            draft_context=draft_context,
            similar_cases=similar_cases,
            failure_patterns=failure_patterns,
            question_count=5,
        )

        questions = await self._question_generator.generate_questions(question_input)

        # 5. レビュー状態を保存
        self._review_states[request.draft_id] = {
            "questions": {q.id: None for q in questions},
        }

        # 6. 進捗を計算
        review_progress = ReviewProgress(
            total_questions=len(questions),
            answered_questions=0,
            unanswered_question_ids=[q.id for q in questions],
        )

        return DraftReviewResponse(
            similar_cases=similar_cases,
            concern_points=pattern_summary.concern_points,
            questions=questions,
            review_progress=review_progress,
        )

    async def update_answer_progress(
        self,
        update: AnswerProgressUpdate,
    ) -> ReviewProgress:
        """
        回答進捗を更新

        Args:
            update: 回答進捗更新データ

        Returns:
            ReviewProgress: 更新後の進捗
        """
        state = self._review_states.get(update.draft_id)

        if state is None:
            raise ValueError(f"Draft not found: {update.draft_id}")

        # 回答を保存
        state["questions"][update.question_id] = update.answer

        # 進捗を再計算
        return self._calculate_progress(update.draft_id)

    async def get_review_progress(self, draft_id: str) -> ReviewProgress:
        """
        レビュー進捗を取得

        Args:
            draft_id: ドラフトID

        Returns:
            ReviewProgress: 現在の進捗
        """
        if draft_id not in self._review_states:
            raise ValueError(f"Draft not found: {draft_id}")

        return self._calculate_progress(draft_id)

    def _calculate_progress(self, draft_id: str) -> ReviewProgress:
        """進捗を計算"""
        state = self._review_states[draft_id]
        questions = state["questions"]

        total = len(questions)
        answered = sum(1 for answer in questions.values() if answer is not None)
        unanswered_ids = [qid for qid, answer in questions.items() if answer is None]

        return ReviewProgress(
            total_questions=total,
            answered_questions=answered,
            unanswered_question_ids=unanswered_ids,
        )
