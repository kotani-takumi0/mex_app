"""
サンプル意思決定ケース
タスク6.2: サンプルデータ投入とコールドスタート対応
"""

SAMPLE_DECISION_CASES: list[dict] = [
    # 採用案（adopted）
    {
        "title": "社内DXプラットフォーム構築プロジェクト",
        "purpose": "社内の業務効率化とデータ活用を促進するための統合プラットフォームを構築する",
        "target_market": "自社グループ全体（従業員5,000名）",
        "business_model": "社内向けサービスとして提供し、業務効率化によるコスト削減を実現",
        "outcome": "adopted",
        "decision_type": "go",
        "decision_reason": "全社DX戦略との整合性が高く、投資対効果が明確に見込める。既存システムとの統合も段階的に実施可能。",
        "failed_hypotheses": [],
        "discussions": [
            {
                "topic": "投資規模の妥当性",
                "summary": "3年間のTCOを算出し、5年で投資回収可能と判断",
                "discussed_at": "2024-01-15",
            }
        ],
        "failure_patterns": [],
    },
    {
        "title": "サブスクリプション型保守サービス",
        "purpose": "従来の単発保守契約から月額制のサブスクリプションモデルへ移行する",
        "target_market": "既存顧客（中堅製造業100社）",
        "business_model": "月額固定料金で予防保守・緊急対応・アップグレードを包括提供",
        "outcome": "adopted",
        "decision_type": "go",
        "decision_reason": "顧客アンケートで80%が乗り換え意向を示し、LTV向上と収益安定化が見込める。",
        "failed_hypotheses": [],
        "discussions": [
            {
                "topic": "価格設定",
                "summary": "現行契約の平均単価から15%増で設定し、サービス拡充で価値を訴求",
                "discussed_at": "2024-02-20",
            }
        ],
        "failure_patterns": [],
    },
    # 却下案（rejected）
    {
        "title": "個人向けヘルスケアアプリ開発",
        "purpose": "AIを活用した健康管理アプリで個人ユーザー市場に参入する",
        "target_market": "健康意識の高い20-40代（国内3,000万人）",
        "business_model": "フリーミアムモデル（基本無料、プレミアム機能月額980円）",
        "outcome": "rejected",
        "decision_type": "no_go",
        "decision_reason": "競合が多数存在し差別化が困難。またB2C事業のノウハウが社内にない。",
        "failed_hypotheses": [
            {
                "hypothesis": "AIによる健康アドバイスで差別化できる",
                "failure_reason": "類似機能を持つ競合アプリが10以上存在し、特許による保護も困難",
            }
        ],
        "discussions": [
            {
                "topic": "市場参入戦略",
                "summary": "後発参入のハンデが大きく、マーケティング費用が膨大になる見込み",
                "discussed_at": "2024-03-10",
            }
        ],
        "failure_patterns": ["競合優位性欠如", "組織文化不適合"],
    },
    {
        "title": "海外現地法人向けERPパッケージ",
        "purpose": "海外拠点向けに標準化されたERPパッケージを開発・販売する",
        "target_market": "日系企業の海外現地法人（東南アジア中心）",
        "business_model": "ライセンス販売＋導入支援＋保守契約",
        "outcome": "rejected",
        "decision_type": "no_go",
        "decision_reason": "各国の法規制対応コストが想定を大幅に超え、採算が取れない見込み。",
        "failed_hypotheses": [
            {
                "hypothesis": "共通機能80%でカスタマイズを最小化できる",
                "failure_reason": "税務・会計処理の国別差異が大きく、実際は60%程度の共通化が限界",
            }
        ],
        "discussions": [
            {
                "topic": "開発コスト見積",
                "summary": "国別対応で当初見積の2.5倍のコストが必要と判明",
                "discussed_at": "2024-04-05",
            }
        ],
        "failure_patterns": ["投資対効果不明", "技術的実現性低"],
    },
    # 撤退案（withdrawn）
    {
        "title": "AIチャットボット顧客対応サービス",
        "purpose": "AIチャットボットによる24時間顧客対応サービスを提供する",
        "target_market": "EC事業者（中小規模、年商1-10億円）",
        "business_model": "月額固定＋従量課金のSaaSモデル",
        "outcome": "withdrawn",
        "decision_type": "no_go",
        "decision_reason": "PoC実施の結果、回答精度が目標に達せず、顧客満足度の向上につながらなかった。",
        "failed_hypotheses": [
            {
                "hypothesis": "回答精度90%以上を達成できる",
                "failure_reason": "PoC結果で75%止まり。商品知識の学習に想定以上の時間とデータが必要",
            },
            {
                "hypothesis": "オペレーターコストを50%削減できる",
                "failure_reason": "複雑な問い合わせは結局人間対応が必要で、削減効果は20%程度",
            },
        ],
        "discussions": [
            {
                "topic": "PoC結果レビュー",
                "summary": "3ヶ月のPoCで目標KPI未達。技術的改善の見通しも立たず撤退を決定",
                "discussed_at": "2024-05-20",
            }
        ],
        "failure_patterns": ["技術的実現性低", "顧客ニーズ不明確"],
    },
    {
        "title": "スマート工場IoTソリューション",
        "purpose": "製造業向けのIoTセンサーとデータ分析基盤をパッケージ提供する",
        "target_market": "中堅製造業（従業員100-500名）",
        "business_model": "初期導入費＋月額利用料（データ容量に応じた従量制）",
        "outcome": "withdrawn",
        "decision_type": "no_go",
        "decision_reason": "既存設備への後付けが技術的に困難で、導入障壁が高すぎた。",
        "failed_hypotheses": [
            {
                "hypothesis": "既存設備に簡単にセンサーを追加できる",
                "failure_reason": "工場ごとに設備が異なり、標準化されたソリューションでは対応できない",
            }
        ],
        "discussions": [
            {
                "topic": "パイロット導入結果",
                "summary": "5社でパイロット実施も、4社で導入断念。カスタマイズコストが高すぎる",
                "discussed_at": "2024-06-15",
            }
        ],
        "failure_patterns": ["既存システム統合困難", "市場規模誤認"],
    },
    # 中止案（cancelled）
    {
        "title": "ブロックチェーン活用サプライチェーン管理",
        "purpose": "ブロックチェーン技術を活用した透明性の高いサプライチェーン管理システムを構築する",
        "target_market": "食品・医薬品メーカー（トレーサビリティ重視企業）",
        "business_model": "コンソーシアム型プラットフォーム（参加費＋トランザクション課金）",
        "outcome": "cancelled",
        "decision_type": "no_go",
        "decision_reason": "コンソーシアム参加企業の合意形成に時間がかかり、市場機会を逸失。",
        "failed_hypotheses": [
            {
                "hypothesis": "主要企業10社のコンソーシアムを1年で組成できる",
                "failure_reason": "データ共有の範囲で各社の利害が対立し、2年経過しても3社止まり",
            }
        ],
        "discussions": [
            {
                "topic": "コンソーシアム組成状況",
                "summary": "競合他社との情報共有に抵抗感が強く、参加企業が増えない",
                "discussed_at": "2024-07-10",
            }
        ],
        "failure_patterns": ["パートナー依存過多", "タイミング不適"],
    },
    {
        "title": "リモートワーク支援SaaS",
        "purpose": "リモートワーク環境下での生産性向上と従業員エンゲージメント向上を支援するSaaSを提供する",
        "target_market": "リモートワーク導入企業（従業員100名以上）",
        "business_model": "ユーザー数に応じた月額課金",
        "outcome": "adopted",
        "decision_type": "go",
        "decision_reason": "市場調査で強いニーズを確認。自社のリモートワーク経験をプロダクト化できる。",
        "failed_hypotheses": [],
        "discussions": [
            {
                "topic": "競合分析",
                "summary": "大手プレイヤーと機能差別化し、中堅企業向けに特化することで勝機あり",
                "discussed_at": "2024-08-05",
            }
        ],
        "failure_patterns": [],
    },
]
