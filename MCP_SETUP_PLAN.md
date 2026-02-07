# MCPサーバー接続 実装計画

## 現状

| コンポーネント | 状態 |
|--------------|------|
| バックエンドAPI（projects, devlogs） | 実装済み・ルーター登録済み |
| DBモデル・マイグレーション | 適用済み（projects, devlog_entries等のテーブル存在確認済み） |
| PostgreSQL / Qdrant | Docker起動中 |
| MCPサーバーソースコード | `mcp-server/src/` に実装済み |
| MCPサーバービルド | `mcp-server/dist/` にコンパイル済み |
| **`mcp_servers.json`** | **パスがプレースホルダーのまま** |
| **`~/.mex/config.json`** | **存在しない** |

## やるべきこと（2つだけ）

### タスク1: `~/.mex/config.json` を作成する

MCPサーバーは起動時に `~/.mex/config.json` を読み込む（`mcp-server/src/config.ts:12`）。
このファイルが存在しないため、MCPサーバーが即座にクラッシュする。

#### 作成する内容

```bash
mkdir -p ~/.mex
```

```json
{
  "api_url": "http://localhost:8000/api",
  "api_key": "<JWTトークン>",
  "ai_tool": "claude_code"
}
```

#### `api_key` の取得方法

`api_key` には有効なJWTトークンが必要。以下のいずれかで取得する:

**方法A: curlで登録してトークンを取得**

```bash
# 新規ユーザー登録（既存ユーザーがいない場合）
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "password123", "display_name": "Demo User"}'

# レスポンスの access_token をコピー
```

**方法B: ログインしてトークン取得**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "password123"}'
```

**注意**: 現在のJWT有効期限は60分（`backend/app/config.py:45`）。
MCPサーバー用にはもっと長い有効期限のトークンが望ましいが、現状は都度再発行で対応する。

#### 前提条件

バックエンドが `http://localhost:8000` で起動していること:

```bash
cd backend
uvicorn app.main:app --reload
```

### タスク2: `.claude/mcp_servers.json` のパスを修正する

#### 現在の内容（`.claude/mcp_servers.json`）

```json
{
  "mex": {
    "command": "node",
    "args": ["/path/to/mex_app/mcp-server/dist/index.js"],
    "env": {}
  }
}
```

#### 修正後

```json
{
  "mex": {
    "command": "node",
    "args": ["/home/takumi/mex_app/mcp-server/dist/index.js"],
    "env": {}
  }
}
```

`/path/to/` → `/home/takumi/` に変更するだけ。

---

## 動作確認手順

上記2タスク完了後、以下の手順で動作確認する。

### 手順1: バックエンドを起動

```bash
cd /home/takumi/mex_app/backend
uvicorn app.main:app --reload
```

### 手順2: ユーザー登録 + トークン取得 + config.json作成

```bash
# ユーザー登録（初回のみ）
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "password123", "display_name": "Demo User"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# config.json 作成
mkdir -p ~/.mex
cat > ~/.mex/config.json << EOF
{
  "api_url": "http://localhost:8000/api",
  "api_key": "$TOKEN",
  "ai_tool": "claude_code"
}
EOF
```

### 手順3: プロジェクトを作成

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "MEX App", "technologies": ["React", "FastAPI", "TypeScript"]}'
```

レスポンスの `id` を控える（MCPからの記録に使う）。

### 手順4: MCPサーバーの疎通確認

Claude Codeを再起動（MCP設定を再読み込み）し、以下を試す:

```
MCPツール list_projects を呼んで、手順3で作成したプロジェクトが返ってくることを確認
```

```
MCPツール record_dev_activity を呼んで、開発ログが記録されることを確認
例: project_id="<手順3のID>", entry_type="learning", summary="テスト記録", technologies=["React"]
```

---

## 既知の制限事項

| 項目 | 内容 | 将来の対応 |
|------|------|-----------|
| JWTの有効期限 | 60分で失効する | MCP用の長期トークン（APIキー）発行エンドポイントを追加する |
| バックエンド必須 | MCPサーバーはバックエンドが起動していないとエラーになる | エラーメッセージを改善し、リトライロジックを追加する |
| プロジェクトID手動指定 | `record_dev_activity` でproject_idを毎回指定する必要がある | CLAUDE.mdにデフォルトproject_idを記載するか、`set_default_project` ツールを追加する |
