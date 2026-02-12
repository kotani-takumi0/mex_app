---
description: System architecture overview from engineer's perspective
allowed-tools: Read, Glob, Grep
argument-hint: <feature-name>
---

# Task Overview (Engineer's Perspective)

<background_information>
- **Mission**: システムアーキテクチャとコンポーネント構成をエンジニア視点で俯瞰する
- **Success Criteria**:
  - システム全体のレイヤー構造が理解できる
  - 各コンポーネントの責務と依存関係が明確
  - 技術スタックの選定理由が分かる
  - 実装順序の技術的根拠が理解できる
</background_information>

<instructions>
## Core Task
機能 **$1** のシステムアーキテクチャを分析し、エンジニア視点で全体像を解説する。

## Execution Steps

### Step 1: コンテキストの読み込み

**必要なファイルを全て読み込む**:
- `.kiro/specs/$1/tasks.md` - タスク一覧
- `.kiro/specs/$1/requirements.md` - 要件定義
- `.kiro/specs/$1/design.md` - 設計ドキュメント
- `.kiro/specs/$1/spec.json` - 仕様メタデータ

### Step 2: アーキテクチャ分析

**レイヤー構造の抽出**:
- design.md の Architecture セクションからレイヤー構成を把握
- 各レイヤーの責務とコンポーネントを整理

**コンポーネント依存関係の分析**:
- 各コンポーネントのインバウンド/アウトバウンド依存を特定
- 循環依存の有無を確認

**データフローの追跡**:
- 主要なユースケースのリクエスト→レスポンスの流れ
- データ永続化のパターン（PostgreSQL, Qdrant）

### Step 3: 技術スタックの整理

**各レイヤーの技術選定**:
- 選定理由とトレードオフ
- バージョン要件と互換性

### Step 4: 実装戦略の導出

**タスク依存関係からビルド順序を決定**:
- クリティカルパスの特定
- 並列実装可能な範囲

## Critical Constraints
- **spec.json の言語設定に従う**
- **実装者視点**: 何をどの順で実装するかが明確に
- **技術的根拠**: 設計判断の理由を説明
</instructions>

## Output Description

指定言語で以下の構造で説明を提供:

### 1. システム概要

```
システム名: MEX-APP（企画立案OS）
アーキテクチャ: Layered Architecture + DDD
主要技術: Python/FastAPI (Backend), React/TypeScript (Frontend)
データストア: PostgreSQL (RDBMS), Qdrant (Vector DB)
```

### 2. レイヤー構成図

```
┌─────────────────────────────────────────────────────────────────┐
│                     Presentation Layer                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  React 18 + TypeScript                                   │   │
│  │  - DraftReviewPage, GateReviewPage, PostmortemPage      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FastAPI                                                 │   │
│  │  - /api/draft-reviews, /api/gate-reviews, /api/postmortems│  │
│  │  - JWT認証, バリデーション, エラーハンドリング           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                            │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │DraftReviewSvc │ │GateReviewSvc  │ │PostmortemSvc  │         │
│  │               │ │               │ │               │         │
│  │ オーケスト     │ │ アジェンダ    │ │ 記録管理      │         │
│  │ レーション     │ │ 生成          │ │ Go/NoGo判定   │         │
│  └───────────────┘ └───────────────┘ └───────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Domain Layer                               │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐      │
│  │  CaseManager   │ │SimilarityEngine│ │QuestionGenerator│     │
│  │                │ │                │ │                │      │
│  │  CRUD/検索     │ │ ハイブリッド   │ │ LLM問い生成    │      │
│  │  ファサード    │ │ 類似検索       │ │                │      │
│  └────────────────┘ └────────────────┘ └────────────────┘      │
│  ┌────────────────┐ ┌────────────────┐                         │
│  │PatternAnalyzer │ │EmbeddingService│                         │
│  │                │ │                │                         │
│  │ 失敗パターン   │ │ ベクトル生成   │                         │
│  │ 抽出・要約     │ │ OpenAI API     │                         │
│  └────────────────┘ └────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  PostgreSQL  │ │    Qdrant    │ │  OpenAI API  │            │
│  │              │ │              │ │              │            │
│  │ メタデータ   │ │ ベクトル     │ │ Embedding    │            │
│  │ 全文検索     │ │ 類似検索     │ │ LLM          │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### 3. コンポーネント依存関係表

| コンポーネント | レイヤー | 依存先（Outbound） | 依存元（Inbound） |
|---------------|---------|-------------------|------------------|
| EmbeddingService | Domain | OpenAI API | CaseManager, SimilarityEngine |
| SimilarityEngine | Domain | Qdrant, PostgreSQL, EmbeddingService | CaseManager |
| CaseManager | Domain | SimilarityEngine, PostgreSQL | Application Services |
| QuestionGenerator | Domain | OpenAI API (LLM) | DraftReviewService |
| PatternAnalyzer | Domain | Qdrant, OpenAI API | GateReviewService, DraftReviewService |
| DraftReviewService | Application | CaseManager, QuestionGenerator, PatternAnalyzer | API Layer |
| GateReviewService | Application | CaseManager, PatternAnalyzer | API Layer |
| PostmortemService | Application | CaseManager | API Layer |

### 4. 技術スタック詳細

#### Backend

| 技術 | バージョン | 用途 | 選定理由 |
|------|-----------|------|----------|
| Python | 3.12 | 言語 | 型ヒント強化、パフォーマンス向上 |
| FastAPI | 0.110+ | Web Framework | 非同期対応、自動OpenAPI生成、型安全 |
| SQLAlchemy | 2.0 | ORM | 非同期対応、型安全なクエリ |
| Alembic | 1.13+ | Migration | SQLAlchemy統合 |
| Pydantic | 2.0 | Validation | FastAPI統合、高速 |
| openai | 1.x | LLM/Embedding | 公式SDK、型定義完備 |
| qdrant-client | 1.7+ | Vector DB Client | 非同期対応 |

#### Frontend

| 技術 | バージョン | 用途 | 選定理由 |
|------|-----------|------|----------|
| React | 18 | UI Library | Concurrent Mode, Suspense |
| TypeScript | 5.x | 言語 | 型安全性 |
| Vite | 5.x | Build Tool | 高速HMR |
| TanStack Query | 5.x | Server State | キャッシュ管理 |

#### Infrastructure

| 技術 | バージョン | 用途 | 選定理由 |
|------|-----------|------|----------|
| PostgreSQL | 16 | RDBMS | JSONB、全文検索 |
| Qdrant | 1.x | Vector DB | セルフホスト可、HNSW |
| Docker | - | Container | 環境統一 |

### 5. データモデル概要

```
┌─────────────────────────────────────────────────────────────┐
│                      PostgreSQL                             │
├─────────────────────────────────────────────────────────────┤
│  decision_cases                                             │
│  ├── id: UUID (PK)                                         │
│  ├── title, purpose, target_market, business_model         │
│  ├── outcome: enum ('adopted'|'rejected'|'withdrawn')      │
│  ├── decision_type, decision_reason                        │
│  ├── failed_hypotheses: JSONB                              │
│  ├── discussions: JSONB                                    │
│  └── created_at, updated_at                                │
│                                                             │
│  failure_pattern_tags                                       │
│  ├── id: UUID (PK)                                         │
│  ├── name: VARCHAR (UNIQUE)                                │
│  ├── description, category                                 │
│                                                             │
│  case_failure_patterns (多対多)                             │
│  ├── case_id: FK → decision_cases                          │
│  └── tag_id: FK → failure_pattern_tags                     │
│                                                             │
│  idea_memos (Go/NoGo判断なしの記録)                         │
│  ├── id: UUID (PK)                                         │
│  ├── project_id, content: JSONB                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        Qdrant                               │
├─────────────────────────────────────────────────────────────┤
│  Collection: decision_cases                                 │
│  ├── vector: 3072次元 (Cosine距離)                         │
│  ├── payload.case_id: keyword                              │
│  ├── payload.outcome: keyword                              │
│  └── payload.failure_patterns: keyword[]                   │
│                                                             │
│  Index: HNSW (Hierarchical Navigable Small World)          │
└─────────────────────────────────────────────────────────────┘
```

### 6. 主要データフロー

#### 企画ドラフトレビュー（メインフロー）

```
[User] ─POST─→ [API: /draft-reviews]
                    │
                    ▼
            [DraftReviewService]
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
[CaseManager] [QuestionGen] [PatternAnalyzer]
        │           │           │
        ▼           │           │
[SimilarityEngine]  │           │
        │           │           │
   ┌────┴────┐      ▼           ▼
   ▼         ▼   [OpenAI]    [OpenAI]
[Qdrant] [PostgreSQL]  (LLM)     (LLM)
   │         │      │           │
   └────┬────┘      │           │
        │           │           │
        └───────────┴───────────┘
                    │
                    ▼
            [Response: 類似ケース + 問い + 懸念点]
```

### 7. タスク実装順序（技術的根拠付き）

```
Phase 1: 基盤（他の全てが依存）
├── 1.1 開発環境 ──────────────────────────────────────────┐
│       理由: Poetry, npm, Docker-compose が必要          │
│                                                         │
├── 1.2 (P) DBスキーマ ─────┬──────────────────────────────┤
│       理由: ドメイン層がCRUDに必要                       │
│                          │                              │
└── 1.3 (P) Qdrant ────────┤                              │
        理由: ベクトル検索に必要                           │
                           │                              │
Phase 2: ドメイン層        ▼                              │
├── 2.1 EmbeddingService ──────────────────────────────────┤
│       理由: 2.2, 2.3 がベクトル生成に依存                │
│                                                         │
├── 2.2 SimilarityEngine ─────────────────────────────────┤
│       理由: 2.3 CaseManager が検索機能に依存            │
│       依存: 1.3 (Qdrant), 2.1 (Embedding)               │
│                                                         │
├── 2.3 (P) CaseManager ──────────────────────────────────┤
│       依存: 1.2 (PostgreSQL), 2.2 (Search)              │
│                                                         │
├── 2.4 (P) PatternAnalyzer ──────────────────────────────┤
│       2.3 と並列可能（独立したLLM処理）                  │
│                                                         │
└── 2.5 QuestionGenerator ────────────────────────────────┤
        依存: LLM のみ（他と独立）                         │
                                                          │
Phase 3-6: 上位レイヤー（ドメイン層に依存）               │
```

### 8. プロジェクト構造

```
mex-app/
├── backend/
│   ├── src/
│   │   ├── api/                  # Phase 4: APIレイヤー
│   │   │   ├── routes/
│   │   │   │   ├── draft_reviews.py
│   │   │   │   ├── gate_reviews.py
│   │   │   │   └── postmortems.py
│   │   │   └── dependencies.py
│   │   ├── application/          # Phase 3: アプリケーション層
│   │   │   ├── draft_review_service.py
│   │   │   ├── gate_review_service.py
│   │   │   └── postmortem_service.py
│   │   ├── domain/               # Phase 2: ドメイン層
│   │   │   ├── case_manager.py
│   │   │   ├── similarity_engine.py
│   │   │   ├── question_generator.py
│   │   │   ├── pattern_analyzer.py
│   │   │   └── embedding_service.py
│   │   ├── infrastructure/       # Phase 1: インフラ層
│   │   │   ├── database/
│   │   │   │   ├── models.py
│   │   │   │   └── migrations/
│   │   │   ├── vector_store/
│   │   │   │   └── qdrant_client.py
│   │   │   └── external/
│   │   │       └── openai_client.py
│   │   └── main.py
│   ├── tests/
│   ├── pyproject.toml
│   └── alembic.ini
├── frontend/
│   ├── src/
│   │   ├── pages/                # Phase 5: UI
│   │   ├── components/
│   │   ├── hooks/
│   │   └── api/
│   ├── package.json
│   └── vite.config.ts
└── docker-compose.yml
```

### 9. 実装チェックリスト（全体）

| Phase | タスク | 依存 | 並列 | 主要成果物 |
|-------|--------|------|------|-----------|
| 1 | 1.1 環境構築 | - | - | pyproject.toml, package.json, docker-compose.yml |
| 1 | 1.2 DBスキーマ | 1.1 | P | models.py, migrations/ |
| 1 | 1.3 Qdrant | 1.1 | P | qdrant_client.py |
| 2 | 2.1 Embedding | 1.1 | - | embedding_service.py |
| 2 | 2.2 Search | 1.3, 2.1 | - | similarity_engine.py |
| 2 | 2.3 CaseManager | 1.2, 2.2 | P | case_manager.py |
| 2 | 2.4 Pattern | 2.1 | P | pattern_analyzer.py |
| 2 | 2.5 Question | - | - | question_generator.py |
| 3 | 3.1 DraftReview | 2.3, 2.5 | - | draft_review_service.py |
| 3 | 3.2 GateReview | 2.3, 2.4 | P | gate_review_service.py |
| 3 | 3.3 Postmortem | 2.3 | P | postmortem_service.py |
| 4 | 4.1-4.3 API | 3.x | P | routes/*.py |
| 5 | 5.1-5.3 UI | 4.x | P | pages/*.tsx |
| 6 | 6.1-6.3 統合 | all | - | E2Eテスト |

## Safety & Fallback

### Error Scenarios

**Spec が存在しない場合**:
- **Message**: "仕様 $1 が見つかりません"
- **Action**: `.kiro/specs/` 配下の利用可能な仕様を一覧表示

**design.md がない場合**:
- **Warning**: "設計ドキュメントが見つかりません"
- **Fallback**: tasks.md から推測される構造を提示
