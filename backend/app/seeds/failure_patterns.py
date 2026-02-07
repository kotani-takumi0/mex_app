"""
失敗パターンタグのマスターデータ
タスク6.2: サンプルデータ投入とコールドスタート対応
"""

MASTER_FAILURE_PATTERNS: list[dict] = [
    # 財務（financial）カテゴリ
    {
        "name": "収益モデル未確立",
        "description": "収益化の方法が明確でない、または実現可能性が低い",
        "category": "financial",
    },
    {
        "name": "投資対効果不明",
        "description": "投資額に見合うリターンが見込めない、またはROI算出根拠が弱い",
        "category": "financial",
    },
    {
        "name": "初期投資過大",
        "description": "必要な初期投資が企業の許容範囲を超えている",
        "category": "financial",
    },
    {
        "name": "キャッシュフロー問題",
        "description": "収益化までの期間が長く、キャッシュフローが悪化するリスク",
        "category": "financial",
    },
    {
        "name": "価格設定困難",
        "description": "適切な価格設定が難しく、収益性を確保できない",
        "category": "financial",
    },
    # オペレーション（operational）カテゴリ
    {
        "name": "実行体制不備",
        "description": "プロジェクトを実行するための人材・体制が整っていない",
        "category": "operational",
    },
    {
        "name": "リソース不足",
        "description": "必要なリソース（人材、設備、予算）が確保できない",
        "category": "operational",
    },
    {
        "name": "スケジュール非現実的",
        "description": "計画されたスケジュールが現実的でない",
        "category": "operational",
    },
    {
        "name": "業務プロセス未設計",
        "description": "運用に必要な業務プロセスが設計されていない",
        "category": "operational",
    },
    {
        "name": "パートナー依存過多",
        "description": "外部パートナーへの依存度が高すぎる",
        "category": "operational",
    },
    # 市場（market）カテゴリ
    {
        "name": "市場規模誤認",
        "description": "想定した市場規模が実際よりも小さい",
        "category": "market",
    },
    {
        "name": "顧客ニーズ不明確",
        "description": "ターゲット顧客のニーズが検証されていない",
        "category": "market",
    },
    {
        "name": "競合優位性欠如",
        "description": "競合に対する明確な優位性がない",
        "category": "market",
    },
    {
        "name": "タイミング不適",
        "description": "市場投入のタイミングが適切でない（早すぎる/遅すぎる）",
        "category": "market",
    },
    {
        "name": "参入障壁低い",
        "description": "参入障壁が低く、模倣されやすい",
        "category": "market",
    },
    # 技術（technical）カテゴリ
    {
        "name": "技術的実現性低",
        "description": "必要な技術が未成熟、または実現困難",
        "category": "technical",
    },
    {
        "name": "技術リスク高",
        "description": "技術的な不確実性が高く、リスクが大きい",
        "category": "technical",
    },
    {
        "name": "スケーラビリティ問題",
        "description": "規模拡大時に技術的な問題が発生する",
        "category": "technical",
    },
    {
        "name": "セキュリティ懸念",
        "description": "セキュリティ上の問題やリスクがある",
        "category": "technical",
    },
    {
        "name": "既存システム統合困難",
        "description": "既存のシステムとの統合が困難",
        "category": "technical",
    },
    # 組織（organizational）カテゴリ
    {
        "name": "経営層支持不足",
        "description": "経営層からの十分な支持・コミットメントが得られない",
        "category": "organizational",
    },
    {
        "name": "組織文化不適合",
        "description": "企画が組織の文化や価値観と合致しない",
        "category": "organizational",
    },
    {
        "name": "部門間連携困難",
        "description": "必要な部門間の連携が取れない",
        "category": "organizational",
    },
    {
        "name": "戦略整合性欠如",
        "description": "会社の全体戦略と整合していない",
        "category": "organizational",
    },
    {
        "name": "変革抵抗",
        "description": "組織内で変革に対する抵抗が大きい",
        "category": "organizational",
    },
]
