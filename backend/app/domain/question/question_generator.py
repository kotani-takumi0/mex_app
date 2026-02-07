"""
問い生成エンジン
タスク2.5: 問い生成エンジンの実装

Design.mdに基づく仕様:
- 類似ケースと失敗パターンに基づき、企画の質を向上させるための「問い」を生成
- LLM（GPT-4/Claude）APIを呼び出し
- 生成された問いをカテゴリ（財務、オペレーション、市場、技術、組織）に分類
"""
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.domain.case.case_manager import SimilarCase
from app.domain.llm.llm_service import LLMService


class QuestionCategory(Enum):
    """問いのカテゴリ"""
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    MARKET = "market"
    TECHNICAL = "technical"
    ORGANIZATIONAL = "organizational"


@dataclass
class DraftContext:
    """企画ドラフトのコンテキスト"""
    purpose: str
    target_market: str
    business_model: str
    additional_context: str | None = None


@dataclass
class QuestionGenInput:
    """問い生成入力"""
    draft_context: DraftContext
    similar_cases: list[SimilarCase]
    failure_patterns: list[str]
    question_count: int = 5


@dataclass
class GeneratedQuestion:
    """生成された問い"""
    id: str
    question: str
    rationale: str
    related_case_ids: list[str]
    related_patterns: list[str]
    category: QuestionCategory


class QuestionGenerator:
    """
    問い生成エンジン

    LLMを使用して企画の質を向上させるための問いを生成する
    """

    def __init__(self, llm_service: LLMService | None = None):
        """
        初期化

        Args:
            llm_service: LLMサービス
        """
        self._llm = llm_service or LLMService()

    async def generate_questions(
        self,
        input_data: QuestionGenInput,
    ) -> list[GeneratedQuestion]:
        """
        問いを生成

        Args:
            input_data: 問い生成入力

        Returns:
            list[GeneratedQuestion]: 生成された問いのリスト
        """
        # プロンプトを構築
        prompt = self._build_prompt(input_data)

        # LLMで問いを生成
        result = await self._llm.generate_analysis(prompt)

        # 結果をパース
        questions = []
        raw_questions = result.get("questions", [])

        for raw_q in raw_questions:
            question_id = f"q-{uuid.uuid4().hex[:8]}"
            category_str = raw_q.get("category", "market")

            try:
                category = QuestionCategory(category_str)
            except ValueError:
                category = QuestionCategory.MARKET

            questions.append(
                GeneratedQuestion(
                    id=question_id,
                    question=raw_q.get("question", ""),
                    rationale=raw_q.get("rationale", ""),
                    related_case_ids=raw_q.get("related_cases", []),
                    related_patterns=raw_q.get("related_patterns", []),
                    category=category,
                )
            )

        return questions

    def _build_prompt(self, input_data: QuestionGenInput) -> str:
        """プロンプトを構築"""
        # 類似ケースの情報を整理
        similar_cases_text = ""
        if input_data.similar_cases:
            cases_info = []
            for case in input_data.similar_cases:
                cases_info.append(
                    f"- {case.title} (ID: {case.case_id}, 結果: {case.outcome.value})\n"
                    f"  目的: {case.purpose}\n"
                    f"  マッチ: {', '.join(case.matched_segments)}"
                )
            similar_cases_text = "\n".join(cases_info)
        else:
            similar_cases_text = "類似ケースなし"

        # 失敗パターンの情報
        patterns_text = ", ".join(input_data.failure_patterns) if input_data.failure_patterns else "なし"

        prompt = f"""
あなたは個人開発アドバイザーです。以下の開発アイデアに対して、
過去の類似プロジェクトと失敗パターンを踏まえた「問い」を生成してください。

## 開発アイデア
- 概要・目的: {input_data.draft_context.purpose}
- ターゲットユーザー: {input_data.draft_context.target_market}
- マネタイズ方法: {input_data.draft_context.business_model}

## 過去の類似プロジェクト
{similar_cases_text}

## 関連する失敗パターン
{patterns_text}

## 要求
{input_data.question_count}個の「問い」を生成してください。
各問いには以下の情報を含めてください：
- question: 開発者が検討すべき問い（質問文）
- rationale: なぜこの問いが重要か（過去の事例を参照）
- category: カテゴリ（financial, operational, market, technical, organizational）
- related_cases: 関連するケースID（上記の類似プロジェクトから）
- related_patterns: 関連する失敗パターン

以下のJSON形式で回答してください：
{{
    "questions": [
        {{
            "question": "この機能にユーザーが月額課金する理由は明確ですか？",
            "rationale": "過去の類似プロジェクトでマネタイズが課題になった",
            "category": "financial",
            "related_cases": ["case-001"],
            "related_patterns": ["financial"]
        }}
    ]
}}
"""
        return prompt
