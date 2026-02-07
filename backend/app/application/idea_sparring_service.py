"""
アイデア壁打ちサービス
旧DraftReviewServiceをリネーム＋改修。
個人開発アドバイザーとして、アイデアに対する類似ケース検索・問い生成を行う。
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
class IdeaSparringRequest:
    """アイデア壁打ちリクエスト"""
    idea_id: str
    purpose: str  # アイデアの概要・目的
    target_market: str  # ターゲットユーザー
    business_model: str  # マネタイズ方法
    additional_context: str | None = None
    user_id: str = ""


@dataclass
class SparringProgress:
    """壁打ち進捗"""
    total_questions: int
    answered_questions: int
    unanswered_question_ids: list[str]


@dataclass
class IdeaSparringResponse:
    """アイデア壁打ちレスポンス"""
    similar_cases: list[SimilarCase]
    concern_points: list[ConcernPoint]
    questions: list[GeneratedQuestion]
    sparring_progress: SparringProgress


@dataclass
class AnswerProgressUpdate:
    """回答進捗更新"""
    idea_id: str
    question_id: str
    answer: str


class IdeaSparringService:
    """
    アイデア壁打ちサービス

    過去のプロジェクト知識を活用し、アイデアの重複を防ぎ質を上げるための
    類似ケース検索、懸念点抽出、問い生成をオーケストレーションする。
    """

    def __init__(
        self,
        case_manager: CaseManager | None = None,
        pattern_analyzer: PatternAnalyzer | None = None,
        question_generator: QuestionGenerator | None = None,
    ):
        self._case_manager = case_manager or CaseManager()
        self._pattern_analyzer = pattern_analyzer or PatternAnalyzer()
        self._question_generator = question_generator or QuestionGenerator()

        # 壁打ち状態の管理（本番ではRedis等を使用）
        self._sparring_states: dict[str, dict[str, Any]] = {}

    async def spar_idea(
        self,
        request: IdeaSparringRequest,
    ) -> IdeaSparringResponse:
        """
        アイデアを壁打ち

        Args:
            request: アイデア壁打ちリクエスト

        Returns:
            IdeaSparringResponse: 壁打ち結果
        """
        # 1. 類似ケース検索（user_idでフィルター）
        query_text = f"{request.purpose} {request.target_market} {request.business_model}"
        similar_cases = await self._case_manager.find_similar_cases(
            query_text=query_text,
            limit=10,
            user_id=request.user_id,
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

        # 5. 壁打ち状態を保存
        self._sparring_states[request.idea_id] = {
            "questions": {q.id: None for q in questions},
        }

        # 6. 進捗を計算
        sparring_progress = SparringProgress(
            total_questions=len(questions),
            answered_questions=0,
            unanswered_question_ids=[q.id for q in questions],
        )

        return IdeaSparringResponse(
            similar_cases=similar_cases,
            concern_points=pattern_summary.concern_points,
            questions=questions,
            sparring_progress=sparring_progress,
        )

    async def update_answer_progress(
        self,
        update: AnswerProgressUpdate,
    ) -> SparringProgress:
        """回答進捗を更新"""
        state = self._sparring_states.get(update.idea_id)

        if state is None:
            raise ValueError(f"Idea not found: {update.idea_id}")

        state["questions"][update.question_id] = update.answer
        return self._calculate_progress(update.idea_id)

    async def get_sparring_progress(self, idea_id: str) -> SparringProgress:
        """壁打ち進捗を取得"""
        if idea_id not in self._sparring_states:
            raise ValueError(f"Idea not found: {idea_id}")

        return self._calculate_progress(idea_id)

    def _calculate_progress(self, idea_id: str) -> SparringProgress:
        """進捗を計算"""
        state = self._sparring_states[idea_id]
        questions = state["questions"]

        total = len(questions)
        answered = sum(1 for answer in questions.values() if answer is not None)
        unanswered_ids = [qid for qid, answer in questions.items() if answer is None]

        return SparringProgress(
            total_questions=total,
            answered_questions=answered,
            unanswered_question_ids=unanswered_ids,
        )
