---
title: "MEX App × Claude Code: MCPサーバーのセットアップガイド"
emoji: "🔌"
type: "tech"
topics: ["mcp", "claudecode", "ai", "portfolio", "開発ログ"]
published: true
---

## はじめに

**MEX App** は、Claude Code での開発作業を自動で記録し、ポートフォリオとして公開できるアプリです。

この記事では、MEX App の **MCP サーバー** を Claude Code に接続する手順を、初めての方にもわかるように解説します。

### MCP サーバーとは？

MCP（Model Context Protocol）は、AI ツールと外部サービスを接続するための仕組みです。MEX App の MCP サーバーを Claude Code に接続すると、以下が自動化されます：

- **開発ログの自動記録** — コーディング中の作業が MEX App に記録される
- **ドキュメント保存** — 学習メモやチュートリアルを MEX App に保存
- **ノートブック連携** — NotebookLM で作成した学習コンテンツの管理

## 前提条件

- **MEX App のアカウント** — まだの方は [MEX App](https://your-mex-app.example.com) で登録
- **Node.js 18 以上** — `node -v` で確認
- **Claude Code** — `npm install -g @anthropic-ai/claude-code` でインストール

## セットアップ手順

### Step 1: MEX App でトークンを発行する

まず MEX App にログインし、セットアップウィザード（またはダッシュボード → 設定）から **MCP トークン** を発行します。

:::message
トークンは発行時に一度だけ表示されます。コピーして安全な場所に保存してください。
:::

### Step 2: ターミナルでセットアップコマンドを実行

プロジェクトのディレクトリで以下を実行します。

```bash
npx -p mex-mcp-server mex-setup
```

実行すると、対話形式で 4 つの質問が表示されます。以下を参考に入力してください。

---

#### 質問 1: API URL

```
API URL [http://localhost:8000/api]:
```

**何を入れるか：** MEX App のバックエンド API の URL です。

| 環境 | 入力する値 |
|------|-----------|
| 本番（Render デプロイ） | `https://mex-app-backend.onrender.com/api` |
| ローカル開発 | そのまま Enter（デフォルト値が使われます） |

:::message alert
ローカル開発環境の方以外は、**必ず本番 URL を入力してください**。デフォルトの `localhost` のままだと接続できません。
:::

---

#### 質問 2: メールアドレス

```
メールアドレス:
```

**何を入れるか：** MEX App に登録したメールアドレスです。

```
メールアドレス: your-email@example.com
```

---

#### 質問 3: パスワード

```
パスワード:
```

**何を入れるか：** MEX App に登録したパスワードです。

:::message
パスワードは入力中に画面に表示される場合があります（端末の仕様によります）。周囲に注意してください。
:::

---

#### 質問 4: AI Tool 名

```
AI Tool名 [claude_code]:
```

**何を入れるか：** 使用している AI ツールの名前です。Claude Code を使っている場合は **そのまま Enter** で OK です。

---

### セットアップ成功時の出力

すべて正しく入力すると、以下のように表示されます。

```
ログイン中...
✓ ログイン成功
✓ APIトークン取得成功（30日間有効）
✓ 設定ファイル作成: /home/username/.mex/config.json

=== セットアップ完了 ===
```

これで `~/.mex/config.json` に接続設定が保存されました。

### Step 3: Claude Code に MCP サーバーを登録

最後に、Claude Code に MEX MCP サーバーを登録します。

```bash
claude mcp add mex -- npx mex-mcp-server
```

これで完了です！

## 動作確認

Claude Code を起動して、プロジェクトで作業してみましょう。開発ログが MEX App のダッシュボードに自動的に記録されるようになります。

Claude Code 内で `/mcp` と打つと、接続されている MCP サーバーの一覧を確認できます。`mex` が表示されていれば正常に接続されています。

## トラブルシューティング

### 「ログイン失敗」と表示される

- メールアドレス・パスワードが正しいか確認
- API URL が正しいか確認（本番環境なのに `localhost` になっていないか）

### 「APIトークン取得失敗」と表示される

- MEX App のアカウントが有効か確認
- ネットワーク接続を確認

### Claude Code で MCP サーバーが認識されない

以下を試してください：

1. Claude Code を再起動
2. `claude mcp list` で `mex` が登録されているか確認
3. 登録されていなければ再度 `claude mcp add mex -- npx mex-mcp-server` を実行

### 30 日後にトークンが期限切れになった

トークンの有効期限は 30 日です。期限が切れたら、再度セットアップコマンドを実行してください：

```bash
npx -p mex-mcp-server mex-setup
```

または MEX App の設定画面から新しいトークンを発行し、`~/.mex/config.json` の `api_key` を書き換えることもできます。

## 設定ファイルの構造（参考）

セットアップが完了すると、`~/.mex/config.json` が以下の形式で作成されます：

```json
{
  "api_url": "https://mex-app-backend.onrender.com/api",
  "api_key": "your-api-token-here",
  "ai_tool": "claude_code"
}
```

手動で編集することも可能ですが、通常はセットアップコマンドの再実行をおすすめします。

## まとめ

| ステップ | コマンド |
|---------|---------|
| セットアップ | `npx -p mex-mcp-server mex-setup` |
| Claude Code に登録 | `claude mcp add mex -- npx mex-mcp-server` |
| 動作確認 | Claude Code で `/mcp` |

セットアップは 2 分程度で完了します。開発ログの自動記録で、ポートフォリオを効率的に構築しましょう。
