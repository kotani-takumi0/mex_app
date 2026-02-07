"""
失敗パターン分析エンジン
タスク2.4: 失敗パターン分析エンジンの実装

Design.mdに基づく仕様:
- 過去の意思決定ケースから論点・懸念点を抽出
- カテゴリ別に要約
- プロジェクトフェーズに基づいてボトルネックとなった論点を特定
- LLMを活用したパターン要約生成
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.domain.case.case_manager import CaseManager, SimilarCase
from app.domain.llm.llm_service import LLMService


class ProjectPhase(Enum):
    """プロジェクトフェーズ"""
    IDEATION = "ideation"
    VALIDATION = "validation"
    DEVELOPMENT = "development"
    LAUNCH = "launch"


@dataclass
class ConcernPoint:
    """懸念点"""
    category: str  # financial, operational, market, technical, organizational
    summary: str
    frequency: int
    related_case_ids: list[str] = field(default_factory=list)


@dataclass
class PatternSummary:
    """パターン要約"""
    concern_points: list[ConcernPoint]
    overall_summary: str


@dataclass
class BottleneckAnalysis:
    """ボトルネック分析結果"""
    phase: ProjectPhase
    key_bottlenecks: list[str]
    historical_frequency: float
    recommended_focus_areas: list[str]


class PatternAnalyzer:
    """
    失敗パターン分析エンジン

    過去の意思決定ケースから論点・懸念点を抽出し、
    カテゴリ別に要約する
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

    async def extract_concern_points(
        self,
        similar_cases: list[SimilarCase],
    ) -> PatternSummary:
        """
        類似ケースから懸念点を抽出

        Args:
            similar_cases: 類似ケースのリスト

        Returns:
            PatternSummary: パターン要約
        """
        # カテゴリ別に懸念点を集計
        category_counts: dict[str, list[tuple[str, str]]] = {
            "financial": [],
            "operational": [],
            "market": [],
            "technical": [],
            "organizational": [],
        }

        for case in similar_cases:
            # マッチしたセグメントからカテゴリを推定
            for segment in case.matched_segments:
                category = self._infer_category(segment)
                category_counts[category].append((case.case_id, segment))

        # LLMを使って要約を生成
        concern_points = []
        for category, items in category_counts.items():
            if items:
                segments = [item[1] for item in items]
                case_ids = list(set(item[0] for item in items))

                # LLMで要約を生成
                summary = await self._generate_category_summary(category, segments)

                concern_points.append(
                    ConcernPoint(
                        category=category,
                        summary=summary,
                        frequency=len(items),
                        related_case_ids=case_ids,
                    )
                )

        # 全体要約を生成
        overall_summary = await self._generate_overall_summary(concern_points)

        return PatternSummary(
            concern_points=concern_points,
            overall_summary=overall_summary,
        )

    async def analyze_phase_bottlenecks(
        self,
        phase: ProjectPhase,
    ) -> BottleneckAnalysis:
        """
        フェーズ別のボトルネックを分析

        Args:
            phase: プロジェクトフェーズ

        Returns:
            BottleneckAnalysis: ボトルネック分析結果
        """
        # LLMを使ってフェーズ別の分析を実行
        prompt = f"""
        プロジェクトの「{phase.value}」フェーズにおける
        過去の失敗パターンを分析し、以下をJSON形式で回答してください：

        {{
            "bottlenecks": ["ボトルネック1", "ボトルネック2"],
            "focus_areas": ["注力すべき領域1", "注力すべき領域2"],
            "frequency": 0.5
        }}
        """

        analysis = await self._llm.generate_analysis(prompt)

        return BottleneckAnalysis(
            phase=phase,
            key_bottlenecks=analysis.get("bottlenecks", []),
            historical_frequency=analysis.get("frequency", 0.0),
            recommended_focus_areas=analysis.get("focus_areas", []),
        )

    async def generate_pattern_summary(
        self,
        failure_patterns: list[str],
        context: str,
    ) -> str:
        """
        失敗パターンの要約を生成

        Args:
            failure_patterns: 失敗パターンのカテゴリリスト
            context: 現在の企画のコンテキスト

        Returns:
            str: 生成された要約
        """
        prompt = f"""
        以下の失敗パターンカテゴリに基づいて、
        「{context}」に関する過去の教訓を要約してください：

        失敗パターン: {', '.join(failure_patterns)}

        具体的な注意点と改善提案を含めてください。
        """

        return await self._llm.generate_summary(prompt)

    def _infer_category(self, text: str) -> str:
        """テキストからカテゴリを推定"""
        text_lower = text.lower()

        category_keywords = {
            "financial": ["収益", "コスト", "予算", "売上", "利益", "財務", "投資"],
            "operational": ["運用", "オペレーション", "業務", "プロセス", "体制"],
            "market": ["市場", "顧客", "競合", "ニーズ", "需要", "マーケット"],
            "technical": ["技術", "システム", "開発", "実装", "アーキテクチャ"],
            "organizational": ["組織", "人材", "チーム", "リソース", "体制"],
        }

        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category

        return "operational"  # デフォルト

    async def _generate_category_summary(
        self,
        category: str,
        segments: list[str],
    ) -> str:
        """カテゴリ別の要約を生成"""
        category_names = {
            "financial": "財務面",
            "operational": "オペレーション面",
            "market": "市場面",
            "technical": "技術面",
            "organizational": "組織面",
        }

        prompt = f"""
        以下は過去の企画案で指摘された「{category_names.get(category, category)}」
        に関する論点です。これらを簡潔に要約してください：

        {chr(10).join(segments)}

        1-2文で要約してください。
        """

        return await self._llm.generate_summary(prompt)

    async def _generate_overall_summary(
        self,
        concern_points: list[ConcernPoint],
    ) -> str:
        """全体要約を生成"""
        if not concern_points:
            return "特に目立った懸念点はありません。"

        points_text = "\n".join(
            f"- {p.category}: {p.summary} (頻度: {p.frequency}件)"
            for p in concern_points
        )

        prompt = f"""
        以下の懸念点を踏まえ、全体的な注意点を1-2文で要約してください：

        {points_text}
        """

        return await self._llm.generate_summary(prompt)
