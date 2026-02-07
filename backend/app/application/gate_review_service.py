"""
ゲートレビュー支援サービス
タスク3.2: ゲートレビュー支援サービスの実装

Design.mdに基づく仕様:
- 案件フェーズと仮説状況に基づき、会議のアジェンダ候補を自動生成
- 過去の類似案件で「なぜ採用/不採用になったか」の主要因を検索・表示
- 論点候補リストを整理し、会議前に参照可能な形式で出力
"""
from dataclasses import dataclass, field
from typing import Any

from app.domain.case.case_manager import CaseManager, SimilarCase
from app.domain.pattern.pattern_analyzer import PatternAnalyzer, ProjectPhase
from app.domain.llm.llm_service import LLMService


@dataclass
class HypothesisStatus:
    """仮説状況"""
    hypothesis: str
    status: str  # "verified", "falsified", "pending"
    confidence: float


@dataclass
class AgendaRequest:
    """アジェンダ生成リクエスト"""
    project_id: str
    current_phase: ProjectPhase
    hypothesis_status: list[HypothesisStatus]


@dataclass
class AgendaItem:
    """アジェンダ項目"""
    title: str
    description: str
    priority: int
    related_case_ids: list[str] = field(default_factory=list)
    suggested_duration_minutes: int = 10


@dataclass
class DiscussionPoint:
    """論点"""
    topic: str
    key_questions: list[str]
    historical_context: str
    recommended_outcome: str


@dataclass
class AgendaResponse:
    """アジェンダ生成レスポンス"""
    agenda_items: list[AgendaItem]
    related_cases: list[SimilarCase]
    key_discussion_points: list[DiscussionPoint]


@dataclass
class DecisionReasonSearchRequest:
    """判断理由検索リクエスト"""
    query: str
    limit: int = 10


@dataclass
class DecisionReason:
    """判断理由"""
    case_id: str
    case_title: str
    decision: str
    primary_reason: str
    contributing_factors: list[str]
    relevance_score: float


class GateReviewService:
    """
    ゲートレビュー支援サービス

    会議のアジェンダ候補生成と過去の判断理由検索を提供
    """

    def __init__(
        self,
        case_manager: CaseManager | None = None,
        pattern_analyzer: PatternAnalyzer | None = None,
        llm_service: LLMService | None = None,
    ):
        """
        初期化

        Args:
            case_manager: ケースマネージャー
            pattern_analyzer: パターン分析エンジン
            llm_service: LLMサービス
        """
        self._case_manager = case_manager or CaseManager()
        self._pattern_analyzer = pattern_analyzer or PatternAnalyzer()
        self._llm = llm_service or LLMService()

    async def generate_agenda(self, request: AgendaRequest) -> AgendaResponse:
        """
        会議のアジェンダ候補を生成

        Args:
            request: アジェンダ生成リクエスト

        Returns:
            AgendaResponse: アジェンダ生成結果
        """
        # 1. フェーズ別のボトルネック分析
        bottleneck_analysis = await self._pattern_analyzer.analyze_phase_bottlenecks(
            phase=request.current_phase
        )

        # 2. 類似ケースを検索
        query = f"{request.current_phase.value} phase"
        if request.hypothesis_status:
            hypotheses = " ".join(h.hypothesis for h in request.hypothesis_status)
            query += f" {hypotheses}"

        similar_cases = await self._case_manager.find_similar_cases(
            query_text=query,
            limit=5,
        )

        # 3. LLMでアジェンダを生成
        prompt = self._build_agenda_prompt(
            request,
            bottleneck_analysis,
            similar_cases,
        )

        llm_result = await self._llm.generate_analysis(prompt)

        # 4. 結果をパース
        agenda_items = []
        for item in llm_result.get("agenda_items", []):
            agenda_items.append(
                AgendaItem(
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    priority=item.get("priority", 1),
                    related_case_ids=[c.case_id for c in similar_cases[:3]],
                    suggested_duration_minutes=item.get("duration", 10),
                )
            )

        discussion_points = []
        for point in llm_result.get("discussion_points", []):
            discussion_points.append(
                DiscussionPoint(
                    topic=point.get("topic", ""),
                    key_questions=point.get("questions", []),
                    historical_context=point.get("context", ""),
                    recommended_outcome=point.get("outcome", ""),
                )
            )

        return AgendaResponse(
            agenda_items=agenda_items,
            related_cases=similar_cases,
            key_discussion_points=discussion_points,
        )

    async def search_decision_reasons(
        self,
        request: DecisionReasonSearchRequest,
    ) -> list[DecisionReason]:
        """
        過去の判断理由を検索

        Args:
            request: 判断理由検索リクエスト

        Returns:
            list[DecisionReason]: 判断理由のリスト
        """
        # 類似ケースを検索
        similar_cases = await self._case_manager.find_similar_cases(
            query_text=request.query,
            limit=request.limit,
        )

        reasons = []
        for case in similar_cases:
            # ケースの詳細を取得
            case_detail = await self._case_manager.get_case_by_id(case.case_id)

            if case_detail and case_detail.decision:
                reasons.append(
                    DecisionReason(
                        case_id=case.case_id,
                        case_title=case.title,
                        decision=case_detail.decision.decision,
                        primary_reason=case_detail.decision.reason,
                        contributing_factors=case.matched_segments,
                        relevance_score=case.score,
                    )
                )

        return reasons

    def _build_agenda_prompt(
        self,
        request: AgendaRequest,
        bottleneck_analysis: Any,
        similar_cases: list[SimilarCase],
    ) -> str:
        """アジェンダ生成プロンプトを構築"""
        hypothesis_text = ""
        if request.hypothesis_status:
            hypothesis_text = "\n".join(
                f"- {h.hypothesis}: {h.status} (信頼度: {h.confidence})"
                for h in request.hypothesis_status
            )
        else:
            hypothesis_text = "なし"

        cases_text = ""
        if similar_cases:
            cases_text = "\n".join(
                f"- {c.title} ({c.outcome.value})"
                for c in similar_cases
            )
        else:
            cases_text = "なし"

        bottlenecks_text = ", ".join(bottleneck_analysis.key_bottlenecks)

        return f"""
ゲートレビュー会議のアジェンダを生成してください。

## プロジェクト情報
- フェーズ: {request.current_phase.value}
- 仮説状況:
{hypothesis_text}

## 過去の類似ケース
{cases_text}

## このフェーズでよくあるボトルネック
{bottlenecks_text}

## 要求
以下のJSON形式でアジェンダを生成してください：
{{
    "agenda_items": [
        {{
            "title": "アジェンダ項目のタイトル",
            "description": "説明",
            "priority": 1,
            "duration": 15
        }}
    ],
    "discussion_points": [
        {{
            "topic": "論点のトピック",
            "questions": ["質問1", "質問2"],
            "context": "過去の文脈",
            "outcome": "推奨される結論"
        }}
    ]
}}
"""
