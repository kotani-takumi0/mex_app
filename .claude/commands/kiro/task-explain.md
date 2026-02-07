---
description: Explain a task from an engineer's implementation perspective
allowed-tools: Read, Glob, Grep
argument-hint: <feature-name> <task-number>
---

# Task Explainer (Engineer's Perspective)

<background_information>
- **Mission**: 指定されたタスクをエンジニア視点で解説し、実装に必要な技術知識を提供する
- **Success Criteria**:
  - 具体的な実装アプローチが理解できる
  - 使用する技術・ライブラリの選定理由が分かる
  - コードレベルでの設計判断が説明される
  - 他のエンジニアに実装方針を説明できる
</background_information>

<instructions>
## Core Task
指定された機能 **$1** のタスク **$2** を、エンジニアが実装に着手できるレベルで技術解説する。

## Execution Steps

### Step 1: コンテキストの読み込み

**必要なファイルを全て読み込む**:
- `.kiro/specs/$1/tasks.md` - タスク一覧
- `.kiro/specs/$1/requirements.md` - 要件定義
- `.kiro/specs/$1/design.md` - 設計ドキュメント（インターフェース定義含む）
- `.kiro/specs/$1/spec.json` - 仕様メタデータ
- `.kiro/steering/` ディレクトリ全体 - プロジェクトコンテキスト

### Step 2: 技術実装の分析

**タスクの技術スコープを特定**:
- 実装するコンポーネント/モジュール名
- 作成するファイル・ディレクトリ
- 実装するクラス/関数のシグネチャ
- 依存する外部ライブラリ

**design.md からインターフェース定義を抽出**:
- 実装すべきインターフェース（TypeScript/Python型定義）
- 入出力のデータ構造
- エラーハンドリングパターン

**データフローを分析**:
- このコンポーネントが受け取るデータ
- 内部での処理ロジック
- 出力するデータと呼び出し先

### Step 3: 実装詳細の解説

**使用技術の技術的背景**:
- なぜこの技術/ライブラリを選んだか
- 代替案との比較（トレードオフ）
- 設定やパラメータの意味

**コードパターンと設計判断**:
- 推奨されるデザインパターン
- エラーハンドリング戦略
- テスト容易性の考慮

### Step 4: 実装上の注意点

**よくある落とし穴**:
- パフォーマンスの罠
- セキュリティ上の注意点
- 外部サービス連携時の考慮事項

**デバッグのヒント**:
- 確認すべきログポイント
- テストデータの準備方法

## Critical Constraints
- **spec.json の言語設定に従う**
- **コードレベルの具体性**: 抽象的な説明ではなく、実装可能な詳細度
- **技術的正確性**: ライブラリのバージョンやAPI仕様を正確に
</instructions>

## Output Description

指定言語で以下の構造で説明を提供:

### 1. タスクサマリー
```
タスク: 2.1 埋め込み生成サービスの実装
スコープ: Domain Layer / EmbeddingService
作成ファイル: backend/src/domain/embedding_service.py
依存: openai>=1.0.0, qdrant-client>=1.7.0
```

### 2. 実装するインターフェース

design.md から抽出した型定義:
```typescript
interface EmbeddingService {
  generateEmbedding(text: string): Promise<Result<number[], EmbeddingError>>;
  batchGenerateEmbeddings(texts: string[]): Promise<Result<number[][], EmbeddingError>>;
}
```

Python実装の場合の対応:
```python
class EmbeddingService(Protocol):
    async def generate_embedding(self, text: str) -> Result[list[float], EmbeddingError]: ...
    async def batch_generate_embeddings(self, texts: list[str]) -> Result[list[list[float]], EmbeddingError]: ...
```

### 3. 技術スタック詳細

| 技術 | バージョン | 用途 | 選定理由 |
|------|-----------|------|----------|
| OpenAI API | v1.x | 埋め込み生成 | text-embedding-3-large で 3072次元、高精度 |
| httpx | 0.27+ | HTTP クライアント | 非同期対応、リトライ機能 |

**代替案との比較**:
- Sentence Transformers: ローカル実行可能だが精度・次元数で劣る
- Cohere Embed: 品質は同等だがOpenAIエコシステムとの統一性

### 4. 実装アプローチ

**ディレクトリ構造**:
```
backend/
└── src/
    └── domain/
        ├── embedding_service.py      # 本タスクで実装
        ├── embedding_service_test.py # ユニットテスト
        └── __init__.py
```

**主要な実装ポイント**:

1. **API呼び出しの実装**
   ```python
   # OpenAI クライアントの初期化
   client = AsyncOpenAI(api_key=settings.openai_api_key)

   # 埋め込み生成
   response = await client.embeddings.create(
       model="text-embedding-3-large",
       input=text,
       dimensions=3072  # 明示的に指定
   )
   ```

2. **リトライロジック**
   - 429 (Rate Limit): 指数バックオフで最大3回リトライ
   - 500系: 即座に1回リトライ後、フォールバック

3. **エラーハンドリング**
   ```python
   class EmbeddingError(Enum):
       RATE_LIMITED = "rate_limited"
       API_ERROR = "api_error"
       INVALID_INPUT = "invalid_input"
   ```

### 5. 依存関係と前提条件

**このタスクが依存するもの**:
- タスク 1.1: プロジェクト構造（Poetryによる依存管理）
- 環境変数: `OPENAI_API_KEY`

**このタスクに依存するもの**:
- タスク 2.2: SimilarityEngine がクエリ埋め込み生成に使用
- タスク 2.3: CaseManager が新規ケース登録時に使用

### 6. テスト戦略

**ユニットテスト**:
```python
@pytest.mark.asyncio
async def test_generate_embedding_success():
    # OpenAI API をモック
    with patch("openai.AsyncOpenAI") as mock_client:
        mock_client.embeddings.create.return_value = MockResponse(...)

        service = EmbeddingService(mock_client)
        result = await service.generate_embedding("test text")

        assert result.is_ok()
        assert len(result.unwrap()) == 3072
```

**統合テスト観点**:
- 実際のOpenAI APIへの疎通確認（CI/CDでスキップ可能に）
- レート制限時の挙動確認

### 7. 実装チェックリスト

- [ ] `EmbeddingService` クラスの実装
- [ ] `generate_embedding()` メソッド実装
- [ ] `batch_generate_embeddings()` メソッド実装
- [ ] リトライロジック実装
- [ ] エラー型定義
- [ ] ユニットテスト作成
- [ ] 環境変数のバリデーション

### 8. 参考リソース

- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [text-embedding-3-large モデル仕様](https://platform.openai.com/docs/models/embeddings)

## Safety & Fallback

### Error Scenarios

**タスクが見つからない場合**:
- **Message**: "タスク $2 が `.kiro/specs/$1/tasks.md` に見つかりません"
- **Action**: 利用可能なタスク番号の一覧を表示

**design.md にインターフェース定義がない場合**:
- **Warning**: "このタスクの詳細なインターフェース定義が見つかりません"
- **Fallback**: タスク説明から推測されるインターフェースを提示
