"""
LLMサービス
プラン別モデル切り替え対応（Free: GPT-4o-mini / Pro: GPT-4o）
"""
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from app.config import get_settings


@dataclass
class LLMConfig:
    """LLM設定"""
    model: str = "gpt-4o-mini"  # デフォルトはFreeプラン向け
    temperature: float = 0.7
    max_tokens: int = 2000


class LLMService:
    """
    LLMサービス

    個人開発アドバイザーとしてアイデア壁打ち・振り返りを支援。
    プラン別にモデルを切り替える。
    """

    def __init__(
        self,
        api_key: str | None = None,
        config: LLMConfig | None = None,
    ):
        self.config = config or LLMConfig()

        if api_key is None:
            settings = get_settings()
            api_key = settings.openai_api_key

        self._client = AsyncOpenAI(api_key=api_key)

    @classmethod
    def for_plan(cls, plan: str) -> "LLMService":
        """
        プランに応じたLLMServiceを生成するファクトリメソッド

        Free: GPT-4o-mini（軽量・低コスト）
        Pro: GPT-4o（高品質）
        """
        if plan == "pro":
            config = LLMConfig(model="gpt-4o", temperature=0.7, max_tokens=3000)
        else:
            config = LLMConfig(model="gpt-4o-mini", temperature=0.7, max_tokens=2000)
        return cls(config=config)

    async def generate_summary(self, prompt: str) -> str:
        """テキスト要約を生成"""
        response = await self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "あなたは個人開発アドバイザーです。"
                        "ユーザーの開発アイデアに対して、過去のプロジェクト知識をもとに"
                        "建設的なフィードバックを提供してください。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return response.choices[0].message.content or ""

    async def generate_analysis(self, prompt: str) -> dict[str, Any]:
        """分析結果を生成（JSON形式）"""
        response = await self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "あなたは個人開発アドバイザーです。"
                        "過去のプロジェクト知識をもとに分析し、JSON形式で回答してください。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            response_format={"type": "json_object"},
        )

        import json
        content = response.choices[0].message.content or "{}"
        return json.loads(content)
