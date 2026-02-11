# MEX App ユーザーガイド

MEX App のセットアップから日常利用までの包括的なガイドです。

## 目次

1. [MEX App とは](#1-mex-app-とは)
2. [環境構築](#2-環境構築)
3. [起動方法](#3-起動方法)
4. [Web UI の使い方](#4-web-ui-の使い方)
5. [MCP サーバー連携](#5-mcp-サーバー連携)
6. [Claude Code コマンド](#6-claude-code-コマンド)
7. [設定ファイルリファレンス](#7-設定ファイルリファレンス)
8. [トラブルシューティング](#8-トラブルシューティング)

---

## 1. MEX App とは

AI 支援開発の**過程**を記録・可視化するポートフォリオアプリです。

- プロジェクト単位で開発ログと技術ドキュメントを蓄積
- MCP サーバー経由で Claude Code から自動記録
- Notion 連携でドキュメント自動生成
- 公開ポートフォリオとして共有可能

### システム構成

```
Claude Code ──MCP──→ MCP Server ──HTTP──→ FastAPI Backend ──→ PostgreSQL
                                              ↑
Notion MCP ←── Claude Code               React Frontend
```

| コンポーネント | 技術 | ポート |
|---|---|---|
| Frontend | React 19 + TypeScript | 3000 |
| Backend | FastAPI + SQLAlchemy | 8000 |
| Database | PostgreSQL 16 | 5432 |
| MCP Server | Node.js + MCP SDK | - (stdio) |

---

## 2. 環境構築

### 必要なもの

- Node.js >= 18
- Python >= 3.10
- Docker（PostgreSQL 用）
- OpenAI API Key（クイズ生成用、任意）

### 初回セットアップ

```bash
# 1. リポジトリをクローン
git clone https://github.com/kotani-takumi0/mex_app.git
cd mex_app

# 2. .env を用意
cp .env.example .env
# OPENAI_API_KEY を設定（クイズ機能を使う場合）

# 3. PostgreSQL を起動
docker compose up -d

# 4. バックエンドのセットアップ
cd backend
pip install -e ".[dev]"
alembic upgrade head
cd ..

# 5. フロントエンドのセットアップ
cd frontend
npm install
cd ..

# 6. MCP サーバーのセットアップ（任意）
cd mcp-server
npm install
npm run build
cd ..
```

---

## 3. 起動方法

3つのターミナルで以下を起動します。

**ターミナル 1: PostgreSQL**（初回以降はコンテナが残っていれば `docker start mex-postgres`）
```bash
docker compose up -d
```

**ターミナル 2: バックエンド**
```bash
cd backend
uvicorn app.main:app --reload
```

**ターミナル 3: フロントエンド**
```bash
cd frontend
npm start
```

起動後、`http://localhost:3000` にアクセスします。

### 起動確認

```bash
# バックエンドの疎通確認
curl http://localhost:8000/
# → {"message": "MEX App API - AI開発ポートフォリオ", "version": "0.3.0"}
```

---

## 4. Web UI の使い方

### 4.1 アカウント作成・ログイン

1. `http://localhost:3000/auth` にアクセス
2. 「登録」タブで表示名・メール・パスワードを入力
3. 登録完了後、自動的にダッシュボードに遷移

### 4.2 プロジェクト作成

1. `/projects/new` に移動
2. 以下を入力:
   - プロジェクト名（必須）
   - 説明
   - 使用技術（タグ形式）
   - GitHub URL / デモ URL
   - 公開設定（ポートフォリオに表示するか）
3. 「作成」をクリック

### 4.3 開発ログの管理

`/projects/:id` のプロジェクト詳細ページで:

- **手動追加**: 「ログを追加」ボタンからタイトル・カテゴリ・内容を入力
- **MCP 自動記録**: Claude Code 経由で記録されたログが自動的に表示される
- **Notion ドキュメント**: `source_url` が設定されたログはリンクとして表示される

### 4.4 MCP トークンの発行

Claude Code 連携に必要なトークンを発行します。

1. `/settings` に移動
2. 「MCP トークン」セクションで「トークン発行」をクリック
3. 表示されたトークンをコピー（**この画面でしか表示されません**）
4. `~/.mex/config.json` に保存（[セクション 5](#5-mcp-サーバー連携) 参照）

トークンの有効期限は **30 日間** です。期限切れや漏洩が疑われる場合は、設定ページから無効化して再発行してください。

### 4.5 公開ポートフォリオ

1. `/settings` でユーザー名（username）を設定
2. プロジェクトの「公開」をオンにする
3. `/p/:username` で公開ページにアクセス可能

### 4.6 画面一覧

| 画面 | パス | 説明 |
|---|---|---|
| ランディング | `/` | サービス紹介 |
| 認証 | `/auth` | ログイン / 登録 |
| ダッシュボード | `/dashboard` | 進捗サマリ、最近のプロジェクト |
| 設定 | `/settings` | プロフィール編集、MCP トークン管理 |
| 新規プロジェクト | `/projects/new` | プロジェクト作成 |
| プロジェクト詳細 | `/projects/:id` | 開発ログ一覧、ドキュメント管理 |
| 公開ポートフォリオ | `/p/:username` | 公開プロフィール |
| 公開プロジェクト | `/p/:username/:id` | 公開プロジェクト詳細 |

---

## 5. MCP サーバー連携

MCP サーバーを設定すると、Claude Code から開発ログやドキュメントを自動記録できます。

### 5.1 セットアップ

#### 方法 A: セットアップ CLI（推奨）

```bash
npx mex-setup
```

対話形式で以下を自動実行します:
- MEX App にログイン
- MCP トークンを取得
- `~/.mex/config.json` を作成

#### 方法 B: 手動設定

1. [4.4](#44-mcp-トークンの発行) でトークンを発行
2. 設定ファイルを作成:

```bash
mkdir -p ~/.mex
```

`~/.mex/config.json`:
```json
{
  "api_url": "http://localhost:8000/api",
  "api_key": "<コピーしたトークン>",
  "ai_tool": "claude_code"
}
```

### 5.2 Claude Code に登録

`~/.claude/mcp_servers.json` に追加:

```json
{
  "mex": {
    "command": "npx",
    "args": ["mex-mcp-server"]
  }
}
```

Claude Code を再起動すると MCP サーバーが自動起動します。

### 5.3 MCP ツール一覧

| ツール名 | 説明 |
|---|---|
| `save_document` | Notion 等で生成したドキュメント URL を MEX App に記録 |
| `list_projects` | プロジェクト一覧を取得 |
| `get_project_context` | プロジェクト情報 + 最近の開発ログを取得 |

### 5.4 `.mex.json`（プロジェクト紐付け）

プロジェクトルートに `.mex.json` を配置すると、`project_id` の指定を省略できます。

```json
{ "project_id": "your-project-uuid" }
```

MCP サーバーはカレントディレクトリから親方向に `.mex.json` を探索します。
`/document` コマンド（[セクション 6.1](#61-document-コマンド)）は、プロジェクト解決時にこのファイルを自動作成します。

---

## 6. Claude Code コマンド

### 6.1 `/document` コマンド

実装内容を Notion にドキュメント化し、MEX App に記録するコマンドです。

#### 使い方

```
/document                          # 直近の git diff から自動推定
/document React Routerの導入        # 主題を明示的に指定
/document バグ修正: APIレスポンス   # デバッグ系ドキュメント
```

#### 実行フロー

```
1. コンテキスト収集
   git diff / git log から実装内容を分析

2. プロジェクト解決
   .mex.json → 既存プロジェクト検索 → 新規作成（自動）

3. Notion 親ページ解決
   既存の技術ドキュメントページを検索、なければ作成

4. Notion ドキュメント作成
   概要・技術的ポイント・使用技術・コード例を含むページを生成

5. MEX App 記録
   save_document でドキュメント URL を記録

6. 結果報告
```

#### 出力例

```
## ドキュメントを生成しました

**タイトル**: 認証フロー設計
**カテゴリ**: design
**Notion**: https://www.notion.so/xxxxx
**MEX App**: 記録完了（source_urlとして保存済み）
```

#### プロジェクト自動解決

`/document` 実行時に `.mex.json` がない場合、以下の順で自動解決します:

1. `list_projects` で既存プロジェクトをリポジトリ名と照合
2. 一致するものがなければ、バックエンド API でプロジェクトを新規作成
3. `.mex.json` を書き出して次回以降は即解決

#### 前提条件

- バックエンドが起動していること
- `~/.mex/config.json` が設定済みであること
- Notion MCP が Claude Code に設定済みであること

#### カテゴリの自動判定

| カテゴリ | 対象となる内容 |
|---|---|
| `tutorial` | 手順・チュートリアル |
| `design` | 設計・アーキテクチャ |
| `debug_guide` | バグ修正・デバッグ |
| `learning` | 学習・調査 |
| `reference` | リファレンス・API 仕様 |

---

## 7. 設定ファイルリファレンス

### `~/.mex/config.json`

MCP サーバーがバックエンド API に接続するための設定。

```json
{
  "api_url": "http://localhost:8000/api",
  "api_key": "<MCPトークン>",
  "ai_tool": "claude_code"
}
```

| キー | 必須 | 説明 |
|---|---|---|
| `api_url` | Yes | バックエンド API の URL |
| `api_key` | Yes | MCP トークン（30 日間有効） |
| `ai_tool` | No | AI ツール名（デフォルト: `claude_code`） |

### `.mex.json`（プロジェクトルート）

プロジェクトと MEX App を紐付ける設定。

```json
{ "project_id": "uuid-of-your-project" }
```

### `~/.claude/mcp_servers.json`

Claude Code の MCP サーバー設定。

```json
{
  "mex": {
    "command": "npx",
    "args": ["mex-mcp-server"]
  }
}
```

### `backend/.env`

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mex_app
JWT_SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
OPENAI_API_KEY=sk-proj-...    # クイズ機能を使う場合
```

---

## 8. トラブルシューティング

### バックエンドに接続できない

```bash
# バックエンドの起動確認
curl http://localhost:8000/

# PostgreSQL の起動確認
docker ps | grep mex-postgres
# 停止していれば: docker start mex-postgres
```

### MCP サーバーが起動しない

```bash
# 設定ファイルの存在確認
cat ~/.mex/config.json

# api_url と api_key が設定されているか確認
# api_key が期限切れの場合は /settings から再発行
```

### `/document` で「project_id が見つからない」

以下のいずれかで対応:
1. プロジェクトルートに `.mex.json` を配置する
2. `/document` コマンドが自動でプロジェクトを作成するので、バックエンドが起動していることを確認

### MCP トークンが期限切れ

1. `http://localhost:3000/settings` にアクセス
2. 古いトークンを無効化
3. 新しいトークンを発行
4. `~/.mex/config.json` の `api_key` を更新

### Notion MCP が動かない

Claude Code で `/mcp` を実行し、Notion MCP サーバーが registered になっていることを確認してください。
