# MEX MCP Server

MEX App の開発ログを AI ツールから自動記録するための MCP サーバーです。

## セットアップ

1. 依存関係をインストール

```bash
cd mcp-server
npm install
```

2. ビルド

```bash
npm run build
```

3. 設定ファイルを作成

`~/.mex/config.json` を作成してください。

```json
{
  "api_url": "http://localhost:8000/api",
  "api_key": "<your_api_key>",
  "ai_tool": "claude_code"
}
```

## Claude Code 連携例

`.claude/mcp_servers.json` に以下を追加します。

```json
{
  "mex": {
    "command": "node",
    "args": ["/path/to/mex_app/mcp-server/dist/index.js"],
    "env": {}
  }
}
```

## 提供ツール

- `record_dev_activity`: 開発ログを記録
- `list_projects`: プロジェクト一覧取得
- `get_project_context`: プロジェクト概要 + 最近の開発ログ取得
