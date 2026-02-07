"""
ポストモーテムサービス
タスク3.3: ポストモーテムサービスの実装

Design.mdに基づく仕様:
- プロジェクト撤退・中止・ペンディング時に、仮説の崩壊理由と組織内議論を入力するテンプレートを提供
- Go/NoGo判断と理由（1〜3文）の有無を検証し、ケースとアイデアメモを区別して保存
- 失敗パターンタグの候補をLLMで推定し、ユーザーに提示
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
    WITHDRAWN = "withdrawn"
    CANCELLED = "cancelled"
    PENDING = "pending"


@dataclass
class GoNoGoDecision:
    """Go/NoGo判断"""
    decision: str  # "go" or "no_go"
    reason: str  # 1-3文


@dataclass
class FailedHypothesis:
    """失敗した仮説"""
    hypothesis: str
    failure_reason: str


@dataclass
class DiscussionRecord:
    """議論記録"""
    topic: str
    summary: str
    discussed_at: str


@dataclass
class PostmortemTemplate:
    """ポストモーテムテンプレート"""
    project_id: str
    sections: list[dict[str, str]]
    outcome_options: list[str]


@dataclass
class PostmortemSubmission:
    """ポストモーテム提出"""
    project_id: str
    outcome: ProjectOutcome
    decision: GoNoGoDecision | None
    failed_hypotheses: list[FailedHypothesis]
    discussions: list[DiscussionRecord]


@dataclass
class PostmortemResult:
    """ポストモーテム結果"""
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


class PostmortemService:
    """
    ポストモーテムサービス

    プロジェクトの振り返りを記録し、組織学習に活用
    """

    def __init__(
        self,
        case_manager: CaseManager | None = None,
        llm_service: LLMService | None = None,
    ):
        """
        初期化

        Args:
            case_manager: ケースマネージャー
            llm_service: LLMサービス
        """
        self._case_manager = case_manager or CaseManager()
        self._llm = llm_service or LLMService()

    async def get_template(self, project_id: str) -> PostmortemTemplate:
        """
        ポストモーテムテンプレートを取得

        Args:
            project_id: プロジェクトID

        Returns:
            PostmortemTemplate: テンプレート
        """
        return PostmortemTemplate(
            project_id=project_id,
            sections=[
                {
                    "name": "仮説の検証結果",
                    "description": "どの仮説が崩れたか、その理由を記録してください",
                },
                {
                    "name": "組織内議論",
                    "description": "どんな議論があったか、主要な論点を記録してください",
                },
                {
                    "name": "判断理由",
                    "description": "Go/NoGo判断とその理由（1〜3文）を記録してください",
                },
            ],
            outcome_options=["withdrawn", "cancelled", "pending"],
        )

    async def submit_postmortem(
        self,
        submission: PostmortemSubmission,
    ) -> PostmortemResult:
        """
        ポストモーテムを提出

        Go/NoGo判断の有無でケースとメモを区別して保存

        Args:
            submission: ポストモーテム提出データ

        Returns:
            PostmortemResult: 保存結果
        """
        if submission.decision is not None:
            # Go/NoGo判断がある場合は意思決定ケースとして保存
            return await self._save_as_decision_case(submission)
        else:
            # 判断がない場合はアイデアメモとして保存
            return await self._save_as_idea_memo(submission)

    async def suggest_failure_patterns(
        self,
        submission: PostmortemSubmission,
    ) -> list[FailurePatternSuggestion]:
        """
        失敗パターンを推定

        Args:
            submission: ポストモーテム提出データ

        Returns:
            list[FailurePatternSuggestion]: 推定された失敗パターン
        """
        # プロンプトを構築
        prompt = self._build_pattern_suggestion_prompt(submission)

        # LLMで推定
        result = await self._llm.generate_analysis(prompt)

        # 結果をパース
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
        submission: PostmortemSubmission,
    ) -> PostmortemResult:
        """意思決定ケースとして保存"""
        # 失敗パターンを推定
        suggestions = await self.suggest_failure_patterns(submission)
        pattern_categories = [s.category for s in suggestions if s.confidence > 0.5]

        # ケースを作成
        case_input = CaseCreateInput(
            title=f"Project {submission.project_id} - {submission.outcome.value}",
            purpose="",  # プロジェクト情報から取得する想定
            outcome=CaseOutcome(submission.outcome.value),
            decision=DomainGoNoGoDecision(
                decision=submission.decision.decision,
                reason=submission.decision.reason,
            ),
            failed_hypotheses=[
                {"hypothesis": fh.hypothesis, "failure_reason": fh.failure_reason}
                for fh in submission.failed_hypotheses
            ],
            discussions=[
                {
                    "topic": d.topic,
                    "summary": d.summary,
                    "discussed_at": d.discussed_at,
                }
                for d in submission.discussions
            ],
        )

        case = await self._case_manager.create_case(case_input)

        return PostmortemResult(
            record_type="decision_case",
            record_id=case.id,
            assigned_patterns=pattern_categories,
        )

    async def _save_as_idea_memo(
        self,
        submission: PostmortemSubmission,
    ) -> PostmortemResult:
        """アイデアメモとして保存"""
        db = SessionLocal()

        try:
            memo_id = str(uuid.uuid4())
            memo = IdeaMemo(
                id=memo_id,
                project_id=submission.project_id,
                content={
                    "outcome": submission.outcome.value,
                    "failed_hypotheses": [
                        {"hypothesis": fh.hypothesis, "failure_reason": fh.failure_reason}
                        for fh in submission.failed_hypotheses
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

            return PostmortemResult(
                record_type="idea_memo",
                record_id=memo_id,
                assigned_patterns=[],
            )

        finally:
            db.close()

    def _build_pattern_suggestion_prompt(
        self,
        submission: PostmortemSubmission,
    ) -> str:
        """失敗パターン推定プロンプトを構築"""
        hypotheses_text = ""
        if submission.failed_hypotheses:
            hypotheses_text = "\n".join(
                f"- {fh.hypothesis}: {fh.failure_reason}"
                for fh in submission.failed_hypotheses
            )
        else:
            hypotheses_text = "なし"

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
以下のポストモーテム情報から、該当する失敗パターンを推定してください。

## プロジェクト結果
{submission.outcome.value}

## 判断
{decision_text}

## 崩れた仮説
{hypotheses_text}

## 議論内容
{discussions_text}

## 失敗パターンカテゴリ
- financial: 財務面（収益性、コスト、予算等）
- operational: オペレーション面（運用、業務、プロセス等）
- market: 市場面（市場規模、顧客ニーズ、競合等）
- technical: 技術面（技術的実現性、システム等）
- organizational: 組織面（人材、体制、リソース等）

以下のJSON形式で回答してください：
{{
    "patterns": [
        {{
            "category": "market",
            "name": "市場規模の誤認",
            "confidence": 0.85,
            "rationale": "市場調査不足による誤認"
        }}
    ]
}}
"""
