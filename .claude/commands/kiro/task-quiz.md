---
description: Quiz to test engineering understanding of tasks
allowed-tools: Read, Glob, Grep, AskUserQuestion
argument-hint: <feature-name> [task-number]
---

# Task Engineering Quiz

<background_information>
- **Mission**: エンジニアリング観点でのタスク理解度を確認するクイズを実施する
- **Success Criteria**:
  - 技術選定の理由を説明できる
  - コンポーネント間の依存関係を理解している
  - 実装上の注意点を把握している
  - 他のエンジニアに技術判断を説明できる
</background_information>

<instructions>
## Core Task
機能 **$1** の技術理解度を確認するクイズを生成・実施する。
$2 が指定されている場合はそのタスクに焦点、指定がない場合は全体から出題。

## Execution Steps

### Step 1: コンテキストの読み込み

**必要なファイルを全て読み込む**:
- `.kiro/specs/$1/tasks.md` - タスク一覧
- `.kiro/specs/$1/requirements.md` - 要件定義
- `.kiro/specs/$1/design.md` - 設計ドキュメント
- `.kiro/specs/$1/spec.json` - 仕様メタデータ

### Step 2: クイズ問題の生成

**エンジニアリング観点のカテゴリ**:
1. **技術選定**: なぜこの技術/ライブラリを使うか
2. **アーキテクチャ**: レイヤー構成と責務分離
3. **依存関係**: コンポーネント間の依存と実装順序
4. **データ設計**: スキーマ設計とインデックス戦略
5. **API設計**: エンドポイント設計とエラーハンドリング
6. **実装詳細**: 具体的なコードパターンと注意点

### Step 3: 対話的なクイズ実施

**AskUserQuestion ツールを使用して問題を出題**:
- 1問ずつ出題
- 回答を受け取り、技術的な正誤判定
- 解説とベストプラクティスを提供

### Step 4: 結果サマリー

**全問終了後に結果を表示**:
- 正答率（カテゴリ別）
- 弱点となる技術領域
- 推奨する追加学習リソース

## Quiz Question Examples

### Category 1: 技術選定
```
Q: EmbeddingService で OpenAI text-embedding-3-large を選定した理由として
   最も適切なものは？

A) 無料で使えるから
B) 3072次元の高次元ベクトルで意味的な類似性を高精度に捉えられるから ← 正解
C) ローカルで実行できるから
D) リアルタイム処理に特化しているから

解説: text-embedding-3-large は OpenAI の最新埋め込みモデルで、
3072次元という高次元ベクトルにより、テキストの意味的な類似性を
高い精度で捉えられます。代替案の Sentence Transformers はローカル実行可能ですが、
次元数・精度で劣ります。
```

### Category 2: アーキテクチャ
```
Q: 本システムで CaseManager が Domain Layer に配置されている理由は？

A) データベースに直接アクセスする必要があるから
B) HTTP リクエストを処理する必要があるから
C) 意思決定ケースのビジネスルールとライフサイクルを管理する責務があるから ← 正解
D) UIコンポーネントとして機能するから

解説: CaseManager は「意思決定ケース」というドメインオブジェクトの
CRUD操作とビジネスルール（バリデーション、タグ付けロジック等）を
カプセル化するため、Domain Layer に配置されます。
Application Layer はユースケースのオーケストレーション、
Infrastructure Layer は外部サービス連携を担当します。
```

### Category 3: 依存関係
```
Q: タスク 2.2 (SimilarityEngine) を実装する前に完了している必要があるタスクは？

A) 3.1 DraftReviewService
B) 1.3 Qdrant セットアップ と 2.1 EmbeddingService ← 正解
C) 4.1 API エンドポイント
D) 5.1 フロントエンド画面

解説: SimilarityEngine は以下に依存します：
- Qdrant (1.3): ベクトル類似検索の実行先
- EmbeddingService (2.1): クエリテキストをベクトルに変換

これらが準備されていないと、SimilarityEngine のコア機能である
ハイブリッド検索（ベクトル + BM25）を実装できません。
```

### Category 4: データ設計
```
Q: decision_cases テーブルで failed_hypotheses を JSONB 型にした理由は？

A) PostgreSQL が JSONB しかサポートしていないから
B) 仮説の数や構造が可変であり、スキーマレスな柔軟性が必要だから ← 正解
C) パフォーマンスが最も高いから
D) 全文検索ができないから

解説: 失敗した仮説の数はケースによって異なり（0個〜複数個）、
各仮説の属性も将来変更される可能性があります。
JSONB を使うことで：
- 可変数の仮説を1カラムで格納
- スキーマ変更なしに属性追加可能
- GINインデックスでJSONB内検索も可能
```

### Category 5: API設計
```
Q: POST /api/draft-reviews のレスポンスに含まれるべきデータとして
   design.md の DraftReviewResponse に定義されているものは？

A) ユーザーのパスワード
B) 類似ケース、懸念点、生成された問い、レビュー進捗 ← 正解
C) データベースの接続文字列
D) サーバーのCPU使用率

解説: DraftReviewResponse インターフェース:
- similarCases: SimilarCase[] - 類似する過去のケース
- concernPoints: ConcernPoint[] - 抽出された懸念点
- questions: GeneratedQuestion[] - LLMが生成した問い
- reviewProgress: ReviewProgress - 回答進捗状況
```

### Category 6: 実装詳細
```
Q: EmbeddingService で OpenAI API の 429 (Rate Limit) エラーが発生した場合の
   適切な対処法は？

A) エラーをそのまま throw してユーザーに表示
B) 指数バックオフでリトライし、上限到達後はエラーを返す ← 正解
C) 無限にリトライし続ける
D) 別のAPIキーに自動切り替え

解説: Rate Limit 対策のベストプラクティス:
1. 指数バックオフ: 1秒 → 2秒 → 4秒 と待機時間を増やす
2. 最大リトライ回数を設定（例: 3回）
3. jitter（ランダムな遅延）を追加して thundering herd を防止
4. 上限到達後は適切なエラーを返し、ユーザーに再試行を促す

無限リトライはリソース枯渇、即座のエラー返却はUX低下を招きます。
```

## Critical Constraints
- **spec.json の言語設定に従う**
- **実装可能な知識**: 理論だけでなく実装に必要な具体的知識を確認
- **技術的根拠**: 正解の理由を技術的に説明
</instructions>

## Output Flow

### 1. クイズ開始の案内
```
🔧 エンジニアリング理解度クイズを開始します

対象: mex-app
問題数: 6問（カテゴリ別）
難易度: 実装者レベル

カテゴリ:
1. 技術選定
2. アーキテクチャ
3. 依存関係
4. データ設計
5. API設計
6. 実装詳細

準備ができたら始めましょう！
```

### 2. 問題出題（AskUserQuestion使用）

1問ずつ出題、回答を待つ。

### 3. 回答へのフィードバック

**正解の場合**:
```
✅ 正解！

[技術的補足]
追加で知っておくと良いポイント:
- 関連するベストプラクティス
- 実装時の Tips
```

**不正解の場合**:
```
❌ 不正解。正解は B でした。

[技術解説]
正解の技術的根拠:
- なぜこの選択が適切か
- 他の選択肢の問題点

[参考資料]
- design.md の該当セクション
- 関連する公式ドキュメント
```

### 4. 最終結果

```
📊 クイズ結果

正答率: 5/6 (83%)

カテゴリ別:
✅ 技術選定: 1/1
✅ アーキテクチャ: 1/1
✅ 依存関係: 1/1
✅ データ設計: 1/1
❌ API設計: 0/1
✅ 実装詳細: 1/1

⚠️ 復習推奨領域: API設計
- design.md の「Components and Interfaces」セクションを再確認
- FastAPI のレスポンスモデル定義を復習

📚 推奨リソース:
- FastAPI 公式ドキュメント: Response Model
- Pydantic V2 Data Validation
```

## Safety & Fallback

### Error Scenarios

**Spec が存在しない場合**:
- **Message**: "仕様 $1 が見つかりません"
- **Action**: `.kiro/specs/` 配下の利用可能な仕様を一覧表示

**途中終了の場合**:
- 途中結果を表示
- 続きから再開可能であることを案内
