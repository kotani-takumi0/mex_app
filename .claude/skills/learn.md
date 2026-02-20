---
description: MEX Appに記録されたNotionドキュメントをNotebookLMに取り込み、学習ハブを構築する
allowed-tools: Bash(git diff:*, git log:*, git show:*, curl:*, cat ~/.mex/config.json:*), Read, Write, Glob, Grep, mcp__notebooklm-mcp__notebook_create, mcp__notebooklm-mcp__source_add, mcp__notebooklm-mcp__notebook_list, mcp__notebooklm-mcp__notebook_get, mcp__notion__notion-fetch, mcp__notion__notion-search, mcp__mex__save_notebook, mcp__mex__get_project_context, mcp__mex__list_projects
---

# NotebookLMソース取り込み

<background_information>
- **Mission**: MEX Appに記録された技術ドキュメント（Notionページ）をNotebookLMノートブックにソースとして取り込む
- **フロー**: プロジェクト解決 → ソースコンテンツ収集 → NotebookLM操作 → MEX App記録 → 結果報告
- **使用インフラ**: NotebookLM MCP（ノートブック作成・ソース追加）、Notion MCP（ページコンテンツ取得）、MEX MCP `save_notebook`（記録）
- **前提**: `/document` または `/understand` でNotionドキュメントが生成済みであること
- **重要**: NotionはSPA（Single Page Application）のため、URLを直接NotebookLMのソースとして追加すると「JavaScript を有効にしてください」エラーページのみが取り込まれる。必ず Notion MCP API (`notion-fetch`) でコンテンツをテキスト取得し、`source_type=text` で追加すること。
- **学習コンテンツ生成（フラッシュカード・音声等）は NotebookLM の UI 上で手動実行すること**
</background_information>

<instructions>

## Step 1: プロジェクト解決

MEX App の `project_id` を解決する:

1. **`.mex.json` を確認**: プロジェクトルート（gitルート）に `.mex.json` が存在すれば、その `project_id` を使用 → **解決完了**
2. **既存プロジェクトを検索**: `mcp__mex__list_projects` でプロジェクト一覧を取得し、ディレクトリ名やリポジトリ名で照合
3. **見つからない場合**: ユーザーに先に `/document` または `/understand` を実行してプロジェクトを作成するよう案内

## Step 2: ソースコンテンツ収集

`mcp__mex__get_project_context` でプロジェクトの DevLogEntry を取得し、ソースURLを収集する:

1. `devlog_entries` から `metadata.source_url` が存在するエントリを抽出
2. URLがNotionドメイン（`notion.so` または `notion.site`）のものを優先
3. 最低1件のソースURLが必要。なければエラー:「先に `/document` または `/understand` でNotionドキュメントを生成してください」

収集したソースのリストをユーザーに表示し、確認を取る:
```
以下のドキュメントをNotebookLMに取り込みます:
1. {title} - {source_url}
2. {title} - {source_url}
...
```

**次に、各ソースのコンテンツを Notion MCP で取得する:**

各 Notion URL に対して `mcp__notion__notion-fetch` を呼び出し、ページのテキストコンテンツを取得する。
- `id`: Notion URL または UUID
- レスポンスの `text` フィールドからページコンテンツ（Markdown形式）を取得
- 取得失敗した場合はスキップし、成功/失敗を記録

## Step 3: NotebookLM ノートブック作成

`mcp__notebooklm-mcp__notebook_create` でノートブックを作成する:

- **タイトル**: `{プロジェクト名} - 学習ノート` 形式
- レスポンスから `notebook_id` を取得

## Step 4: ソース追加（テキストとして追加）

**重要: `source_type=text` を使用すること。`source_type=url` でNotion URLを追加してはならない。**

Step 2 で取得した各ページコンテンツを `mcp__notebooklm-mcp__source_add` で追加:

- `notebook_id`: Step 3 で取得したID
- `source_type`: **`text`**（必須。`url` は使用禁止）
- `title`: Notionページのタイトル（例: `[Understand] 認証システム`）
- `text`: Step 2 で `notion-fetch` から取得したページコンテンツ
- `wait`: `true`（処理完了を待つ）
- エラーが出たソースはスキップし、成功/失敗を記録

## Step 5: MEX App記録

`mcp__mex__save_notebook` を呼び出して MEX App に記録する:

パラメータ:
- **project_id**: Step 1 で解決したID
- **title**: ノートブックのタイトル
- **notebook_id**: Step 3 で取得したID
- **notebook_url**: NotebookLMのノートブックURL（`https://notebooklm.google.com/notebook/{notebook_id}`）
- **technologies**: プロジェクトの技術スタック
- **learning_type**: `summary`

## Step 6: 結果報告

以下の形式でユーザーに報告:

```
## NotebookLMにソースを取り込みました

**ノートブック**: {タイトル}
**ソース数**: {追加したソース数}件
**NotebookLM**: {ノートブックURL}
**MEX App**: 記録完了

**取り込んだドキュメント**:
- {title1}
- {title2}
- ...

学習コンテンツ（フラッシュカード・音声ポッドキャスト等）は NotebookLM の UI から生成できます。
```

## エラーハンドリング

- **`save_notebook` が見つからない場合**: MEX MCPサーバーの再ビルドと再起動が必要。「`cd mcp-server && npm run build` を実行後、MCPサーバーを再起動してください」と案内
- **NotebookLM MCPが見つからない場合**: 「`uv tool install notebooklm-mcp-cli && nlm setup add claude-code && nlm login` を実行してください」と案内
- **NotebookLM認証エラー**: 「`nlm login` で再認証してください」と案内
- **Notion MCP でページ取得失敗**: ページが削除済みまたはアクセス権がない可能性。スキップして続行し、失敗したURLを報告
- **ソースのテキストが空**: Notion MCP がコンテンツを返さない場合。ページが空でないか確認を案内
- **プロジェクト未設定**: 「先に `/document` または `/understand` でドキュメントを生成するか、`.mex.json` にproject_idを設定してください」と案内

</instructions>

## 推奨ワークフロー

> **`/document` または `/understand` → `/learn` の順で実行してください**
>
> `/learn` は `/document` や `/understand` で生成されたNotionドキュメントのコンテンツをNotebookLMのソースとして取り込みます。
> ドキュメントが存在しない場合、ソースを追加できません。
> 学習コンテンツの生成は NotebookLM の UI 上で手動で行ってください。
>
> ```
> # 推奨フロー A: 新規実装の学習
> 1. 機能を実装する
> 2. git commit する
> 3. /document を実行する（Notionドキュメント生成）
> 4. /learn を実行する（NotebookLMにソース取り込み）
> 5. NotebookLM UI で学習コンテンツを生成する
>
> # 推奨フロー B: 既存コードベースの学習
> 1. /understand を実行する（コードベース分析 → Notionドキュメント生成）
> 2. /learn を実行する（NotebookLMにソース取り込み）
> 3. NotebookLM UI で学習コンテンツを生成する
> ```

## 使用例

```
/learn    # NotebookLMにソースを取り込む
```
