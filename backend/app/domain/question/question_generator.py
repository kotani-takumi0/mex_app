"""クイズ生成エンジン"""

from dataclasses import dataclass

from app.domain.llm.llm_service import LLMService


@dataclass
class GeneratedQuizQuestion:
    """生成されたクイズ問題"""

    technology: str
    question: str
    options: list[str]
    correct_answer: int
    explanation: str
    difficulty: str


class QuestionGenerator:
    """開発ログから4択クイズを生成する"""

    def __init__(self, llm_service: LLMService | None = None):
        self._llm = llm_service or LLMService()

    async def generate_questions(
        self,
        devlog_entries: list[dict],
        technologies: list[str],
        count: int,
        difficulty: str,
    ) -> list[GeneratedQuizQuestion]:
        prompt = self._build_quiz_prompt(devlog_entries, technologies, count, difficulty)
        result = await self._llm.generate_analysis(prompt)

        questions: list[GeneratedQuizQuestion] = []
        for raw_q in result.get("questions", []):
            options = raw_q.get("options", [])
            if not isinstance(options, list) or len(options) < 4:
                continue
            options = options[:4]

            correct_answer = raw_q.get("correct_answer", 0)
            if not isinstance(correct_answer, int):
                correct_answer = 0
            if correct_answer < 0 or correct_answer > 3:
                correct_answer = 0

            questions.append(
                GeneratedQuizQuestion(
                    technology=raw_q.get("technology", ""),
                    question=raw_q.get("question", ""),
                    options=options,
                    correct_answer=correct_answer,
                    explanation=raw_q.get("explanation", ""),
                    difficulty=raw_q.get("difficulty", difficulty),
                )
            )

        return questions

    @staticmethod
    def _build_quiz_prompt(
        devlog_entries: list[dict],
        technologies: list[str],
        count: int,
        difficulty: str,
    ) -> str:
        entries_text = "\n".join(
            f"- [{e.get('entry_type', '')}] {e.get('summary', '')} (技術: {', '.join(e.get('technologies', []))})"
            for e in devlog_entries
        )

        return f"""
あなたは技術面接官です。以下の開発ログに基づいて、開発者が使用した技術を
本当に理解しているかを確認するための4択クイズを生成してください。

## 開発ログ
{entries_text}

## 対象技術
{", ".join(technologies)}

## 要求
- {count}問の4択クイズを生成
- 難易度: {difficulty}
- 各問題は開発ログの内容に関連すること
- 「なんとなくAIに作らせた」だけでは答えられない、技術の本質的な理解を問う問題にすること
- 正解は1つのみ

以下のJSON形式で回答してください：
{{
    "questions": [
        {{
            "technology": "React Router",
            "question": "React Routerの<Routes>コンポーネントの役割として正しいものはどれですか？",
            "options": [
                "URLパスに基づいて表示するコンポーネントを切り替える",
                "HTTPリクエストをサーバーに送信する",
                "ブラウザの戻るボタンを無効化する",
                "CSSのルーティングルールを定義する"
            ],
            "correct_answer": 0,
            "explanation": "React Routerの<Routes>は現在のURLパスに基づいて、マッチする<Route>の子コンポーネントをレンダリングします。",
            "difficulty": "easy"
        }}
    ]
}}
"""
