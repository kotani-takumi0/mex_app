"""
コールドスタート対応（フォールバック）
タスク6.2: サンプルデータ投入とコールドスタート対応
"""
from typing import Any


def get_empty_results_message(result_type: str) -> str:
    """
    データが少ない場合のメッセージを取得

    Args:
        result_type: 結果タイプ（similar_cases, questions, concerns）

    Returns:
        ユーザー向けメッセージ
    """
    messages = {
        "similar_cases": (
            "現在、類似ケースのデータが十分に蓄積されていません。"
            "組織内の過去の意思決定記録を登録することで、より有用な類似ケースが表示されるようになります。"
        ),
        "questions": (
            "過去のデータに基づく問いを生成するには、より多くの意思決定ケースの登録が必要です。"
            "一般的な視点からの問いを表示しています。"
        ),
        "concerns": (
            "懸念点の分析には過去の失敗パターンデータが必要です。"
            "ポストモーテムの記録を蓄積することで、より精度の高い懸念点が抽出されます。"
        ),
        "agenda": (
            "アジェンダ候補の生成には過去の会議記録が必要です。"
            "一般的なアジェンダテンプレートを表示しています。"
        ),
    }
    return messages.get(result_type, "データが不足しています。")


def get_fallback_similar_cases() -> list[dict]:
    """
    類似ケースのフォールバックデータを取得

    Returns:
        フォールバック用の空リスト（または説明用データ）
    """
    return []


def get_fallback_questions() -> list[dict]:
    """
    問いのフォールバックデータを取得

    Returns:
        一般的な視点からの問いリスト
    """
    return [
        {
            "id": "fallback-q1",
            "question": "この企画の収益モデルは明確ですか？いつ、どのように収益化しますか？",
            "rationale": "新規事業で最も重要な検討事項の一つです",
            "category": "financial",
            "related_case_ids": [],
            "related_patterns": [],
        },
        {
            "id": "fallback-q2",
            "question": "ターゲット顧客は誰ですか？そのニーズは検証されていますか？",
            "rationale": "顧客不在の企画は失敗リスクが高いです",
            "category": "market",
            "related_case_ids": [],
            "related_patterns": [],
        },
        {
            "id": "fallback-q3",
            "question": "競合との差別化ポイントは何ですか？持続可能な優位性はありますか？",
            "rationale": "競争環境の理解は不可欠です",
            "category": "market",
            "related_case_ids": [],
            "related_patterns": [],
        },
        {
            "id": "fallback-q4",
            "question": "この企画を実行するための体制は整っていますか？必要なスキルセットは確保できますか？",
            "rationale": "実行力がなければ良い企画も失敗します",
            "category": "operational",
            "related_case_ids": [],
            "related_patterns": [],
        },
        {
            "id": "fallback-q5",
            "question": "技術的な実現可能性は検証されていますか？主要なリスクは特定されていますか？",
            "rationale": "技術リスクの見落としは大きな損失につながります",
            "category": "technical",
            "related_case_ids": [],
            "related_patterns": [],
        },
        {
            "id": "fallback-q6",
            "question": "会社の戦略方針と整合していますか？経営層のサポートは得られますか？",
            "rationale": "組織的な支援がないと推進が困難です",
            "category": "organizational",
            "related_case_ids": [],
            "related_patterns": [],
        },
    ]


def get_fallback_concerns() -> list[dict]:
    """
    懸念点のフォールバックデータを取得

    Returns:
        一般的な懸念点カテゴリリスト
    """
    return [
        {
            "category": "財務",
            "summary": "収益モデルと投資対効果を十分に検討してください",
            "frequency": 0,
            "related_case_ids": [],
        },
        {
            "category": "市場",
            "summary": "市場規模と顧客ニーズの検証を行ってください",
            "frequency": 0,
            "related_case_ids": [],
        },
        {
            "category": "オペレーション",
            "summary": "実行体制とリソースの確保を確認してください",
            "frequency": 0,
            "related_case_ids": [],
        },
    ]


def get_fallback_agenda_items() -> list[dict]:
    """
    アジェンダのフォールバックデータを取得

    Returns:
        一般的なアジェンダ項目リスト
    """
    return [
        {
            "title": "企画概要の確認",
            "description": "目的、ターゲット、ビジネスモデルの概要を共有",
            "priority": 1,
            "related_case_ids": [],
            "suggested_duration_minutes": 10,
        },
        {
            "title": "市場・競合分析",
            "description": "市場規模、競合状況、差別化ポイントの確認",
            "priority": 2,
            "related_case_ids": [],
            "suggested_duration_minutes": 15,
        },
        {
            "title": "収益性・投資計画",
            "description": "収益モデル、必要投資額、回収計画の検討",
            "priority": 3,
            "related_case_ids": [],
            "suggested_duration_minutes": 15,
        },
        {
            "title": "リスク評価",
            "description": "主要なリスクの特定と対策の検討",
            "priority": 4,
            "related_case_ids": [],
            "suggested_duration_minutes": 10,
        },
        {
            "title": "Go/NoGo判断",
            "description": "最終的な判断とネクストステップの決定",
            "priority": 5,
            "related_case_ids": [],
            "suggested_duration_minutes": 10,
        },
    ]
