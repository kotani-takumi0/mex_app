# MEX MCP Server

MEX App の開発ログを AI コーディングツールから自動記録するための [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) サーバーです。

## インストール

```bash
npm install -g mex-mcp-server
```

または `npx` で直接実行できます（インストール不要）。

## セットアップ

### 1. MEX App でアカウントを作成し、API トークンを発行

1. MEX App にログイン
2. 設定ページ（`/settings`）→「API トークン」セクションでトークンを発行
3. 表示されたトークンをコピー（**この画面でしか表示されません**）

### 2. セットアップ CLI を実行

対話形式でログイン → トークン取得 → 設定ファイル作成をすべて自動で行います。

```bash
npx mex-setup
```

プロンプトに従ってメールアドレス・パスワードを入力すると、`~/.mex/config.json` が自動生成されます。

### 3. Claude Code の MCP 設定に登録

`~/.claude/mcp_servers.json` に以下を追加します：

```json
{
  "mex": {
    "command": "npx",
    "args": ["mex-mcp-server"]
  }
}
```

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
