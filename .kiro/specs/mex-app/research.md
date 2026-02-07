# Research & Design Decisions

## Summary
- **Feature**: `mex-app`
- **Discovery Scope**: New Feature（グリーンフィールド開発）
- **Key Findings**:
  - RAG（Retrieval-Augmented Generation）アーキテクチャが類似ケース検索と問い生成に最適
  - ハイブリッド検索（ベクトル検索 + テキスト検索）が2026年のベストプラクティス
  - Case-Based Reasoning（CBR）とLLM統合がニューロシンボリックハイブリッドシステムとして有効

## Research Log

### RAGアーキテクチャパターン
- **Context**: 過去の意思決定ケースから類似事例を検索し、問いを生成するシステムが必要
- **Sources Consulted**:
  - [AWS RAG Documentation](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
  - [Pinecone RAG Guide](https://www.pinecone.io/learn/retrieval-augmented-generation/)
  - [RAG in 2026 Enterprise AI](https://www.techment.com/blogs/blogs-rag-in-2026-enterprise-ai/)
- **Findings**:
  - RAGは4つのコアコンポーネント: Ingestion、Retrieval、Augmentation、Generation
  - 512トークンのチャンクサイズが最適なパフォーマンス
  - ハイブリッド検索（ベクトル + テキスト）が2026年の推奨デフォルト
  - Agentic RAGにより、どの質問をするか、どのツールを使うかを動的に決定可能
- **Implications**: 意思決定ケースの類似検索にRAGパイプラインを採用、問い生成にLLMを活用

### ベクトルデータベース選定
- **Context**: 意思決定ケースの埋め込みベクトルを保存・検索する必要がある
- **Sources Consulted**:
  - [Top Vector Database Solutions 2026](https://azumo.com/artificial-intelligence/ai-insights/top-vector-database-solutions)
  - [Qdrant Documentation](https://qdrant.tech/)
- **Findings**:
  - ベクトルデータベース市場は2024年の$1.73Bから2032年には$10.6Bに成長予測
  - Qdrant: オープンソース、エンタープライズグレードのパフォーマンス、コスト効率
  - Weaviate: AI機能内蔵、自動埋め込み生成
  - ANN（近似最近傍）検索がKNNより効率的
- **Implications**: Qdrantをプライマリベクトルストアとして採用（オープンソース、セルフホスト可能）

### Case-Based Reasoning (CBR) とLLM統合
- **Context**: 過去の失敗パターンから学習し、新規案件に適用する仕組みが必要
- **Sources Consulted**:
  - [CBR-LLM Research](https://www.emergentmind.com/topics/case-based-reasoning-augmented-large-language-model-cbr-llm)
  - [Semantic Search with LangChain](https://docs.langchain.com/oss/python/langchain/knowledge-base)
- **Findings**:
  - CBR-LLMはニューロシンボリックハイブリッドシステムとして機能
  - 類似メトリクスを使用して類似ケースを検索し、LLM駆動の推論に組み込む
  - セマンティックキャッシュにより、類似クエリを認識し効率化
- **Implications**: 失敗パターンのタグ付けとセマンティック検索を組み合わせたハイブリッドアプローチを採用

### ナレッジマネジメントシステムパターン
- **Context**: 組織の意思決定ログを構造化・資産化する必要がある
- **Sources Consulted**:
  - [Enterprise AI Knowledge Management 2026](https://www.gosearch.ai/faqs/enterprise-ai-knowledge-management-guide-2026/)
  - [Architecture Decision Records](https://github.com/joelparkerhenderson/architecture-decision-record)
- **Findings**:
  - 2026年のKMSはAIをコア機能として統合（セマンティック検索、自動タグ付け、推奨）
  - ADR（Architecture Decision Record）パターンが意思決定ログの標準
  - ナレッジインテリジェンスレイヤーがAIシステムへの知識注入に必須
- **Implications**: 意思決定ケースをADRに類似した構造化フォーマットで保存

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| RAG + Vector DB | 埋め込みベクトルによる類似検索とLLM生成 | 高精度な類似検索、最新情報の反映 | ベクトルDB運用コスト | 2026年のエンタープライズ標準 |
| Pure LLM Fine-tuning | ドメイン特化モデルの微調整 | 高速推論 | 頻繁な再学習コスト、データ更新困難 | 知識が頻繁に変更される場合は不適 |
| Keyword Search + Rules | 従来のキーワード検索とルールベース | 実装シンプル | セマンティック理解の欠如 | 要件を満たせない |
| Hybrid RAG | ベクトル検索 + テキスト検索 + リランキング | 最高精度、柔軟性 | 複雑性増加 | **採用パターン** |

## Design Decisions

### Decision: Hybrid RAGアーキテクチャの採用
- **Context**: 過去の意思決定ケースから類似事例を高精度で検索し、文脈に応じた問いを生成する必要がある
- **Alternatives Considered**:
  1. Pure Vector Search — シンプルだが、キーワード一致が重要な場合に精度低下
  2. Pure Keyword Search — セマンティック類似性を捉えられない
  3. LLM Fine-tuning — データ更新時の再学習コストが高い
- **Selected Approach**: Hybrid RAG（ベクトル検索 + BM25テキスト検索 + リランキング）
- **Rationale**: 2026年のベストプラクティスであり、セマンティック類似性とキーワード一致の両方を活用可能
- **Trade-offs**: 実装複雑性は増すが、検索精度と柔軟性で優位
- **Follow-up**: リランキングモデルの選定、チャンクサイズの最適化

### Decision: Qdrantをベクトルストアとして採用
- **Context**: 意思決定ケースの埋め込みベクトルを効率的に保存・検索する必要がある
- **Alternatives Considered**:
  1. Pinecone — マネージドだがコスト高
  2. Weaviate — 機能豊富だがオーバーヘッド
  3. Qdrant — オープンソース、セルフホスト可能
- **Selected Approach**: Qdrant
- **Rationale**: オープンソースでセルフホスト可能、エンタープライズグレードのパフォーマンス、コスト効率
- **Trade-offs**: 運用責任は増すが、コストとデータ主権で優位
- **Follow-up**: インデックス設計、スケーリング戦略

### Decision: 構造化された意思決定ケースフォーマット
- **Context**: 意思決定ログを将来の検索・学習に活用可能な形式で保存する必要がある
- **Alternatives Considered**:
  1. 自由形式テキスト — 柔軟だが構造化困難
  2. 固定フォーマット — 構造化しやすいが柔軟性欠如
  3. ADR類似フォーマット — 構造化と柔軟性のバランス
- **Selected Approach**: ADR（Architecture Decision Record）に類似した構造化フォーマット
- **Rationale**: 業界標準、意思決定の文脈・選択肢・理由を明確に記録可能
- **Trade-offs**: 入力時のユーザー負担は増すがテンプレート提供で軽減
- **Follow-up**: 入力テンプレートUIの設計

## Risks & Mitigations
- **Risk 1**: ベクトル検索の精度が不十分 — ハイブリッド検索とリランキングで軽減
- **Risk 2**: LLM生成コストが高い — キャッシュ戦略とセマンティックキャッシュで軽減
- **Risk 3**: ユーザーが構造化入力を面倒に感じる — テンプレートとAI補助入力で軽減
- **Risk 4**: 初期データ不足で類似検索が機能しない — サンプルデータ投入とコールドスタート戦略

## References
- [AWS RAG Documentation](https://aws.amazon.com/what-is/retrieval-augmented-generation/) — RAGの基本概念
- [Pinecone RAG Guide](https://www.pinecone.io/learn/retrieval-augmented-generation/) — RAGアーキテクチャパターン
- [Top Vector Database Solutions 2026](https://azumo.com/artificial-intelligence/ai-insights/top-vector-database-solutions) — ベクトルDB比較
- [Enterprise AI Knowledge Management 2026](https://www.gosearch.ai/faqs/enterprise-ai-knowledge-management-guide-2026/) — エンタープライズKMS動向
- [CBR-LLM Research](https://www.emergentmind.com/topics/case-based-reasoning-augmented-large-language-model-cbr-llm) — Case-Based ReasoningとLLM統合
