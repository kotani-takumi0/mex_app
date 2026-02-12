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

AI ツール（Claude Code）から開発ログを自動記録する場合は MCP サーバーを設定します。
初回のセットアップは 3 ステップで、一度だけ行えば以降はどのプロジェクトでも使えます。

**前提条件**
- MEX App のアカウントを作成済みであること（`/auth` で新規登録）
- MEX App のバックエンドが起動していること（別ターミナルで `uvicorn app.main:app --reload`）
- Node.js がインストールされていること

**Step 1: ユーザー認証の設定**（初回のみ・どのディレクトリで実行しても OK）

```bash
npx -p mex-mcp-server mex-setup
```

対話形式で以下の質問に回答します：

| 質問 | 入力内容 |
|---|---|
| API URL | そのまま Enter（ローカル開発なら `http://localhost:8000/api` でOK） |
| メールアドレス | MEX App に登録済みのメールアドレス |
| パスワード | MEX App に登録済みのパスワード |
| AI Tool名 | そのまま Enter（デフォルト `claude_code`） |

成功すると `~/.mex/config.json` が自動生成されます。これは API の認証情報を保持するファイルで、全プロジェクト共通で使われます。

**Step 2: Claude Code に MCP サーバーを登録**（プロジェクトごとに 1 回）

MCP サーバーを使いたいプロジェクトのディレクトリで以下を実行します：

```bash
cd ~/your-project
claude mcp add mex -s project -- npx mex-mcp-server
```

これで `.claude/mcp_server.json` が自動生成されます。

**Step 3: Claude Code を起動して MCP を承認**

```bash
claude
```

初回起動時に MCP サーバーの接続許可を求められるので、承認してください。
`/mcp` コマンドで `mex` が表示されればセットアップ完了です。

**仕組み: 自動生成される設定ファイル**

すべてコマンドが自動で作成するため、手動でファイルを作る必要はありません。

```
ホームディレクトリ（全プロジェクト共通）
  ~/.mex/config.json              ← Step 1 で自動生成（API認証情報）

各プロジェクト（プロジェクトごと）
  ~/your-project/.claude/mcp_server.json  ← Step 2 で自動生成（MCPサーバー登録）
  ~/your-project/.mex.json                ← /document 初回実行時に自動生成（プロジェクトID）
```

| ファイル | 作成コマンド | 役割 |
|---|---|---|
| `~/.mex/config.json` | `npx -p mex-mcp-server mex-setup` | API URL + 認証トークン（30日間有効） |
| `.claude/mcp_server.json` | `claude mcp add mex ...` | Claude Code にどの MCP サーバーを使うか教える |
| `.mex.json` | `/document` 初回実行時 | MEX App 上のプロジェクト ID を保持 |

複数のプロジェクトで使う場合、Step 1 は一度だけで OK です。
新しいプロジェクトでは Step 2 → Step 3 を行うだけで使えます。

詳しくは `MCP_SERVER.md` を参照してください。

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
