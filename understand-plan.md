# MEX App コードベース理解ドキュメント設計書

> `/understand` スキル実行時のドキュメント生成計画。
> 各モジュールのNotionドキュメント構造（技術分解・解説・Q&A）の設計を記録する。

## 共通設定

| 項目 | 値 |
|------|-----|
| Notion親ページ | `mex_app MEX Docs`（`30ccfdc5-7d99-811c-bde1-cc1df9568040`） |
| project_id | `1103ef1e-a074-467e-9d58-166bce39e7f6` |
| category | `learning`（全モジュール共通） |
| タイトル形式 | `[Understand] {モジュール名}` |

## プロジェクト概要

**プロジェクトタイプ**: React 19 + FastAPI + Node.js モノレポ
**総コード行数**: 約5,500行（Python + TypeScript + TSX）
**ファイル分布**: バックエンド53ファイル、フロントエンド63ファイル、MCPサーバー8ファイル

---

## Module 1: 認証システム

**対象ファイル**:
- `backend/app/auth/jwt.py` — JWT生成・検証
- `backend/app/auth/dependencies.py` — FastAPI認証依存関係
- `backend/app/auth/plan_guards.py` — プラン制限ガード
- `backend/app/api/auth.py` — 認証APIエンドポイント

**使用技術**: PyJWT, bcrypt/passlib, FastAPI Depends

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| JWT（PyJWT） | コア | HS256アルゴリズム, 60分有効期限, planクレーム埋込, MCPトークン30日有効 |
| bcrypt（passlib） | コア | パスワードハッシュ化, CryptContextパターン |
| FastAPI Depends | コア | 依存性注入チェーン, HTTPBearer, get_current_user_dependency |
| プラン制御（plan_guards） | コア | Free: 2プロジェクト上限, DB側planを正とする設計判断 |
| MCPトークン管理 | 補助 | SHA-256ハッシュ保存, revoke機構, フェイルクローズ原則 |
| パスワードバリデーション | 補助 | 10文字以上, 4種文字要件, Pydantic field_validator |

### Q&A方針

- **基礎**: JWTの構造と署名検証、bcryptのソルト生成
- **判断**: 60分有効期限の設計理由、DB側planを正とする判断（JWTはトークン発行時点の値）、MCPトークンのフェイルクローズ
- **応用**: レート制限値（登録5/min, ログイン10/min）、トークン漏洩時の対応

---

## Module 2: API Layer

**対象ファイル**:
- `backend/app/api/projects.py` — プロジェクトCRUD
- `backend/app/api/devlogs.py` — 開発ログCRUD
- `backend/app/api/dashboard.py` — ダッシュボード集計
- `backend/app/api/billing.py` — Stripe決済
- `backend/app/api/portfolio.py` — 公開ポートフォリオ

**使用技術**: FastAPI, Pydantic, Stripe, slowapi

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| FastAPI APIRouter | コア | prefix/tagsによるモジュール分離、ルーター登録 |
| Pydantic スキーマ | コア | リクエスト/レスポンスバリデーション、型安全 |
| Stripe Checkout + Webhook | コア | 冪等性保証（StripeWebhookEvent）, Customer Portal |
| 公開ポートフォリオAPI | 補助 | username正規表現検証, is_publicフィルタリング |
| レート制限（slowapi） | 補助 | Webhook 30/min, 登録5/min |

### Q&A方針

- **基礎**: FastAPI APIRouterの役割、Pydanticバリデーション
- **判断**: Stripe Webhookの冪等性保証の必要性、ポートフォリオの認証なしアクセス設計
- **応用**: Webhook署名検証の仕組み、レート制限の攻撃耐性

---

## Module 3: Application Services

**対象ファイル**:
- `backend/app/application/project_service.py` — プロジェクト管理
- `backend/app/application/devlog_service.py` — 開発ログ管理
- `backend/app/application/billing_service.py` — 決済管理
- `backend/app/application/usage_service.py` — ダッシュボード統計

**使用技術**: SQLAlchemy, Dataclasses, Stripe API

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| サービスレイヤーパターン | コア | API↔DB間のビジネスロジック分離、関心の分離 |
| DataclassベースDTO | コア | ProjectCreate/Update, DevLogCreate/Update、不変データ転送 |
| シークレット検出統合 | コア | DevLogService内でSecretDetector.mask()を呼び出す設計 |
| Stripe BillingService | コア | Checkout/Portal/Webhook処理, プラン自動切替 |
| DashboardService | 補助 | 統計集計, notebook_idによるノートブックカウント |

### Q&A方針

- **基礎**: サービスレイヤーパターンの定義と利点
- **判断**: シークレット検出をDevLogServiceに統合した理由、BillingServiceのプラン自動切替フロー
- **応用**: Stripe Webhook失敗時のプラン不整合、セッション管理のtry/finally

---

## Module 4: Domain Services

**対象ファイル**:
- `backend/app/domain/llm/llm_service.py` — LLMサービス
- `backend/app/domain/embedding/embedding_service.py` — 埋め込み生成
- `backend/app/domain/similarity/similarity_engine.py` — 類似検索
- `backend/app/domain/security/secret_detector.py` — シークレット検出

**使用技術**: OpenAI API, pgvector, 正規表現

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| OpenAI LLMService | コア | for_plan()ファクトリ, Free:gpt-4o-mini / Pro:gpt-4o |
| EmbeddingService | コア | text-embedding-3-small, 1536次元, バッチ処理対応 |
| pgvector類似検索 | コア | コサイン距離（<=>演算子）, SQL直接実行, フィルター付き |
| SecretDetector | コア | 10+パターン正規表現, mask/detect/has_secrets |
| エクスポネンシャルバックオフ | 補助 | リトライロジック, 2^attempt * delay |

### Q&A方針

- **基礎**: embeddingとは何か、コサイン距離の意味
- **判断**: text-embedding-3-smallを選んだ理由（コスト最適化）, pgvectorとQdrantの移行判断, for_plan()ファクトリの設計
- **応用**: シークレット検出パターンの網羅性と誤検知、バッチ埋め込みのトークン分配

---

## Module 5: Infrastructure/DB

**対象ファイル**:
- `backend/app/infrastructure/database/models.py` — 6テーブル定義
- `backend/app/infrastructure/database/session.py` — セッション管理
- `backend/app/config.py` — アプリケーション設定
- `backend/app/main.py` — FastAPIエントリーポイント

**使用技術**: SQLAlchemy 2.0, pgvector, Alembic, pydantic-settings, Sentry

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| SQLAlchemy 2.0 ORM | コア | DeclarativeBase, 6テーブル（User, Project, DevLogEntry, UsageLog, Subscription, MCPToken, StripeWebhookEvent）, リレーション |
| pgvector統合 | コア | Vector(1536), devlog_entriesのembeddingカラム |
| コネクションプール | コア | 本番:pool_size=5, max_overflow=3 / 開発:20+10, pool_recycle差異 |
| pydantic-settings | コア | 環境変数管理, 本番バリデーション（JWT秘密鍵32文字以上チェック） |
| セキュリティヘッダー | 補助 | nosniff, DENY, HSTS, SecurityHeadersMiddleware |
| CORS設定 | 補助 | カンマ区切りパース, 明示的メソッド/ヘッダー指定 |

### Q&A方針

- **基礎**: ORMの役割、コネクションプールの概念
- **判断**: 本番/開発でプール設定を変える理由（Render Starterの接続数制限）、metadata_命名の理由（SQLAlchemy予約語回避）
- **応用**: 本番バリデーターによる起動時チェック、cascade="all, delete-orphan"の影響

---

## Module 6: Performance & Monitoring

**対象ファイル**:
- `backend/app/performance/rate_limiter.py` — レート制限
- `backend/app/performance/semantic_cache.py` — セマンティックキャッシュ
- `backend/app/performance/concurrent_handler.py` — 同時リクエスト制御
- `backend/app/performance/metrics.py` — メトリクス収集
- `backend/app/performance/search_benchmark.py` — 検索ベンチマーク

**使用技術**: slowapi, asyncio.Semaphore, Sentry

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| slowapiレート制限 | コア | スライディングウィンドウ, エンドポイント別設定 |
| セマンティックキャッシュ | コア | TTL+類似度マッチング, embedding結果キャッシュでAPI費用削減 |
| セマフォ制御 | 補助 | asyncio.Semaphore, 同時リクエスト上限 |
| メトリクス収集 | 補助 | パーセンタイル計算（p50/p90/p99）, パフォーマンストラッキング |
| Sentry統合 | 補助 | DSN設定時のみ有効化, traces_sample_rate=0.1 |

### Q&A方針

- **基礎**: レート制限の目的、セマンティックキャッシュとは
- **判断**: セマンティックキャッシュの有効性判断、Sentryサンプリングレート0.1の根拠
- **応用**: 高負荷時のセマフォ挙動、キャッシュ無効化戦略

---

## Module 7: Frontend Pages & Routes

**対象ファイル**:
- `frontend/src/App.tsx` — ルーティング定義
- `frontend/src/components/Auth/AuthPage.tsx` — 認証ページ
- `frontend/src/components/Dashboard/DashboardPage.tsx` — ダッシュボード
- `frontend/src/components/Projects/ProjectDetailPage.tsx` — プロジェクト詳細
- `frontend/src/components/Projects/ProjectFormPage.tsx` — プロジェクト作成/編集
- `frontend/src/components/Portfolio/PublicPortfolioPage.tsx` — 公開ポートフォリオ

**使用技術**: React 19, React Router 7, react-hot-toast

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| React Router 7 | コア | BrowserRouter, Routes, Route, Navigate, useParams |
| ルートガードパターン | コア | PublicRoute（認証済み→/dashboard）, ProtectedRoute（未認証→/auth） |
| AuthenticatedLayout | コア | Navigation + main + UsernameSetupModal ラッパー |
| ProjectDetailPage | コア | ドキュメントCRUD, 学習ハブ, 公開トグル, 編集モーダル |
| 公開ポートフォリオ | 補助 | /p/:username, 認証不要, CTAフッター |

### Q&A方針

- **基礎**: SPAルーティングの仕組み、ルートガードの役割
- **判断**: PublicRoute/ProtectedRouteの分離設計、AuthenticatedLayoutの責務
- **応用**: ProjectDetailPageの「学んだこと」欄の設計意図（AIは入力しない）、ルートフォールバック

---

## Module 8: Frontend Components

**対象ファイル**:
- `frontend/src/components/common/Navigation.tsx` — ナビゲーション
- `frontend/src/components/common/PageHeader.tsx` — ページヘッダー
- `frontend/src/components/common/EmptyState.tsx` — 空状態表示
- `frontend/src/components/common/LoadingSkeleton.tsx` — スケルトンローディング
- `frontend/src/components/common/ErrorBoundary.tsx` — エラーバウンダリ
- `frontend/src/components/common/UsernameSetupModal.tsx` — ユーザー名設定モーダル
- `frontend/src/components/common/UpgradePrompt.tsx` — アップグレード促進

**使用技術**: React 19, react-icons, CSS

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| Navigation | コア | スティッキーヘッダー, ハンバーガーメニュー, プランバッジ |
| スケルトンローディング | コア | DashboardSkeleton, shimmerアニメーション |
| ErrorBoundary | コア | Reactクラスコンポーネント, フォールバックUI |
| UsernameSetupModal | 補助 | 初回設定, 正規表現バリデーション, 公開URLプレビュー |
| UpgradePrompt | 補助 | Proプランアップセル, Stripe Checkout連携 |
| EmptyState | 補助 | 汎用「データなし」UI, icon+title+description+action |

### Q&A方針

- **基礎**: コンポーネント再利用の考え方、Propsによるカスタマイズ
- **判断**: ErrorBoundaryがクラスコンポーネントである理由（React APIの制約）、スケルトンローディングのUX効果
- **応用**: UsernameSetupModalの表示条件判定、UpgradePromptのStripe連携フロー

---

## Module 9: Frontend API Client

**対象ファイル**:
- `frontend/src/api/client.ts` — HTTPクライアントコア
- `frontend/src/api/auth.ts` — 認証API
- `frontend/src/api/projects.ts` — プロジェクトAPI
- `frontend/src/api/devlogs.ts` — 開発ログAPI
- `frontend/src/api/dashboard.ts` — ダッシュボードAPI
- `frontend/src/api/portfolio.ts` — ポートフォリオAPI
- `frontend/src/api/billing.ts` — 決済API

**使用技術**: Fetch API, TypeScript, localStorage

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| HTTPクライアント（Fetch API） | コア | apiGet/Post/Put/Delete, Content-Type自動設定 |
| トークン管理 | コア | localStorage永続化 + in-memoryキャッシュ, setAuthToken/clearAuthToken |
| レスポンスエンベロープ | コア | `{data, error, status}` 統一形式, 型安全 |
| DevLogsデータ変換 | コア | backend entry_type→frontend category, summary→title マッピング |
| カスタムイベント（auth-error） | 補助 | 401自動ログアウト, window.dispatchEvent |

### Q&A方針

- **基礎**: Fetch APIの基本、レスポンスエンベロープパターンの利点
- **判断**: axiosではなくFetch APIを選んだ理由、auth-errorイベントバスの設計
- **応用**: entry_type↔categoryマッピングの拡張性、トークン期限切れ時のUX

---

## Module 10: Frontend Design System

**対象ファイル**:
- `frontend/src/design-tokens.css` — デザイントークン
- `frontend/src/global.css` — グローバルスタイル
- `frontend/src/index.css` — エントリーCSS

**使用技術**: CSS Custom Properties, Google Fonts

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| CSS Custom Properties | コア | カラー/タイポグラフィ/スペーシング/シャドウの一元管理 |
| タイポグラフィ設計 | コア | Sora+Zen Kaku Gothic New（見出し）, Plus Jakarta Sans+Zen Kaku Gothic New（本文） |
| グレインテクスチャ | コア | body::after, SVGノイズフィルター（feTurbulence） |
| AIスロップ排除ルール | コア | translateYホバー禁止, 135deg禁止, ease禁止, rgba(0,0,0)影禁止 |
| アニメーション設計 | 補助 | cubic-bezier(0.22,0.61,0.36,1), 11種keyframe, prefers-reduced-motion |

### Q&A方針

- **基礎**: デザイントークンとは何か、CSS Custom Propertiesの仕組み
- **判断**: CSS-in-JSではなくCSS Custom Propertiesを選んだ理由、AIスロップ排除の具体的な代替手法
- **応用**: prefers-reduced-motionアクセシビリティ対応、フォントフォールバック戦略

---

## Module 11: MCP Server

**対象ファイル**:
- `mcp-server/src/index.ts` — サーバーエントリーポイント
- `mcp-server/src/config.ts` — 設定読み込み
- `mcp-server/src/api-client.ts` — MEX App APIクライアント
- `mcp-server/src/tools/record-activity.ts` — save_documentツール
- `mcp-server/src/tools/list-projects.ts` — list_projectsツール
- `mcp-server/src/tools/get-context.ts` — get_project_contextツール
- `mcp-server/src/tools/save-notebook.ts` — save_notebookツール
- `mcp-server/src/cli/setup.ts` — セットアップCLI

**使用技術**: Node.js, @modelcontextprotocol/sdk, TypeScript

### 技術分解

| 技術要素 | 解説の深さ | モジュールにおける役割 |
|---------|---------|-----------------|
| Model Context Protocol SDK | コア | Server, StdioServerTransport, ListToolsRequest/CallToolRequest |
| 4つのMCPツール | コア | save_document, list_projects, get_project_context, save_notebook |
| config.ts二重設計 | コア | ~/.mex/config.json（グローバル認証）+ .mex.json（プロジェクト単位ID） |
| MexApiClient | コア | fetch, Bearer認証, request<T>ジェネリック, エラーハンドリング |
| セットアップCLI | 補助 | ログイン→APIトークン取得→config.json自動生成（離脱防止） |

### Q&A方針

- **基礎**: MCPプロトコルとは何か、StdioServerTransportの仕組み
- **判断**: config二重構造（グローバル+ローカル）の設計判断、セットアップCLI実装の背景（3つのAIレビューの指摘）
- **応用**: MCPツール追加の拡張方法、トークン期限切れ時のエラーハンドリング

---

## 生成フロー

```
1. Notionページ作成（11件 × notion-create-pages）
2. MEX App記録（11件 × save_document）
3. 結果報告
```

各モジュールのドキュメントは `/understand` スキルの品質制約に従い:
- 実装コードの具体的な設定値・ライブラリ名・関数名・ファイルパスを引用
- Q&Aは各段階最低2問、合計6問以上
- セキュリティ関連技術を含むモジュールにはセキュリティQ&Aを追加
