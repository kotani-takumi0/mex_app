# MEX MCP Server

MEX App の開発ログを AI コーディングツールから自動記録するための [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) サーバーです。

npm パッケージとして公開されており、`npx` で直接実行できます。

## セットアップ

### 1. セットアップ CLI を実行

対話形式でログイン → トークン取得 → `~/.mex/config.json` 作成をすべて自動で行います。
事前にバックエンドを起動しておいてください。

```bash
npx -p mex-mcp-server mex-setup
```

プロンプトに従って入力してください：

| 質問 | 入力内容 |
|---|---|
| API URL | そのまま Enter（ローカル開発なら `http://localhost:8000/api` でOK） |
| メールアドレス | MEX App に登録済みのメールアドレス |
| パスワード | MEX App に登録済みのパスワード |
| AI Tool名 | そのまま Enter（デフォルト `claude_code`） |

> 手動で設定する場合は [MCP_SERVER.md](../MCP_SERVER.md) を参照してください。

### 2. Claude Code の MCP 設定に登録

`.claude/mcp_servers.json`（プロジェクト単位）または `~/.claude/settings.json`（全プロジェクト共通）に以下を追加します：

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
| `save_document` | 技術ドキュメントの記録 |
| `list_projects` | プロジェクト一覧取得 |
| `get_project_context` | プロジェクト概要 + 最近の開発ログ取得 |

## セキュリティ

- `~/.mex/config.json` には API トークンが含まれます。**Git にコミットしたり、他者と共有しないでください。**
- トークンは MEX App の設定ページからいつでも失効できます。

## License

MIT
