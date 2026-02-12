# MEX MCP Server 利用ガイド

MEX App の開発ログを AI ツールから自動記録するための MCP サーバーの使い方をまとめたドキュメントです。

## 概要

MCP サーバーは MEX App の API と通信し、以下の操作を AI ツール経由で行えるようにします。
- 開発ログの記録
- プロジェクト一覧の取得
- プロジェクト概要 + 最近の開発ログの取得

## 前提条件

- MEX App の API が起動していること
- API へのアクセスに必要な `api_key` が用意されていること
- Node.js 環境で `npm` が使えること

## セットアップ

### 1. MCP サーバーをビルド

```bash
cd mcp-server
npm install && npm run build
```

### 2. セットアップ CLI を実行

対話形式でログイン → トークン取得 → `~/.mex/config.json` 作成をすべて自動で行います。

```bash
node dist/cli/setup.js
```

> 手動で設定する場合は `~/.mex/config.json` を以下の内容で作成してください：
>
> ```json
> {
>   "api_url": "http://localhost:8000/api",
>   "api_key": "<your_api_key>",
>   "ai_tool": "claude_code"
> }
> ```
>
> - `api_url` と `api_key` は必須です。
> - `ai_tool` は省略可能で、未指定時は `claude_code` が使われます。

### 3. MCP サーバーを登録

Claude Code の MCP 設定に登録すれば、自動で起動されます（下記「Claude Code 連携例」参照）。

## 使い方の流れ（ざっくり）

1. **MCP クライアントにサーバーを登録**（例: Claude Code）
2. **MCP サーバーを起動**
3. **AI に「どのツールを使うか」を指示**して、必要な情報を取得/記録する

MCP は「AI が使えるツールを提供する仕組み」です。  
このサーバーを登録すると、AI が `list_projects` や `record_dev_activity` を呼べるようになります。

## Claude Code 連携例

`~/.claude/mcp_servers.json` に以下を追加します。

```json
{
  "mex": {
    "command": "node",
    "args": ["/absolute/path/to/mex_app/mcp-server/dist/index.js"]
  }
}
```

> `args` のパスは実際の `mcp-server/dist/index.js` の絶対パスに置き換えてください。

## 実際の利用例（プロンプト例）

以下は **AI に依頼する文章例** です。  
MCP クライアント（Claude Code など）が裏側でツール呼び出しを行います。

### 例1: プロジェクト一覧を取得

```
MEX のプロジェクト一覧を取得して。
```

### 例2: プロジェクトIDを指定して概要を取得

```
project_id が "abc123" のプロジェクト概要と最近の開発ログを取得して。
```

### 例3: 開発ログを記録

```
project_id が "abc123" のプロジェクトに
「バグ修正でAPIの例外処理を追加した」という内容を記録して。
```

## ツール呼び出しイメージ（参考）

※ 実際の呼び出しは MCP クライアントが行います。ここでは**形のイメージ**を示します。

### `list_projects`

```json
{
  "tool": "list_projects",
  "input": {}
}
```

### `get_project_context`

```json
{
  "tool": "get_project_context",
  "input": {
    "project_id": "abc123"
  }
}
```

### `record_dev_activity`

```json
{
  "tool": "record_dev_activity",
  "input": {
    "project_id": "abc123",
    "entry_type": "debug",
    "summary": "APIの例外処理を追加してログ出力を改善した",
    "detail": "getDevLogs の失敗時に例外を throw するよう修正",
    "technologies": ["TypeScript", "MEX API"]
  }
}
```

## 提供ツール

### `record_dev_activity`

開発過程を MEX App に記録します。

入力:
- `project_id` (string, 必須)
- `entry_type` (string, 必須)
- `summary` (string, 必須)
- `technologies` (string[], 必須)
- `detail` (string, 任意)

`entry_type` の選択肢:
- `code_generation`
- `debug`
- `design_decision`
- `learning`
- `error_resolution`

### `list_projects`

MEX App に登録されているプロジェクトの一覧を取得します。

入力: なし

### `get_project_context`

プロジェクトの概要と最近の開発ログを取得します。

入力:
- `project_id` (string, 必須)

## 参考実装

サーバー実装は `mcp-server/src` にあります。

- `mcp-server/src/index.ts` サーバー起動とツール登録
- `mcp-server/src/tools/*` ツール定義
- `mcp-server/src/api-client.ts` MEX API クライアント
