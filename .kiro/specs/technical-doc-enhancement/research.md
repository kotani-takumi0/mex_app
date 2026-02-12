# Research & Design Decisions

## Summary
- **Feature**: `technical-doc-enhancement`
- **Discovery Scope**: Extension（既存 `/document` スキルのドキュメント構造変更）
- **Key Findings**:
  - 変更対象は `.claude/commands/document.md` の Step 3 ドキュメント構造テンプレートのみ
  - バックエンドAPI・MCPサーバー・フロントエンドへの変更は不要
  - LLM（Claude）がドキュメント生成エンジンとして機能し、プロンプト指示に従ってコンテンツを構造化する

## Research Log

### 既存 `/document` スキルの拡張ポイント分析
- **Context**: 現行スキルのどの部分を変更すれば要件を満たせるか
- **Sources Consulted**: `.claude/commands/document.md`、MCP サーバー実装、バックエンドAPI
- **Findings**:
  - Step 1（コンテキスト収集）: git diff/log による変更内容取得は既存。技術分解・Q&A生成に必要な情報は既に収集されている
  - Step 2（Notion親ページ解決）: 変更不要
  - Step 3（ドキュメント作成）: ここのMarkdownテンプレートを差し替えるのが本変更の核心
  - Step 4（MEX App記録）: パラメータ構造は変更なし
  - Step 5（結果報告）: 新構造に合わせた報告形式の微調整のみ
- **Implications**: 変更スコープが極めて限定的。プロンプトのドキュメント構造指示のみの変更で全要件を実現可能

### Notion MCP のMarkdown対応範囲
- **Context**: 新しい階層構造（H2/H3/箇条書き/Q&A形式）がNotion MCPで正しくレンダリングされるか
- **Sources Consulted**: `mcp__notion__notion-create-pages` の使用実績（既存スキル）
- **Findings**:
  - `notion-create-pages` は標準Markdown（H2, H3, 箇条書き, コードブロック, 太字）をサポート
  - Q&A形式（`**Q:**` / `**A:**`）も太字+テキストとして問題なくレンダリング可能
  - ネスト構造もNotionのトグルブロックやインデントで表現可能
- **Implications**: Notion側の制約による構造変更は不要

### ドキュメント生成品質の制御手法
- **Context**: LLMが汎用的なテンプレ解説ではなく、実装コードに基づく具体的な内容を生成するための指示設計
- **Sources Consulted**: 既存プロンプト、要件 6（品質担保）
- **Findings**:
  - 現行 Step 1 で `git diff HEAD~1` の出力を取得済み → これを「技術分解」と「解説」の入力として明示的に参照させる指示が必要
  - `get_project_context` で技術スタック情報も取得済み → 代替技術の比較に活用可能
  - 具体性を担保するには「git diff から具体的な設定値・ライブラリ名・関数名を引用すること」という制約をプロンプトに含める必要がある
- **Implications**: プロンプトに「git diff の内容を必ず参照し、具体的な値を引用する」という指示を明記する

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| プロンプト変更のみ | document.md の Step 3 テンプレートを差し替え | 変更最小、既存フロー維持、即時適用可能 | LLM の生成品質に依存 | 採用 |
| バックエンド拡張 | 専用の構造化APIエンドポイント追加 | 構造の強制力が高い | 過剰設計、既存APIとの整合性管理が必要 | 不採用：プロンプト変更で十分 |
| 専用テンプレートエンジン | Notion側にテンプレートページを用意 | 構造の一貫性保証 | Notion MCP の制約、メンテナンスコスト | 不採用：柔軟性が低下する |

## Design Decisions

### Decision: プロンプト駆動のドキュメント構造変更
- **Context**: 6つの要件を実現するためのアーキテクチャ選択
- **Alternatives Considered**:
  1. バックエンドに構造化ロジックを追加し、APIレスポンスとしてドキュメント構造を返す
  2. MCP サーバーに新ツール `save_structured_document` を追加する
  3. `/document` スキルのプロンプト指示のみを変更する
- **Selected Approach**: Option 3 — プロンプト指示の変更のみ
- **Rationale**:
  - 変更対象ファイルが1つ（`.claude/commands/document.md`）
  - 既存のワークフロー（Step 1〜5）を維持
  - バックエンドAPI・MCPサーバー・フロントエンドへの変更が不要
  - LLM の文脈理解力を活用して、git diff から技術分解・解説・Q&Aを自然に生成できる
- **Trade-offs**: LLM の生成品質に依存するが、プロンプトの具体的な指示と構造制約で品質を担保する
- **Follow-up**: 実際の生成結果を検証し、プロンプトの調整を繰り返す

### Decision: 4セクション階層構造
- **Context**: ドキュメントの構造をどう設計するか
- **Selected Approach**: 実装サマリー → 技術分解 → 各技術解説 → 想定Q&A の4層
- **Rationale**: ユーザーの出発点（機能指示）から技術理解へ自然に導く認知的な流れに沿っている。「何を作ったか」→「何が必要だったか」→「それは何か」→「説明できるか」の順序

## Risks & Mitigations
- **LLM生成品質のばらつき**: プロンプトに「git diff の具体値を引用する」「汎用説明のみ不可」の制約を明記して軽減
- **ドキュメントの長大化**: 技術要素の重要度に応じた深さ調整指示（コア技術は詳細、補助は簡潔）で制御
- **Notionページの可読性**: H2/H3 の階層構造とNotionの折りたたみ機能で対応

## References
- `.claude/commands/document.md` — 現行スキル定義
- `mcp-server/src/tools/record-activity.ts` — save_document ツール実装
- `backend/app/api/devlogs.py` — DevLog APIエンドポイント
