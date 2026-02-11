---
description: タスク実装後の技術ドキュメントをNotionに生成し、MEX Appに記録する
allowed-tools: Bash(git diff:*, git log:*, git show:*, curl:*, cat ~/.mex/config.json:*), Read, Write, Glob, Grep, mcp__notion__notion-search, mcp__notion__notion-create-pages, mcp__notion__notion-fetch, mcp__mex__save_document, mcp__mex__get_project_context, mcp__mex__list_projects
argument-hint: [ドキュメントの主題（省略可）]
---

# Notion連携ドキュメント生成

<background_information>
- **Mission**: 実装した内容を理解するための技術ドキュメントをNotionに自動生成し、MEX Appに記録する
- **フロー**: コンテキスト収集 → プロジェクト解決 → Notion親ページ解決 → ドキュメント作成 → MEX App記録 → 結果報告
- **使用インフラ**: Notion MCP（ページ作成）、MEX MCP `save_document`（ドキュメント記録）、Git（変更内容取得）
- **重要な設計意図**: MEX App の「学んだこと」欄はユーザーが後から自分の言葉で書く場所。AIはここに内容を入れない。URLは必ず `source_url` フィールドに分離する。
</background_information>

<instructions>

## Step 1: コンテキスト収集

以下の情報を並行して収集する:

1. **ドキュメントの主題を決定**:
   - `$1` が指定されていればそれを主題として使用
   - 指定なしの場合は `git diff --stat HEAD~1` と `git log --oneline -3` から実装内容を推定

2. **プロジェクト情報を取得**:
   - `mcp__mex__get_project_context` を呼び出してプロジェクト名・技術スタック・最近のログを取得
   - プロジェクト名を変数として保持（Notion親ページの検索に使用）

3. **実装の詳細を把握**:
   - `git diff HEAD~1` や直近の会話の流れから、実装の技術的ポイントを整理
   - 使用した技術・ライブラリを特定

## Step 1.5: プロジェクト解決

MEX App の `project_id` を解決する。以降のステップで `save_document` に渡す。

1. **`.mex.json` を確認**: プロジェクトルート（gitルート）に `.mex.json` が存在すれば、その `project_id` を使用 → **解決完了、Step 2 へ**

2. **既存プロジェクトを検索**: `mcp__mex__list_projects` でプロジェクト一覧を取得し、`git remote get-url origin` のリポジトリ名やディレクトリ名とタイトルを照合する
   - **一致するプロジェクトが見つかった場合**: その `id` を使用 → `.mex.json` を書き出して **解決完了**

3. **新規作成**: 一致するプロジェクトがない場合、バックエンドAPIで自動作成する:
   - `~/.mex/config.json` から `api_url` と `api_key` を読む
   - git情報からプロジェクト情報を推定:
     - `title`: リポジトリ名またはディレクトリ名
     - `description`: README.md の冒頭やgit情報から簡潔に（1〜2文）
     - `technologies`: 使用技術（package.json, requirements.txt 等から推定、5個程度）
     - `repository_url`: `git remote get-url origin`
   - APIを呼び出す:
     ```bash
     curl -s -X POST {api_url}/projects \
       -H "Authorization: Bearer {api_key}" \
       -H "Content-Type: application/json" \
       -d '{"title": "...", "description": "...", "technologies": [...], "repository_url": "...", "status": "in_progress"}'
     ```
   - レスポンスから `id` を取得

4. **`.mex.json` を書き出し**: プロジェクトルートに以下を作成（Step 2, 3 で新たに解決した場合のみ）:
   ```json
   { "project_id": "{解決したID}" }
   ```
   これにより次回以降は Step 1 で即解決される。

## Step 2: Notion親ページの解決

プロジェクトごとの親ページを解決する:

1. `mcp__notion__notion-search` でプロジェクト名に関連する既存の技術ドキュメント親ページを検索
2. **見つかった場合**: その page_id を親ページとして使用
3. **見つからなかった場合**: `mcp__notion__notion-create-pages` でワークスペース直下に「{プロジェクト名} MEX Docs」という空のページを作成し、その page_id を使用

## Step 3: Notionドキュメント作成

`mcp__notion__notion-create-pages` で親ページ配下にドキュメントを作成する。

**タイトルの付け方（重要）:**
- **短く簡潔に**（1行、20文字程度）
- 例: 「React Router導入」「認証フロー設計」「API レスポンスバグ修正」
- NG: 長い説明文をタイトルにしない

**ドキュメント構造**（Notion Markdown形式）:

```
## 概要
何を実装したか、その背景と目的を簡潔に説明。

## 技術的ポイント
理解に必要な知識や設計判断を箇条書きで整理。
- ポイント1
- ポイント2

## 使用技術
- 技術/ライブラリ名とその役割

## コード例・アーキテクチャ
必要に応じてコードスニペットや構成図を含める。

## 参考リンク
関連するドキュメントやリソースがあれば記載。
```

- 作成後、レスポンスから Notion ページの URL を取得する
- URLが取得できない場合は `mcp__notion__notion-fetch` でページ情報を取得してURLを構成する

## Step 4: MEX App記録

**`mcp__mex__save_document` を呼び出す。**

パラメータの設定ルール:
- **project_id**: Step 1.5 で解決した `project_id`（必須）
- **title**: Notionページのタイトルと同じ短い要約（1行、20文字程度）
- **category**: 内容に基づき以下から自動選択
  - `tutorial`: 手順・チュートリアル的な内容
  - `design`: 設計・アーキテクチャの説明
  - `debug_guide`: バグ修正・デバッグの記録
  - `learning`: 学習・調査のまとめ
  - `reference`: リファレンス・API仕様
- **technologies**: 実装で使用した主要な技術のリスト（3〜5個程度）
- **source_url**: Step 3 で取得した **NotionページのURL**（必須。ここにURLを入れることで、Frontend上でクリッカブルリンクとして表示される）

**絶対にやらないこと:**
- `record_dev_activity` を使わない（`save_document` を使う）
- URLを title や detail に混ぜない（必ず `source_url` に入れる）

## Step 5: 結果報告

以下の形式でユーザーに報告:

```
## ドキュメントを生成しました

**タイトル**: {タイトル}
**カテゴリ**: {category}
**Notion**: {NotionページURL}
**MEX App**: 記録完了（source_urlとして保存済み）
```

プロジェクトを新規作成した場合は以下も追記:
```
**Note**: プロジェクト「{title}」を新規作成し、`.mex.json` に保存しました。
```

## エラーハンドリング

- **`save_document` が見つからない場合**: MCP サーバーの再起動が必要。「MCPサーバーを再起動してください（`/mcp` → mex を restart）」と案内する。`record_dev_activity` へのフォールバックはしない。
- **プロジェクト作成APIエラー**: `~/.mex/config.json` が存在しない、またはAPIが応答しない場合は、バックエンドの起動状態と設定を確認するよう案内する。トークン期限切れの場合は `/api/auth/login` で再取得を案内する
- **Notion接続エラー**: エラー内容を表示し、Notion MCPの設定確認を案内
- **MEX App記録エラー**: Notionページは作成済みなのでURLを表示し、手動記録を案内

</instructions>

## 使用例

```
/document                          # 直近のgit diffから自動推定
/document React Routerの導入        # 主題を明示的に指定
/document バグ修正: APIレスポンス   # デバッグ系ドキュメント
```
