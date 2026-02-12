# MEX App 技術理解ロードマップ

MEX App を技術的に理解するための段階的学習プラン。
各フェーズで Todo アプリを拡張しながら、MEX App で使われている技術を一つずつ習得する。

## 全体像

```
Phase 1  →  Phase 2  →  Phase 3  →  Phase 4
React基礎    API連携    FastAPI     応用技術
(1-2週間)    (1週間)    (1-2週間)   (随時)
  ↓            ↓          ↓           ↓
 Todo App    Todo+API   Todo+DB    MEX App読解
```

---

## Phase 1: フロントエンド基礎（Todo アプリ）

**目標**: React の基本的な開発パターンを習得する

| トピック | MEX App での実例 |
|---|---|
| JSX / コンポーネント分割 | PageHeader, EmptyState, TodoItem 等 |
| useState / useEffect | フォーム入力、データ取得 |
| React Router でページ遷移 | `/dashboard`, `/projects/:id` |
| CSS Custom Properties | `design-tokens.css` のトークン設計 |
| フォーム + バリデーション | 認証フォーム、プロジェクト作成フォーム |
| react-hot-toast | 成功/エラー通知 |

**やること**: Vite + React + TypeScript で Todo アプリを構築する

**完了基準**: Todo アプリが完成し、React の基本操作に迷いがなくなる

---

## Phase 2: API 連携（Todo アプリ拡張）

**目標**: フロントエンドとバックエンドの繋ぎ方を理解する

| トピック | MEX App での実例 |
|---|---|
| fetch / async-await | API からデータ取得 |
| REST API の基本（GET/POST/PUT/DELETE） | `/api/projects`, `/api/devlogs` |
| ローディング / エラーハンドリング | Skeleton UI, ErrorBoundary |
| 認証ヘッダー（Bearer トークン） | `Authorization: Bearer <JWT>` |
| PublicRoute / ProtectedRoute | 認証状態によるルート制御 |

**やること**: Todo アプリに簡易バックエンド（FastAPI）を追加し、localStorage を API に置き換える

**完了基準**: フロントエンドから API を叩いて CRUD 操作ができる

---

## Phase 3: バックエンド基礎（FastAPI）

**目標**: MEX App のバックエンド構成を理解する

| トピック | MEX App での実例 |
|---|---|
| FastAPI のルーター・エンドポイント定義 | `api/auth.py`, `api/projects.py` |
| Pydantic でリクエスト/レスポンス型定義 | 各エンドポイントの入出力スキーマ |
| 依存性注入（`Depends`） | `get_current_user`, `get_db` |
| SQLAlchemy ORM（テーブル定義・CRUD） | `models.py` の 11 テーブル |
| JWT 認証の仕組み | `auth/jwt.py` でトークン生成・検証 |
| パスワードハッシュ（bcrypt） | `passlib` でのハッシュ化 |

**やること**: Todo アプリのバックエンドを FastAPI + SQLAlchemy + PostgreSQL で構築する

**完了基準**: 認証付きの REST API を自力で構築できる

---

## Phase 4: MEX App 固有の応用技術

Phase 1〜3 が理解できれば、MEX App のコードの **約 8 割** は読めるようになる。
残りの 2 割が以下の応用技術。

| トピック | 難易度 | MEX App での使い方 |
|---|---|---|
| Stripe 決済連携 | 中 | Checkout Session, Webhook, 冪等性保証 |
| OpenAI API + クイズ自動生成 | 中 | `quiz_service.py` で LLM にプロンプトを投げる |
| pgvector（ベクトル検索） | 高 | DevLog の埋め込みベクトルで類似検索 |
| Alembic（DB マイグレーション） | 低 | スキーマ変更の管理 |
| レート制限（slowapi） | 低 | API の過負荷防止 |
| セキュリティヘッダー | 低 | CORS, HSTS, XSS 対策 |

**やること**: MEX App のコードを読みながら、各機能を `/document` で記録していく

**完了基準**: MEX App の各機能を技術的に説明できる

---

## 学習のコツ

- 各フェーズの作業は **ステップごとにコミット** → `/document` で技術ドキュメントを生成する
- 分からない箇所は MEX App の対応するコードを読んで比較する
- Phase 4 は順序不問。興味のある技術から取り組む
