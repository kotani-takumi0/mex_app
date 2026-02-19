---
description: NotebookLM MCPを使って学習コンテンツ（フラッシュカード/音声ポッドキャスト等）を自動生成し、MEX Appに記録する
allowed-tools: Bash(git diff:*, git log:*, git show:*, curl:*, cat ~/.mex/config.json:*), Read, Write, Glob, Grep, mcp__notebooklm__notebook_create, mcp__notebooklm__source_add, mcp__notebooklm__studio_create, mcp__notebooklm__notebook_share_public, mcp__notebooklm__notebook_list, mcp__mex__save_notebook, mcp__mex__get_project_context, mcp__mex__list_projects
argument-hint: [学習タイプ: flashcard|audio|summary|full（省略可）]
---

# NotebookLM学習コンテンツ生成

<background_information>
- **Mission**: MEX Appに記録された技術ドキュメント（Notionページ）をNotebookLMに取り込み、フラッシュカード・音声ポッドキャスト・要約などの学習コンテンツを自動生成する
- **フロー**: 学習タイプ決定 → プロジェクト解決 → ソースURL収集 → NotebookLM操作 → MEX App記録 → 結果報告
- **使用インフラ**: NotebookLM MCP（ノートブック作成・ソース追加・スタジオ生成）、MEX MCP `save_notebook`（記録）
- **前提**: `/document` でNotionドキュメントが生成済みであること。NotebookLMにはそのNotionページURLをソースとして追加する。
</background_information>

<instructions>

## Step 1: 学習タイプ決定

`$1` 引数から学習コンテンツの種類を決定する:

| 引数 | 学習タイプ | 生成内容 |
|------|-----------|---------|
| `flashcard` | フラッシュカード | 暗記用カード |
| `audio` | 音声ポッドキャスト | 会話形式の音声解説 |
| `summary` | 要約 | 技術要点の簡潔なまとめ |
| `full` (デフォルト) | フルセット | フラッシュカード + 音声 |
| 省略時 | `full` | フルセット |

## Step 2: プロジェクト解決

MEX App の `project_id` を解決する:

1. **`.mex.json` を確認**: プロジェクトルート（gitルート）に `.mex.json` が存在すれば、その `project_id` を使用 → **解決完了**
2. **既存プロジェクトを検索**: `mcp__mex__list_projects` でプロジェクト一覧を取得し、ディレクトリ名やリポジトリ名で照合
3. **見つからない場合**: ユーザーに先に `/document` を実行してプロジェクトを作成するよう案内

## Step 3: ソースURL収集

`mcp__mex__get_project_context` でプロジェクトの DevLogEntry を取得し、ソースURLを収集する:

1. `devlog_entries` から `metadata.source_url` が存在するエントリを抽出
2. URLがNotionドメイン（`notion.so` または `notion.site`）のものを優先
3. 最低1件のソースURLが必要。なければエラー:「先に `/document` でNotionドキュメントを生成してください」

収集したソースURLのリストをユーザーに表示し、確認を取る:
```
以下のドキュメントをNotebookLMに取り込みます:
1. {title} - {source_url}
2. {title} - {source_url}
...
```

## Step 4: NotebookLM ノートブック作成

`mcp__notebooklm__notebook_create` でノートブックを作成する:

- **タイトル**: `{プロジェクト名} - 学習ノート` 形式
- レスポンスから `notebook_id` を取得

## Step 5: ソース追加

Step 3 で収集した各ソースURLを `mcp__notebooklm__source_add` で追加:

- `notebook_id`: Step 4 で取得したID
- 各URLを順番に追加
- エラーが出たURLはスキップし、成功/失敗を記録

## Step 6: 学習コンテンツ生成

Step 1 で決定した学習タイプに応じて `mcp__notebooklm__studio_create` を呼び出す:

| タイプ | 操作 |
|--------|------|
| `flashcard` | フラッシュカード生成 |
| `audio` | 音声ポッドキャスト生成 |
| `summary` | 要約ノート生成 |
| `full` | フラッシュカード + 音声の両方を生成 |

## Step 7: 公開リンク生成（任意）

ユーザーに公開リンクを作成するか確認:
- **はい**: `mcp__notebooklm__notebook_share_public` で公開リンクを生成
- **いいえ**: スキップ

## Step 8: MEX App記録

`mcp__mex__save_notebook` を呼び出して MEX App に記録する:

パラメータ:
- **project_id**: Step 2 で解決したID
- **title**: ノートブックのタイトル
- **notebook_id**: Step 4 で取得したID
- **notebook_url**: NotebookLMのノートブックURL
- **technologies**: プロジェクトの技術スタック
- **learning_type**: Step 1 で決定したタイプ
- **public_url**: Step 7 で生成した公開リンク（あれば）

## Step 9: 結果報告

以下の形式でユーザーに報告:

```
## 学習コンテンツを生成しました

**ノートブック**: {タイトル}
**学習タイプ**: {flashcard/audio/summary/full}
**ソース数**: {追加したソースURL数}件
**NotebookLM**: {ノートブックURL}
**公開リンク**: {公開URL（あれば）}
**MEX App**: 記録完了

**取り込んだドキュメント**:
- {title1}
- {title2}
- ...
```

## エラーハンドリング

- **`save_notebook` が見つからない場合**: MEX MCPサーバーの再ビルドと再起動が必要。「`cd mcp-server && npm run build` を実行後、MCPサーバーを再起動してください」と案内
- **NotebookLM MCPが見つからない場合**: 「`pip install notebooklm-mcp-cli && nlm setup add claude-code && nlm login` を実行してください」と案内
- **NotebookLM認証エラー**: 「`nlm login` で再認証してください」と案内
- **ソースURL追加失敗**: 対象URLが非公開またはアクセス不可の可能性。スキップして続行し、失敗したURLを報告
- **プロジェクト未設定**: 「先に `/document` でドキュメントを生成するか、`.mex.json` にproject_idを設定してください」と案内

</instructions>

## 推奨ワークフロー

> **`/document` → `/learn` の順で実行してください**
>
> `/learn` は `/document` で生成されたNotionドキュメントのURLをNotebookLMのソースとして使用します。
> ドキュメントが存在しない場合、ソースを追加できません。
>
> ```
> # 推奨フロー
> 1. 機能を実装する
> 2. git commit する
> 3. /document を実行する（Notionドキュメント生成）
> 4. /learn を実行する（NotebookLM学習コンテンツ生成）
> ```

## 使用例

```
/learn                  # デフォルト（flashcard + audio）
/learn flashcard        # フラッシュカードのみ
/learn audio            # 音声ポッドキャストのみ
/learn summary          # 要約のみ
```
