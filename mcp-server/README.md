# MEX MCP Server

MEX App の開発ログを AI コーディングツールから自動記録するための [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) サーバーです。

## セットアップ

### 1. ビルド

```bash
cd mcp-server
npm install && npm run build
```

### 2. MEX App でアカウントを作成し、API トークンを発行

1. MEX App にログイン
2. 設定ページ（`/settings`）→「API トークン」セクションでトークンを発行
3. 表示されたトークンをコピー（**この画面でしか表示されません**）

### 3. セットアップ CLI を実行

対話形式でログイン → トークン取得 → 設定ファイル作成をすべて自動で行います。

```bash
node dist/cli/setup.js
```

プロンプトに従ってメールアドレス・パスワードを入力すると、`~/.mex/config.json` が自動生成されます。

> 手動で設定する場合は [MCP_SERVER.md](../MCP_SERVER.md) を参照してください。

### 4. Claude Code の MCP 設定に登録

`~/.claude/mcp_servers.json` に以下を追加します：

```json
{
  "mex": {
    "command": "node",
    "args": ["/absolute/path/to/mcp-server/dist/index.js"]
  }
}
```

> `args` のパスは実際の `dist/index.js` の絶対パスに置き換えてください。

## 提供ツール

| ツール名 | 機能 |
|----------|------|
| `record_dev_activity` | 開発活動の記録 |
| `list_projects` | プロジェクト一覧取得 |
| `get_project_context` | プロジェクト概要 + 最近の開発ログ取得 |

## セキュリティ

- `~/.mex/config.json` には API トークンが含まれます。**Git にコミットしたり、他者と共有しないでください。**
- トークンは MEX App の設定ページからいつでも失効できます。

## License

MIT
