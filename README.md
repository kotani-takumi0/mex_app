# MEX App - AI開発ポートフォリオ

AI支援開発の過程を記録・可視化するポートフォリオプラットフォームです。
MCPサーバーで開発ログを自動収集し、公開ポートフォリオとして共有できます。

**Overview**
MEX App は「完成物だけでは伝わらない開発の過程」を提示するためのアプリです。
プロジェクト単位で開発ログを蓄積し、公開ポートフォリオとして共有できます。
理解度チェック（クイズUI）は現在準備中です。

**Key Features**
- プロジェクト管理（ステータス、技術タグ、リポジトリ/デモURL、公開設定）
- 開発ログ（手動入力 + MCPサーバーによる自動記録）
- 理解度チェック（準備中）
- ダッシュボード（進捗サマリ、最近のプロジェクト、トップスキル）
- 公開ポートフォリオ（ユーザー別の公開ページとプロジェクト詳細）

**Routes**
| 画面 | パス | 説明 |
| --- | --- | --- |
| ランディング | `/` | 未認証ユーザー向けの紹介ページ |
| 認証 | `/auth` | ログイン/登録 |
| ダッシュボード | `/dashboard` | 進捗サマリとスキルスコア |
| 設定 | `/settings` | プロフィール編集・MCPトークン管理 |
| 新規プロジェクト | `/projects/new` | プロジェクト作成 |
| プロジェクト詳細 | `/projects/:id` | 開発ログ一覧・手動追加 |
| 理解度チェック | `/projects/:id/quiz` | 準備中 |
| 公開ポートフォリオ | `/p/:username` | 公開プロフィールとプロジェクト一覧 |
| 公開プロジェクト詳細 | `/p/:username/:projectId` | 開発ログとクイズ結果の公開表示 |

**Tech Stack**
- フロントエンド: React 19, TypeScript, React Router 7
- バックエンド: FastAPI, SQLAlchemy 2, Alembic
- データベース: PostgreSQL
- ベクトル検索: pgvector（PostgreSQL拡張）
- AI: OpenAI API
- MCPサーバー: Node.js + Model Context Protocol SDK
- 決済: Stripe（バックエンドのみ）

**Setup**
Step 1: `.env` を用意します。
```bash
cp .env.example .env
```
`OPENAI_API_KEY` を設定してください。

Step 2: PostgreSQL を起動します。
```bash
docker compose up -d
```
**補足（起動できない場合）**
- `docker compose` が使えず `unknown shorthand flag: 'd' in -d` が出る場合、Composeプラグインが入っていません。
  - 既に `mex-postgres` コンテナがあるなら:
    ```bash
    docker start mex-postgres
    ```
  - ない場合は Compose を導入するか、旧 `docker-compose` を使ってください。
    ```bash
    # Ubuntu/Debian例
    sudo apt-get update
    sudo apt-get install docker-compose-plugin
    # 旧コマンドを使う場合
    sudo apt-get install docker-compose
    ```

Step 3: バックエンドをセットアップします。
```bash
cd backend
pip install -e ".[dev]"
alembic upgrade head
```

Step 4: フロントエンドをセットアップします。
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
AIツールから開発ログを自動記録する場合は MCP サーバーを設定します。
詳しい手順は `MCP_SERVER.md` を参照してください。
トークンはログイン後、`/settings` から発行できます。

```bash
# セットアップ（対話形式でトークン取得 + 設定ファイル作成）
npx mex-setup

# Claude Code の MCP 設定に登録（~/.claude/mcp_servers.json）
# { "mex": { "command": "npx", "args": ["mex-mcp-server"] } }
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
