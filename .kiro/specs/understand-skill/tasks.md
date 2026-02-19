# Implementation Plan

- [x] 1. `/understand` スキル定義ファイルの骨格を作成する
- [x] 1.1 `.claude/skills/understand.md` のフロントマター・背景情報・全体構造を定義する
  - フロントマター: description, allowed-tools, argument-hint を `/document` に準拠して定義
  - allowed-tools に Glob, Read, Grep, Bash(git:*, curl:*, wc:*, cat ~/.mex/config.json:*), Write, mcp__notion__*, mcp__mex__* を設定
  - background_information: Mission（既存コードベースの理解促進）、フロー概要（5フェーズ）、使用インフラを記述
  - 全ステップの見出し構造（Step 1〜Step 5）を定義
  - _Requirements: Req 1, Req 2, Req 5, Req 7_

- [x] 2. Step 1: コードベース分析ロジックを実装する
- [x] 2.1 プロジェクトタイプ判定とモジュール自動検出の手順を記述する
  - プロジェクトタイプ判定: package.json / requirements.txt / pyproject.toml の有無で Node.js / Python / モノレポを判別
  - ディレクトリ構造を Glob で走査し、設計ドキュメントのヒューリスティック（frontend/src/components/, backend/app/api/ 等）でモジュール候補を検出
  - 各モジュール候補について Read で主要ファイルを読み、責務を推定する指示を記述
  - モジュール情報（名前・責務・主要ファイル・推定行数・使用技術）をテーブル形式でユーザーに表示する指示を記述
  - _Requirements: Req 1.1, Req 1.2_

- [x] 2.2 スコープ指定と対話型モジュール選択の手順を記述する
  - `$ARGUMENTS` が指定された場合の分岐ロジック: ディレクトリパス / モジュール名キーワード / なし の3パターン
  - 全モジュール表示後にユーザーへ「全モジュールを生成」「特定モジュールを選択」の確認を取る指示を記述
  - _Requirements: Req 1.3, Req 1.4_

- [x] 3. Step 2: プロジェクト解決ロジックを実装する
- [x] 3.1 `/document` と同じプロジェクト解決ロジックを記述する
  - `.mex.json` 確認 → `list_projects` 照合 → `curl POST /projects` 新規作成 → `.mex.json` 保存の4段階
  - `/document` の Step 1.5 と同一のロジックを、`/understand` の文脈（コードベース分析結果から title/description/technologies を推定）に合わせて記述
  - _Requirements: Req 5.1, Req 5.2, Req 5.3_

- [x] 4. Step 3: Notion 親ページ解決を実装する
- [x] 4.1 `/document` と同じ Notion 親ページ解決ロジックを記述する
  - `notion-search` で `{プロジェクト名} MEX Docs` を検索 → 見つかれば使用 → なければ新規作成
  - `/document` の Step 2 と同一のロジック
  - _Requirements: Req 3.1_

- [x] 5. Step 4: モジュールごとのドキュメント生成ループを実装する
- [x] 5.1 ドキュメント生成の共通テンプレートを記述する
  - `/document` と統一されたドキュメント構造（モジュール概要・技術分解・各技術解説・想定Q&A）のテンプレートを記述
  - `/document` との差分: 冒頭セクションが「実装サマリー」→「モジュール概要」（責務・位置づけ・依存関係・構成ファイル一覧）
  - 技術分解・解説・Q&A は `/document` と同一フォーマット
  - 品質制約: 実装コードの具体的な設定値・ライブラリ名・関数名・ファイルパスに基づいて生成する指示
  - Notion タイトルを `[Understand] {モジュール名}` 形式にする指示
  - _Requirements: Req 2.1, Req 2.2, Req 2.3, Req 2.4, Req 3.2, Req 3.3_

- [x] 5.2 ループ処理と MEX 記録の手順を記述する
  - 選択されたモジュールを順番に処理するループ構造を記述
  - 各イテレーション: ソースコード Read → ドキュメント生成 → `notion-create-pages` → URL 取得 → `save_document`（category: learning）
  - save_document パラメータ: title（モジュール名要約）、category（learning）、technologies（モジュール使用技術）、source_url（Notion URL）
  - 進捗表示: 「i/N モジュール処理中: {名前}」→ 「i/N 完了: {名前}」
  - エラー発生時はスキップして次のモジュールへ続行する指示
  - _Requirements: Req 4.1, Req 4.2, Req 7.1, Req 7.2, Req 7.3_

- [x] 6. Step 5: 結果報告と `/learn` 導線を実装する
- [x] 6.1 結果報告テンプレートと `/learn` 導線を記述する
  - サマリー形式: タイトル、分析モジュール数、成功/失敗件数、生成された Notion ページ一覧（タイトル + URL）
  - エラーがあった場合は失敗モジュールと理由を一覧表示
  - `/learn` コマンド例を導線として表示する指示を記述
  - _Requirements: Req 4.3, Req 6.1, Req 6.2_

- [x] 7. エラーハンドリングと使用例セクションを追加する
- [x] 7.1 エラーハンドリングブロックと使用例を記述する
  - 設計ドキュメントで定義した6種のエラーケースの対応指示を記述
  - 推奨ワークフロー（`/understand` → `/learn` の順）を記述
  - 使用例（引数なし / スコープ指定 / モジュール名指定）を記述
  - _Requirements: Req 6.2, Req 7.3_

- [x] 8. MEX App 自身で `/understand` を実行して検証する
- [x] 8.1 MEX App プロジェクトで全体分析を実行し、動作を検証する
  - ✅ `/understand` を MEX App プロジェクトで実行し、14 モジュールが正しく検出された
  - ✅ 2 モジュール（認証システム、APIエンドポイント層）を選択してドキュメント生成を実行し、Notion ページの構造・品質を確認
  - ✅ MEX App に開発ログとして記録された（entry_id: 2fa0271b, 283089ef）
  - ⬜ `/learn` で生成ドキュメントがソースとして検出されることは次回確認
  - _Requirements: Req 1〜7 全て_

- [ ] 8.2 スコープ指定の動作を検証する
  - `/understand backend` でバックエンドのみ分析されることを確認
  - `/understand auth` で認証関連モジュールが検出されることを確認
  - _Requirements: Req 1.3_
