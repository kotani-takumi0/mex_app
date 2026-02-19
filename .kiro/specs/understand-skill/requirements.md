# Requirements Document

## Introduction

AI コーディングツールで作ったアプリや、途中から参加したプロジェクトの既存コードベースを理解したいというニーズは大きいが、現在の MEX App にはこれを支援する機能がない。`/document` スキルは `git diff`（直前のコミット差分）をベースにドキュメントを生成するため、過去に遡っての分析や、既存コードベース全体の理解支援には対応していない。

本機能（`/understand` スキル）は、既存コードベースをモジュール/機能単位で分析し、各モジュールの技術ドキュメントを Notion に自動生成して MEX App に開発ログとして記録する。これにより以下のコールドスタート問題を解決する：

- **自分がAIで作ったアプリを後から理解したい**（最も一般的なケース）
- **途中から MEX を導入し、過去分のドキュメントがない**
- **既存プロジェクトに途中参加し、コードベースを把握したい**
- **ポートフォリオに過去の作品を追加し、理解を証明したい**

`/document` が「これからの変更を記録する」のに対し、`/understand` は「今あるものを理解する」ためのスキルである。

## Requirements

### Requirement 1: コードベースのモジュール分解
**Objective:** As a **AI実装ユーザー**, I want **既存コードベースが自動的にモジュール/機能単位に分解されること**, so that **巨大なコードベースを一度に理解しようとせず、意味のある単位で段階的に学習できる**。

#### Acceptance Criteria
1. When [`/understand` が引数なしで実行された], the [Codebase Analyzer] shall [プロジェクトルートからディレクトリ構造、設定ファイル（package.json, requirements.txt 等）、ソースコードを走査し、機能単位のモジュール一覧を自動検出する]。
2. The [Codebase Analyzer] shall [検出した各モジュールについて、モジュール名・主要な責務・含まれるファイル群・推定行数を一覧としてユーザーに表示する]。
3. When [`/understand [モジュール名 or ディレクトリパス]` のように範囲が指定された], the [Codebase Analyzer] shall [指定された範囲のみを分析対象とし、全体スキャンをスキップする]。
4. The [Codebase Analyzer] shall [モジュール一覧を表示後、ユーザーに「全モジュールを生成する」か「特定のモジュールを選択する」かを確認する]。

### Requirement 2: モジュール単位の技術ドキュメント生成
**Objective:** As a **AI実装ユーザー**, I want **各モジュールについて、実装コードに基づいた技術ドキュメントが生成されること**, so that **AIが選択した技術の意味と設計判断の根拠を理解できる**。

#### Acceptance Criteria
1. The [Document Generator] shall [各モジュールについて、以下の構造でNotionドキュメントを生成する：(a) モジュール概要 — このモジュールの責務と全体における位置づけ、(b) 技術分解 — モジュールを構成する技術要素の一覧と各要素の役割、(c) 各技術要素の解説 — 「それは何か / なぜ必要か / 他の選択肢 / 壊れたらどうなるか」の4段階解説、(d) 想定Q&A — 基礎・判断・応用の3段階で各2問以上]。
2. The [Document Generator] shall [ドキュメント内容を実装コードの具体的な設定値・ライブラリ名・関数名・ファイルパスに基づいて生成し、汎用的な説明のみにしない]。
3. The [Document Generator] shall [モジュール間の依存関係（例：「認証モジュールはJWTモジュールに依存」）を概要セクションに含める]。
4. The [Document Generator] shall [`/document` の既存ドキュメント構造（H2/H3の階層構造、Notion Markdown形式）と統一されたフォーマットを使用する]。

### Requirement 3: Notion への一括ドキュメント作成
**Objective:** As a **AI実装ユーザー**, I want **生成されたドキュメント群がNotionに整理された形で保存されること**, so that **後から参照しやすく、`/learn` でNotebookLMに取り込める状態になる**。

#### Acceptance Criteria
1. The [Document Generator] shall [`/document` と同じNotion親ページ（`{プロジェクト名} MEX Docs`）の配下にドキュメントを作成する]。
2. The [Document Generator] shall [各モジュールのドキュメントを個別のNotionページとして作成する（1モジュール = 1ページ）]。
3. The [Document Generator] shall [Notionページのタイトルを「[Understand] {モジュール名}」形式とし、`/document` で生成されたページと区別できるようにする]。
4. The [Document Generator] shall [作成後、各NotionページのURLを取得する]。

### Requirement 4: MEX App への一括記録
**Objective:** As a **AI実装ユーザー**, I want **生成された全ドキュメントがMEX Appの開発ログとして記録されること**, so that **ポートフォリオとダッシュボードに反映され、学習進捗が可視化される**。

#### Acceptance Criteria
1. The [Recorder] shall [各モジュールのドキュメントを `mcp__mex__save_document` で個別にMEX Appに記録する]。
2. The [Recorder] shall [以下のパラメータを設定する：(a) title — モジュール名の短い要約、(b) category — `learning`（既存コードの理解であるため）、(c) technologies — モジュールで使用されている主要技術、(d) source_url — NotionページのURL]。
3. The [Recorder] shall [記録完了後、成功/失敗の件数サマリーをユーザーに報告する]。

### Requirement 5: プロジェクト解決とセットアップ
**Objective:** As a **AI実装ユーザー**, I want **`/understand` がプロジェクトの自動検出・作成を含め、セットアップ不要で使えること**, so that **MEXを初めて使うプロジェクトでもすぐに実行できる**。

#### Acceptance Criteria
1. The [Project Resolver] shall [`/document` と同じプロジェクト解決ロジック（`.mex.json` → `list_projects` 照合 → 新規作成）を使用する]。
2. The [Project Resolver] shall [プロジェクト新規作成時、コードベース分析の結果から `title`、`description`、`technologies`、`repository_url` を自動推定する]。
3. The [Project Resolver] shall [解決または作成した `project_id` を `.mex.json` に保存し、以降の `/document` や `/learn` でも利用可能にする]。

### Requirement 6: `/learn` との連携
**Objective:** As a **AI実装ユーザー**, I want **`/understand` で生成されたドキュメントが `/learn` でそのまま利用できること**, so that **理解→学習→証明のパイプラインが途切れない**。

#### Acceptance Criteria
1. The [Document Generator] shall [生成したNotionドキュメントのURLを `source_url` フィールドに保存し、`/learn` の Step 3（ソースURL収集）で自動的に検出される状態にする]。
2. The [Understand Skill] shall [実行完了後の結果報告に、`/learn` への導線（コマンド例）を含める]。

### Requirement 7: 実行進捗の可視化
**Objective:** As a **AI実装ユーザー**, I want **複数モジュールの分析・ドキュメント生成の進捗がリアルタイムで確認できること**, so that **大規模プロジェクトでも安心して待てる**。

#### Acceptance Criteria
1. The [Understand Skill] shall [モジュール分析の開始時に、検出したモジュール数と推定所要時間をユーザーに表示する]。
2. The [Understand Skill] shall [各モジュールのドキュメント生成完了時に、進捗状況（例：「3/7 モジュール完了: 認証システム」）をユーザーに表示する]。
3. The [Understand Skill] shall [エラーが発生したモジュールをスキップして続行し、最終報告で失敗したモジュールをまとめて報告する]。
