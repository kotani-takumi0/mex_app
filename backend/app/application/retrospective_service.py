"""
プロジェクト振り返りサービス
旧PostmortemServiceをリネーム＋改修。
個人開発プロジェクトの振り返りを記録し、ナレッジを蓄積する。
"""
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.domain.case.case_manager import (
    CaseManager,
    CaseCreateInput,
    CaseOutcome,
    GoNoGoDecision as DomainGoNoGoDecision,
)
from app.domain.llm.llm_service import LLMService
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import IdeaMemo


class ProjectOutcome(Enum):
    """プロジェクト結果"""
    COMPLETED = "completed"  # 完了（個人開発向けに追加）
    SHIPPED = "shipped"  # リリース済み（個人開発向けに追加）
    WITHDRAWN = "withdrawn"
    CANCELLED = "cancelled"
    PENDING = "pending"


@dataclass
class ProjectDecision:
    """プロジェクト判断"""
    decision: str  # "continue", "pivot", "stop"
    reason: str


@dataclass
class LessonLearned:
    """学んだこと"""
    topic: str
    insight: str


@dataclass
class DiscussionRecord:
    """振り返りメモ"""
    topic: str
    summary: str
    discussed_at: str


@dataclass
class RetrospectiveTemplate:
    """振り返りテンプレート"""
    project_id: str
    sections: list[dict[str, str]]
    outcome_options: list[str]


@dataclass
class RetrospectiveSubmission:
    """振り返り提出"""
    project_id: str
    project_title: str
    outcome: ProjectOutcome
    decision: ProjectDecision | None
    lessons_learned: list[LessonLearned]
    discussions: list[DiscussionRecord]
    user_id: str = ""


@dataclass
class RetrospectiveResult:
    """振り返り結果"""
    record_type: str  # "decision_case" or "idea_memo"
    record_id: str
    assigned_patterns: list[str]


@dataclass
class FailurePatternSuggestion:
    """失敗パターン提案"""
    category: str
    name: str
    confidence: float
    rationale: str


class RetrospectiveService:
    """
    プロジェクト振り返りサービス

    個人開発プロジェクトの振り返りを記録し、
    失敗パターンをタグ付けしてナレッジとして蓄積する。
    """

    def __init__(
        self,
        case_manager: CaseManager | None = None,
        llm_service: LLMService | None = None,
    ):
        self._case_manager = case_manager or CaseManager()
        self._llm = llm_service or LLMService()

    async def get_template(self, project_id: str) -> RetrospectiveTemplate:
        """振り返りテンプレートを取得"""
        return RetrospectiveTemplate(
            project_id=project_id,
            sections=[
                {
                    "name": "学んだこと",
                    "description": "このプロジェクトで学んだ技術・ビジネス上のインサイトを記録してください",
                },
                {
                    "name": "うまくいかなかったこと",
                    "description": "想定通りにいかなかった点とその理由を記録してください",
                },
                {
                    "name": "次のアクション",
                    "description": "次のプロジェクトに活かす判断（続行・ピボット・中止）と理由を記録してください",
                },
            ],
            outcome_options=["completed", "shipped", "withdrawn", "cancelled", "pending"],
        )

    async def submit_retrospective(
        self,
        submission: RetrospectiveSubmission,
    ) -> RetrospectiveResult:
        """
        振り返りを提出

        判断の有無でケースとメモを区別して保存する
        """
        if submission.decision is not None:
            return await self._save_as_decision_case(submission)
        else:
            return await self._save_as_idea_memo(submission)

    async def suggest_failure_patterns(
        self,
        submission: RetrospectiveSubmission,
    ) -> list[FailurePatternSuggestion]:
        """失敗パターンを推定"""
        prompt = self._build_pattern_suggestion_prompt(submission)
        result = await self._llm.generate_analysis(prompt)

        suggestions = []
        for pattern in result.get("patterns", []):
            suggestions.append(
                FailurePatternSuggestion(
                    category=pattern.get("category", ""),
                    name=pattern.get("name", ""),
                    confidence=pattern.get("confidence", 0.0),
                    rationale=pattern.get("rationale", ""),
                )
            )

        return suggestions

    async def _save_as_decision_case(
        self,
        submission: RetrospectiveSubmission,
    ) -> RetrospectiveResult:
        """意思決定ケースとして保存"""
        suggestions = await self.suggest_failure_patterns(submission)
        pattern_categories = [s.category for s in suggestions if s.confidence > 0.5]

        # decision を go/no_go にマッピング
        decision_mapping = {
            "continue": "go",
            "pivot": "no_go",
            "stop": "no_go",
        }
        decision_type = decision_mapping.get(submission.decision.decision, "no_go")

        # outcome を CaseOutcome にマッピング
        outcome_mapping = {
            "completed": "adopted",
            "shipped": "adopted",
            "withdrawn": "withdrawn",
            "cancelled": "cancelled",
            "pending": "withdrawn",
        }
        outcome_value = outcome_mapping.get(submission.outcome.value, "withdrawn")

        case_input = CaseCreateInput(
            title=submission.project_title,
            purpose=f"Project {submission.project_id}",
            outcome=CaseOutcome(outcome_value),
            decision=DomainGoNoGoDecision(
                decision=decision_type,
                reason=submission.decision.reason,
            ),
            failed_hypotheses=[
                {"topic": ll.topic, "insight": ll.insight}
                for ll in submission.lessons_learned
            ],
            discussions=[
                {
                    "topic": d.topic,
                    "summary": d.summary,
                    "discussed_at": d.discussed_at,
                }
                for d in submission.discussions
            ],
            user_id=submission.user_id,
        )

        case = await self._case_manager.create_case(case_input)

        return RetrospectiveResult(
            record_type="decision_case",
            record_id=case.id,
            assigned_patterns=pattern_categories,
        )

    async def _save_as_idea_memo(
        self,
        submission: RetrospectiveSubmission,
    ) -> RetrospectiveResult:
        """アイデアメモとして保存"""
        db = SessionLocal()

        try:
            memo_id = str(uuid.uuid4())
            memo = IdeaMemo(
                id=memo_id,
                user_id=submission.user_id,
                project_id=submission.project_id,
                content={
                    "project_title": submission.project_title,
                    "outcome": submission.outcome.value,
                    "lessons_learned": [
                        {"topic": ll.topic, "insight": ll.insight}
                        for ll in submission.lessons_learned
                    ],
                    "discussions": [
                        {
                            "topic": d.topic,
                            "summary": d.summary,
                            "discussed_at": d.discussed_at,
                        }
                        for d in submission.discussions
                    ],
                },
            )
            db.add(memo)
            db.commit()

            return RetrospectiveResult(
                record_type="idea_memo",
                record_id=memo_id,
                assigned_patterns=[],
            )
        finally:
            db.close()

    def _build_pattern_suggestion_prompt(
        self,
        submission: RetrospectiveSubmission,
    ) -> str:
        """失敗パターン推定プロンプトを構築"""
        lessons_text = ""
        if submission.lessons_learned:
            lessons_text = "\n".join(
                f"- {ll.topic}: {ll.insight}"
                for ll in submission.lessons_learned
            )
        else:
            lessons_text = "なし"

        discussions_text = ""
        if submission.discussions:
            discussions_text = "\n".join(
                f"- {d.topic}: {d.summary}"
                for d in submission.discussions
            )
        else:
            discussions_text = "なし"

        decision_text = ""
        if submission.decision:
            decision_text = f"{submission.decision.decision}: {submission.decision.reason}"
        else:
            decision_text = "判断なし"

        return f"""
以下の個人開発プロジェクトの振り返りから、該当する失敗パターンを推定してください。

## プロジェクト
{submission.project_title}

## 結果
{submission.outcome.value}

## 判断
{decision_text}

## 学んだこと
{lessons_text}

## メモ
{discussions_text}

## 失敗パターンカテゴリ
- financial: 収益面（マネタイズ、コスト、課金等）
- operational: 運用面（デプロイ、運用、保守等）
- market: 市場面（ユーザーニーズ、競合、差別化等）
- technical: 技術面（技術選定、実装難易度、スケーラビリティ等）
- organizational: リソース面（時間、モチベーション、スキル等）

以下のJSON形式で回答してください：
{{
    "patterns": [
        {{
            "category": "market",
            "name": "ユーザーニーズの見誤り",
            "confidence": 0.85,
            "rationale": "想定ユーザー層のリサーチ不足"
        }}
    ]
}}
"""
