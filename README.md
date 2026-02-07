# MEX App - AI開発ポートフォリオ

AI支援開発の過程と理解度を記録・可視化するポートフォリオプラットフォームです。
MCPサーバーで開発ログを自動収集し、ログから4択クイズを生成して理解度を測定します。

**Overview**
MEX App は「完成物だけでは伝わらない開発の過程」と「技術理解度」を一緒に提示するためのアプリです。
プロジェクト単位で開発ログを蓄積し、クイズ結果からスキルスコアを算出して公開ポートフォリオとして共有できます。

**Key Features**
- プロジェクト管理（ステータス、技術タグ、リポジトリ/デモURL、公開設定）
- 開発ログ（手動入力 + MCPサーバーによる自動記録）
- 4択クイズ生成（開発ログから問題生成、回答でスキルスコア更新）
- ダッシュボード（進捗サマリ、最近のプロジェクト、トップスキル）
- 公開ポートフォリオ（ユーザー別の公開ページとプロジェクト詳細）

**Routes**
| 画面 | パス | 説明 |
| --- | --- | --- |
| ランディング | `/` | 未認証ユーザー向けの紹介ページ |
| 認証 | `/auth` | ログイン/登録 |
| ダッシュボード | `/dashboard` | 進捗サマリとスキルスコア |
| 新規プロジェクト | `/projects/new` | プロジェクト作成 |
| プロジェクト詳細 | `/projects/:id` | 開発ログ一覧・手動追加 |
| 理解度チェック | `/projects/:id/quiz` | クイズ生成と回答 |
| 公開ポートフォリオ | `/p/:username` | 公開プロフィールとプロジェクト一覧 |
| 公開プロジェクト詳細 | `/p/:username/:projectId` | 開発ログとクイズ結果の公開表示 |

**Tech Stack**
- フロントエンド: React 19, TypeScript, React Router 7
- バックエンド: FastAPI, SQLAlchemy 2, Alembic
- データベース: PostgreSQL
- ベクトルDB: Qdrant
- AI: OpenAI API
- MCPサーバー: Node.js + Model Context Protocol SDK
- 決済: Stripe（バックエンドのみ）

**Setup**
Step 1: `.env` を用意します。
```bash
cp .env.example .env
```
`OPENAI_API_KEY` を設定してください。Qdrant を Cloud で使う場合は `QDRANT_URL` と `QDRANT_API_KEY` も指定します。

Step 2: PostgreSQL を起動します。
```bash
docker compose up -d
```

Step 3: Qdrant を起動します。
```bash
docker run -d --name mex-qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

Step 4: バックエンドをセットアップします。
```bash
cd backend
pip install -e ".[dev]"
alembic upgrade head
```

Step 5: フロントエンドをセットアップします。
```bash
cd frontend
npm install
```

**Run**
バックエンド（port 8000）:
```bash
cd backend
uvicorn app.main:app --reload
```

フロントエンド（port 3000）:
```bash
cd frontend
npm start
```

**MCP Server (Optional)**
AIツールから開発ログを自動記録する場合は `mcp-server` を起動します。
詳しい手順は `MCP_SERVER.md` を参照してください。

```bash
cd mcp-server
npm install
npm run build
npm run start
```

**Dev Commands**
```bash
# Backend
cd backend
pytest
ruff check app/
ruff check app/ --fix

# Frontend
cd frontend
npm run build
npm test
npm run lint
```
