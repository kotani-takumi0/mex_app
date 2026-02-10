# MCP トークン ガイド

MEX App における MCP トークンの仕組みと使い方をまとめたドキュメントです。

## ユーザー向けセットアップ手順

一般ユーザーが MCP トークンを発行し、Claude Code から MEX に接続するまでの手順です。

### 前提条件

- MEX App のアカウントを持っていること
- Node.js がインストールされていること

### Step 1: MEX App にログインしてトークンを発行

1. ブラウザで MEX App を開く
2. ログインする
3. 設定ページ（`/settings`）に移動
4. 「APIトークン」セクションでトークンを発行
5. 表示されたトークンをコピー（**この画面でしか表示されません**）

### Step 2: セットアップ CLI を実行

対話形式でログイン → トークン取得 → `~/.mex/config.json` 作成をすべて自動で行います。

```bash
npx mex-setup
```

> 手動で設定する場合は `~/.mex/config.json` を以下の内容で作成してください：
>
> ```json
> {
>   "api_url": "http://localhost:8000/api",
>   "api_key": "<コピーしたトークン>",
>   "ai_tool": "claude_code"
> }
> ```

### Step 3: Claude Code の MCP 設定に登録

`~/.claude/mcp_servers.json` に以下を追加します：

```json
{
  "mex": {
    "command": "npx",
    "args": ["mex-mcp-server"]
  }
}
```

### Step 4: 動作確認

Claude Code 上で以下のツールが使えれば成功です：

- `mcp__mex__list_projects` — プロジェクト一覧取得
- `mcp__mex__record_dev_activity` — 開発活動の記録
- `mcp__mex__get_project_context` — プロジェクト詳細 + 開発ログ取得

---

## 開発者向けセットアップ手順

ソースコードからMCPサーバーをビルドして使う場合の手順です。

### 方法 A: セットアップCLI（推奨）

対話形式でログイン → トークン取得 → `~/.mex/config.json` 作成をすべて自動で行います。

```bash
npx mex-setup
```

以下の対話プロンプトが表示されます：

```
=== MEX MCP Server セットアップ ===

API URL [http://localhost:8000/api]:    ← Enter でデフォルト
メールアドレス: your@email.com          ← MEX アカウントのメール
パスワード: ********                    ← MEX アカウントのパスワード
AI Tool名 [claude_code]:               ← Enter でデフォルト

✓ ログイン成功
✓ APIトークン取得成功（30日間有効）
✓ 設定ファイル作成: /home/<user>/.mex/config.json
```

### 方法 B: 手動セットアップ

上記「ユーザー向けセットアップ手順」の Step 1〜2 を実行してください。

本リポジトリではプロジェクト直下の `.mcp.json` に MCP サーバーが登録済みです：

```json
{
  "mcpServers": {
    "mex": {
      "command": "npx",
      "args": ["mex-mcp-server"]
    }
  }
}
```

このリポジトリ内で Claude Code を起動すれば、自動的に MCP サーバーが読み込まれます。

---

## トークンの種類

| 種類 | 有効期限 | 用途 |
|------|----------|------|
| セッション JWT | 60分 | フロントエンドの Web 認証 |
| MCP トークン | 30日 | MCP サーバー → バックエンド API の認証 |

MCP トークンは、Claude Code 等の外部ツールから MEX API を安全に利用するための長寿命トークンです。

## トークンのライフサイクル

### 1. トークン発行

フロントエンドの `/settings` ページから発行します。

- API: `POST /auth/api-token`
- トークンは **発行時に1回だけ表示** されます（再表示不可）
- データベースには **SHA-256 ハッシュ** のみ保存されるため、原文は復元できません

### 2. ローカル設定

発行したトークンを `~/.mex/config.json` に保存します：

```json
{
  "api_url": "http://localhost:8000/api",
  "api_key": "<発行されたMCPトークン>",
  "ai_tool": "claude_code"
}
```

MCP サーバー起動時にこのファイルが読み込まれます（`mcp-server/src/config.ts`）。

### 3. API 認証

`MexApiClient`（`mcp-server/src/api-client.ts`）が、全リクエストに Bearer トークンを付与します：

```
Authorization: Bearer <api_key>
```

これにより以下の MCP ツールが認証付きで動作します：

| ツール名 | 機能 |
|----------|------|
| `record_dev_activity` | 開発活動の記録 |
| `list_projects` | プロジェクト一覧取得 |
| `get_project_context` | プロジェクト詳細 + 開発ログ取得 |

### 4. トークン検証

バックエンド（`backend/app/auth/dependencies.py`）でリクエストごとに以下を検証します：

1. JWT 署名・有効期限の検証
2. `mcp_tokens` テーブルで失効チェック（`revoked_at` が設定されていないか確認）

### 5. トークン失効

フロントエンドの `/settings` ページからいつでも失効できます。

- API: `POST /auth/mcp-token/revoke`
- `revoked_at` にタイムスタンプが設定され、即座に無効化されます
- トークンの所有者のみが失効操作を実行できます

## セキュリティ設計

- **ハッシュ保存**: トークン原文はDBに保存せず、SHA-256 ハッシュのみ保存。DB漏洩時のリスクを軽減
- **即時失効**: 失効操作は即座に反映され、以降のリクエストはすべて拒否
- **スコープ制限**: デフォルトスコープは `devlog:write`
- **フェイルオープン**: 失効チェック時の DB エラーはグレースフルに処理（通常の JWT はテーブルに存在しないため）

## 関連ファイル

| レイヤー | ファイル | 役割 |
|----------|---------|------|
| Backend | `backend/app/api/auth.py` | トークン発行・失効エンドポイント |
| Backend | `backend/app/auth/dependencies.py` | トークン検証・失効チェック |
| Backend | `backend/app/auth/jwt.py` | JWT 生成・検証ユーティリティ |
| Backend | `backend/app/infrastructure/database/models.py` | `mcp_tokens` テーブル定義 |
| Backend | `alembic/versions/004_pgvector_and_mcp_tokens.py` | DB マイグレーション |
| MCP Server | `mcp-server/src/config.ts` | `~/.mex/config.json` 読み込み |
| MCP Server | `mcp-server/src/api-client.ts` | Bearer 認証付き API クライアント |
| MCP Server | `mcp-server/src/index.ts` | MCP サーバーエントリポイント |
| MCP Server | `mcp-server/src/tools/` | 各ツールの実装 |
| Frontend | `frontend/src/components/Settings/SettingsPage.tsx` | トークン管理 UI |
| Frontend | `frontend/src/api/auth.ts` | トークン関連 API 呼び出し |
| Frontend | `frontend/src/types/index.ts` | 型定義（`ApiTokenResponse`, `MCPTokenInfo`） |
