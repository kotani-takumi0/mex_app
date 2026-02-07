"""
LLMサービス
GPT-4/Claude APIを呼び出すための共通サービス
"""
from dataclasses import dataclass
from typing import Any

from openai import AsyncOpenAI

from app.config import get_settings


@dataclass
class LLMConfig:
    """LLM設定"""
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2000


class LLMService:
    """
    LLMサービス

    OpenAI GPT-4 APIを使用してテキスト生成を行う
    """

    def __init__(
        self,
        api_key: str | None = None,
        config: LLMConfig | None = None,
    ):
        """
        初期化

        Args:
            api_key: OpenAI APIキー
            config: LLM設定
        """
        self.config = config or LLMConfig()

        if api_key is None:
            settings = get_settings()
            api_key = settings.openai_api_key

        self._client = AsyncOpenAI(api_key=api_key)

    async def generate_summary(self, prompt: str) -> str:
        """
        テキスト要約を生成

        Args:
            prompt: プロンプト

        Returns:
            str: 生成された要約
        """
        response = await self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "あなたは企画立案の専門家です。"},
                {"role": "user", "content": prompt},
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return response.choices[0].message.content or ""

    async def generate_analysis(self, prompt: str) -> dict[str, Any]:
        """
        分析結果を生成（JSON形式）

        Args:
            prompt: プロンプト

        Returns:
            dict: 分析結果
        """
        response = await self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {
                    "role": "system",
                    "content": "あなたは企画立案の専門家です。JSON形式で回答してください。",
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
