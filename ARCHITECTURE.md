# MEX App アーキテクチャ設計書 — AI開発ポートフォリオへの転換

## 1. コンセプト

### 1.1 課題

バイブコーディング（AI支援開発）の普及により、誰でもアプリを作れる時代になった。
現在のポートフォリオは完成物の公開に留まっており、AIに任せて作っただけでも同じ成果物が出来てしまう。
企業側は候補者が本当に技術を理解しているか判別しにくくなっている。

### 1.2 解決策

開発**過程**を自動記録し、技術の**理解**を自分の言葉で証明する新しいポートフォリオプラットフォーム。

1. **MCPサーバー**によりAI開発の過程を自動記録（入力の手間を大幅削減）
2. コミットから**Notionに教育的ドキュメントを自動生成**（WHY・HOWの解説 + 基礎〜応用Q&A）
3. ドキュメントで学んだことを**自分の言葉でアプリに記録**させる
4. 「完成物 + 過程 + 理解の記録」を企業に見せる**新しいポートフォリオ**

### 1.3 ターゲットユーザー

就活・インターン準備中の学生（特にAIを活用して開発する学生）

---

## 2. システム全体像

```
┌─────────────────────────────────────────────────────────┐
│  AI開発環境 (Claude Code, Cursor, etc.)                  │
│                                                          │
│  ┌──────────────────┐                                    │
│  │ MEX MCP Server   │ ← 開発過程をリアルタイムに捕捉      │
│  │ (TypeScript)      │                                    │
│  └────────┬─────────┘                                    │
└───────────┼─────────────────────────────────────────────┘
            │ POST /api/devlogs/{project_id}/entries
            │ (Bearer token認証)
            ▼
┌─────────────────────────────────────────────────────────┐
│  MEX Backend (FastAPI)                                   │
│                                                          │
│  /api/auth/*          認証 (JWT)                         │
│  /api/projects/*      プロジェクトCRUD                    │
│  /api/devlogs/*       開発ログ記録 ← MCP連携             │
│  /api/quiz/*          理解度チェック生成・回答             │
│  /api/portfolio/*     公開ポートフォリオ取得               │
│  /api/dashboard/*     概要統計                            │
│                                                          │
│  ┌────────────┐ ┌──────────┐ ┌────────┐ ┌────────────┐  │
│  │ Embedding  │ │ LLM      │ │ Qdrant │ │ PostgreSQL │  │
│  │ Service    │ │ Service  │ │        │ │            │  │
│  └────────────┘ └──────────┘ └────────┘ └────────────┘  │
└─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────┐
│  MEX Frontend (React 19 + TypeScript + React Router 7)   │
│                                                          │
│  /auth              ログイン・登録                        │
│  /dashboard         ポートフォリオ概要（本人用）           │
│  /projects/new      プロジェクト新規作成                   │
│  /projects/:id      プロジェクト詳細・開発ログ             │
│  /projects/:id/quiz 理解度チェック                        │
│  /p/:username       公開ポートフォリオ（企業閲覧用）       │
│  /p/:username/:id   公開プロジェクト詳細                   │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 既存コード → 新機能マッピング

### 3.1 そのまま再利用するコード

| コンポーネント | ファイルパス | 説明 |
|--------------|------------|------|
| JWT認証 | `backend/app/auth/jwt.py`, `dependencies.py`, `models.py` | ログイン・登録・トークン検証。変更不要 |
| Embedding生成 | `backend/app/domain/embedding/embedding_service.py` | OpenAI text-embedding-3-large。開発ログのベクトル化に再利用 |
| LLMサービス | `backend/app/domain/llm/llm_service.py` | GPT-4呼び出し。クイズ問題生成に再利用 |
| 類似検索 | `backend/app/domain/similarity/similarity_engine.py` | Qdrantベクトル検索。類似プロジェクト検索に再利用 |
| Qdrantクライアント | `backend/app/infrastructure/vectordb/qdrant_client.py` | ベクトルDB操作。変更不要 |
| DBセッション | `backend/app/infrastructure/database/session.py` | `SessionLocal`, `get_db()`。変更不要 |
| APIクライアント | `frontend/src/api/client.ts` | `apiGet`, `apiPost`, `apiPut`, `apiDelete`, トークン管理。変更不要 |
| AuthContext | `frontend/src/contexts/AuthContext.tsx` | 認証状態管理。変更不要 |
| 共通コンポーネント | `frontend/src/components/common/` | `Navigation.tsx`, `PageHeader.tsx`, `EmptyState.tsx`, `LoadingSkeleton.tsx`, `AppLoadingScreen.tsx`。ラベル変更のみ |
| デザインシステム | `frontend/src/design-tokens.css`, `frontend/src/global.css` | CSS変数、リセット、共通スタイル。変更不要 |

### 3.2 改修して再利用するコード

| 現在のファイル | 現在の役割 | 新しい役割 | 変更内容 |
|--------------|----------|----------|---------|
| `backend/app/infrastructure/database/models.py` | `User`, `DecisionCase`, `IdeaMemo`等 | `User`(拡張), `Project`, `DevLogEntry`, `QuizQuestion`, `QuizAttempt`, `SkillScore` | セクション4で詳述 |
| `backend/app/application/idea_sparring_service.py` | アイデア壁打ちオーケストレーション | **QuizService** — 開発ログからクイズ生成 | `spar_idea()` → `generate_quiz()` に改修。`CaseManager`呼び出しを`DevLogEntry`からのコンテキスト取得に変更 |
| `backend/app/application/retrospective_service.py` | 振り返り記録 | **DevLogService** — 開発ログ管理 | `submit_retrospective()` → `create_entry()` に改修。`CaseManager`への保存を`DevLogEntry`テーブルへの保存に変更 |
| `backend/app/application/usage_service.py` | 利用量統計 | **DashboardService** — ポートフォリオ統計 | 統計クエリをProject/DevLogEntry/SkillScore基準に変更 |
| `backend/app/domain/question/question_generator.py` | 自由回答の問い生成 | **4択クイズ生成** | プロンプトを4択クイズ形式に変更。`GeneratedQuestion`に`options[]`と`correct_answer`を追加 |
| `backend/app/api/__init__.py` | auth, idea_sparring, retrospectives, dashboard, billing | auth, projects, devlogs, quiz, portfolio, dashboard | ルーター登録を差し替え |
| `backend/app/api/idea_sparring.py` | 壁打ちAPI | **quiz.py** — クイズAPI | エンドポイントパスとリクエスト/レスポンスを変更 |
| `backend/app/api/retrospectives.py` | 振り返りAPI | **devlogs.py** — 開発ログAPI | エンドポイントパスとリクエスト/レスポンスを変更 |
| `backend/app/api/dashboard.py` | 利用量ダッシュボード | ポートフォリオ概要 | レスポンス構造を変更 |
| `frontend/src/App.tsx` | 3ルート構成 | 新ルート構成 | セクション7で詳述 |
| `frontend/src/types/index.ts` | 壁打ち/振り返り型 | プロジェクト/開発ログ/クイズ型 | セクション8で詳述 |
| `frontend/src/components/Dashboard/DashboardPage.tsx` | 利用統計 | ポートフォリオ概要 | プロジェクト一覧・スキルマップ表示に変更 |
| `frontend/src/components/IdeaSparring/IdeaSparringPage.tsx` | 壁打ちフォーム+結果 | **理解度チェック画面** | 4択クイズUI・スコア表示に変更 |
| `frontend/src/components/Retrospective/RetrospectivePage.tsx` | 振り返りフォーム | **開発ログ閲覧・手動追記画面** | タイムライン表示+手動追記フォームに変更 |
| `frontend/src/components/Landing/LandingPage.tsx` | 企業向けコピー | 学生向けコピー | テキスト全面書き換え |

### 3.3 削除するコード（デッドコード）

| ファイル | 理由 |
|---------|------|
| `backend/app/api/draft_reviews.py` | ルーター未登録。新コンセプトに不要 |
| `backend/app/api/gate_reviews.py` | ルーター未登録。新コンセプトに不要 |
| `backend/app/api/postmortems.py` | retrospectivesに統合済み。新コンセプトに不要 |
| `backend/app/application/draft_review_service.py` | 上記APIのサービス層。不要 |
| `backend/app/application/gate_review_service.py` | 上記APIのサービス層。不要 |

---

## 4. データモデル設計

既存の `backend/app/infrastructure/database/models.py` を改修する。
既存のユーティリティ `generate_uuid()`, `utc_now()`, `Base` クラスはそのまま使用。

### 4.1 User テーブル（既存を拡張）

```python
class User(Base):
    __tablename__ = "users"

    # --- 既存カラム（変更なし） ---
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=True)
    auth_provider = Column(String(20), nullable=False, default="email")
    plan = Column(String(20), nullable=False, default="free")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # --- 新規カラム ---
    username = Column(String(50), nullable=True, unique=True)  # 公開ポートフォリオURL用 (/p/:username)
    bio = Column(Text, nullable=True)                          # 自己紹介文
    github_url = Column(String(500), nullable=True)            # GitHubプロフィールURL

    # --- Relationships（変更） ---
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    # 旧 cases, idea_memos は削除

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
    )
```

### 4.2 Project テーブル（DecisionCase を置換）

```python
class Project(Base):
    """
    プロジェクトテーブル
    ユーザーが開発したプロジェクトを管理する
    """
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)               # プロジェクト名
    description = Column(Text, nullable=True)                  # プロジェクト概要
    technologies = Column(JSON, default=list)                  # 使用技術タグ ["React", "FastAPI", "OpenAI"]
    repository_url = Column(String(500), nullable=True)        # GitHubリポジトリURL
    demo_url = Column(String(500), nullable=True)              # デモURL
    status = Column(String(20), nullable=False, default="in_progress")  # in_progress | completed | archived
    is_public = Column(Boolean, nullable=False, default=False) # ポートフォリオに公開するか
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User", back_populates="projects")
    devlog_entries = relationship("DevLogEntry", back_populates="project", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="project", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_projects_user_id", "user_id"),
        Index("idx_projects_status", "status"),
        Index("idx_projects_is_public", "is_public"),
    )
```

### 4.3 DevLogEntry テーブル（新規）

```python
class DevLogEntry(Base):
    """
    開発ログエントリ
    MCPサーバーまたは手動入力から記録される開発過程の1ステップ
    """
    __tablename__ = "devlog_entries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    source = Column(String(20), nullable=False, default="manual")
    # 'mcp' = MCPサーバーからの自動記録
    # 'manual' = ユーザーがWebから手動入力

    entry_type = Column(String(30), nullable=False)
    # 'code_generation' = AIにコードを生成させた
    # 'debug' = バグ修正・デバッグ
    # 'design_decision' = 設計判断
    # 'learning' = 技術の学び・気づき
    # 'error_resolution' = エラー解決

    summary = Column(String(500), nullable=False)              # 要約（例: "React RouterでSPA遷移を実装"）
    detail = Column(Text, nullable=True)                       # 詳細（コード差分、AIへのプロンプト等）
    technologies = Column(JSON, default=list)                  # この作業で使った技術 ["React Router", "TypeScript"]
    ai_tool = Column(String(50), nullable=True)                # 使用AIツール: 'claude_code' | 'cursor' | 'copilot' | etc.
    created_at = Column(DateTime(timezone=True), default=utc_now)
    metadata = Column(JSON, default=dict)                      # MCPからの追加データ

    # Relationships
    project = relationship("Project", back_populates="devlog_entries")
    quiz_questions = relationship("QuizQuestion", back_populates="devlog_entry")

    __table_args__ = (
        Index("idx_devlog_entries_project_id", "project_id"),
        Index("idx_devlog_entries_user_id", "user_id"),
        Index("idx_devlog_entries_created_at", "created_at"),
        Index("idx_devlog_entries_entry_type", "entry_type"),
    )
```

### 4.4 QuizQuestion テーブル（新規）

```python
class QuizQuestion(Base):
    """
    理解度チェック問題
    開発ログからLLMが自動生成する4択クイズ
    """
    __tablename__ = "quiz_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    devlog_entry_id = Column(String(36), ForeignKey("devlog_entries.id", ondelete="SET NULL"), nullable=True)
    # nullableなのは、プロジェクト全体から生成されるケースもあるため

    technology = Column(String(100), nullable=False)           # 対象技術（例: "React Router"）
    question = Column(Text, nullable=False)                    # 問題文
    options = Column(JSON, nullable=False)                     # 4択 ["選択肢A", "選択肢B", "選択肢C", "選択肢D"]
    correct_answer = Column(Integer, nullable=False)           # 正解インデックス (0-3)
    explanation = Column(Text, nullable=False)                 # 解説
    difficulty = Column(String(10), nullable=False, default="medium")  # easy | medium | hard
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    project = relationship("Project", back_populates="quiz_questions")
    devlog_entry = relationship("DevLogEntry", back_populates="quiz_questions")
    attempts = relationship("QuizAttempt", back_populates="question", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_quiz_questions_project_id", "project_id"),
        Index("idx_quiz_questions_user_id", "user_id"),
        Index("idx_quiz_questions_technology", "technology"),
    )
```

### 4.5 QuizAttempt テーブル（新規）

```python
class QuizAttempt(Base):
    """
    クイズ回答記録
    ユーザーの各回答を記録し、スコア計算に使用
    """
    __tablename__ = "quiz_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    quiz_question_id = Column(String(36), ForeignKey("quiz_questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    selected_answer = Column(Integer, nullable=False)          # ユーザーが選んだインデックス (0-3)
    is_correct = Column(Boolean, nullable=False)               # 正誤
    time_spent_seconds = Column(Integer, nullable=True)        # 回答にかかった秒数
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    question = relationship("QuizQuestion", back_populates="attempts")

    __table_args__ = (
        Index("idx_quiz_attempts_user_id", "user_id"),
        Index("idx_quiz_attempts_question_id", "quiz_question_id"),
    )
```

### 4.6 SkillScore テーブル（新規）

```python
class SkillScore(Base):
    """
    技術別理解度スコア
    クイズ結果から集計される技術別のスコア
    """
    __tablename__ = "skill_scores"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    technology = Column(String(100), nullable=False)           # 技術名（例: "React", "FastAPI"）
    score = Column(Float, nullable=False, default=0.0)         # 0.0〜100.0 の理解度スコア
    total_questions = Column(Integer, nullable=False, default=0)
    correct_answers = Column(Integer, nullable=False, default=0)
    last_assessed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    __table_args__ = (
        Index("idx_skill_scores_user_id", "user_id"),
        Index("idx_skill_scores_technology", "technology"),
        # ユーザー×技術でユニーク
        Index("uq_skill_scores_user_tech", "user_id", "technology", unique=True),
    )
```

### 4.7 削除するテーブル

以下のモデルクラスとリレーションシップを削除する:
- `DecisionCase` — `Project` に置換
- `FailurePatternTag` — 不要（クイズベースに移行）
- `CaseFailurePattern` — 不要
- `IdeaMemo` — 不要（`DevLogEntry` に統合）

`UsageLog` と `Subscription` は維持する（課金管理に必要）。

### 4.8 マイグレーション戦略

Alembicマイグレーションで段階的に移行する:
1. 新テーブル（`projects`, `devlog_entries`, `quiz_questions`, `quiz_attempts`, `skill_scores`）を作成
2. `users` テーブルに `username`, `bio`, `github_url` カラムを追加
3. 旧テーブル（`decision_cases`, `failure_pattern_tags`, `case_failure_patterns`, `idea_memos`）を削除

```bash
cd backend
alembic revision --autogenerate -m "pivot_to_portfolio_schema"
alembic upgrade head
```

---

## 5. バックエンドAPI仕様

### 5.1 認証 API（既存維持）

パス: `backend/app/api/auth.py`。変更なし。

| メソッド | パス | 説明 |
|---------|------|------|
| POST | `/api/auth/register` | ユーザー登録 |
| POST | `/api/auth/login` | ログイン |
| GET | `/api/auth/me` | 現在のユーザー情報取得 |

### 5.2 プロジェクトAPI（新規: `backend/app/api/projects.py`）

| メソッド | パス | 認証 | 説明 |
|---------|------|------|------|
| GET | `/api/projects` | 要 | 自分のプロジェクト一覧 |
| POST | `/api/projects` | 要 | プロジェクト新規作成 |
| GET | `/api/projects/{project_id}` | 要 | プロジェクト詳細 |
| PUT | `/api/projects/{project_id}` | 要 | プロジェクト更新 |
| DELETE | `/api/projects/{project_id}` | 要 | プロジェクト削除 |

#### POST `/api/projects` リクエスト
```json
{
  "title": "面接練習AIアプリ",
  "description": "ChatGPT APIを使った模擬面接アプリ",
  "technologies": ["React", "TypeScript", "OpenAI API", "FastAPI"],
  "repository_url": "https://github.com/user/interview-ai",
  "demo_url": "https://interview-ai.vercel.app",
  "status": "in_progress"
}
```

#### POST `/api/projects` レスポンス
```json
{
  "id": "proj-xxxx-xxxx",
  "title": "面接練習AIアプリ",
  "description": "ChatGPT APIを使った模擬面接アプリ",
  "technologies": ["React", "TypeScript", "OpenAI API", "FastAPI"],
  "repository_url": "https://github.com/user/interview-ai",
  "demo_url": "https://interview-ai.vercel.app",
  "status": "in_progress",
  "is_public": false,
  "created_at": "2026-02-07T10:00:00Z",
  "updated_at": "2026-02-07T10:00:00Z",
  "devlog_count": 0,
  "quiz_score": null
}
```

#### GET `/api/projects` レスポンス
```json
{
  "projects": [
    {
      "id": "proj-xxxx-xxxx",
      "title": "面接練習AIアプリ",
      "technologies": ["React", "TypeScript", "OpenAI API"],
      "status": "in_progress",
      "is_public": false,
      "devlog_count": 12,
      "quiz_score": 78.5,
      "created_at": "2026-02-07T10:00:00Z",
      "updated_at": "2026-02-08T15:30:00Z"
    }
  ]
}
```

### 5.3 開発ログAPI（新規: `backend/app/api/devlogs.py`）

| メソッド | パス | 認証 | 説明 |
|---------|------|------|------|
| GET | `/api/devlogs/{project_id}` | 要 | プロジェクトの開発ログ一覧 |
| POST | `/api/devlogs/{project_id}/entries` | 要 | 開発ログ追加（MCP・手動共通） |
| PUT | `/api/devlogs/entries/{entry_id}` | 要 | 開発ログ編集 |
| DELETE | `/api/devlogs/entries/{entry_id}` | 要 | 開発ログ削除 |

#### POST `/api/devlogs/{project_id}/entries` リクエスト
```json
{
  "source": "mcp",
  "entry_type": "code_generation",
  "summary": "React RouterでSPA遷移を実装した",
  "detail": "BrowserRouter, Routes, Route を使用してページ遷移を構築。useNavigate hookで動的遷移も実装した。",
  "technologies": ["React Router", "React", "TypeScript"],
  "ai_tool": "claude_code",
  "metadata": {
    "prompt_summary": "SPAのルーティングを実装して",
    "files_changed": ["src/App.tsx", "src/pages/Home.tsx"]
  }
}
```

#### POST `/api/devlogs/{project_id}/entries` レスポンス
```json
{
  "id": "entry-xxxx-xxxx",
  "project_id": "proj-xxxx-xxxx",
  "source": "mcp",
  "entry_type": "code_generation",
  "summary": "React RouterでSPA遷移を実装した",
  "detail": "...",
  "technologies": ["React Router", "React", "TypeScript"],
  "ai_tool": "claude_code",
  "created_at": "2026-02-07T11:30:00Z",
  "metadata": { ... }
}
```

#### GET `/api/devlogs/{project_id}` レスポンス
```json
{
  "entries": [
    {
      "id": "entry-xxxx-xxxx",
      "source": "mcp",
      "entry_type": "code_generation",
      "summary": "React RouterでSPA遷移を実装した",
      "technologies": ["React Router", "React"],
      "ai_tool": "claude_code",
      "created_at": "2026-02-07T11:30:00Z"
    },
    {
      "id": "entry-yyyy-yyyy",
      "source": "manual",
      "entry_type": "learning",
      "summary": "useEffectのクリーンアップ関数の重要性を理解した",
      "technologies": ["React"],
      "ai_tool": null,
      "created_at": "2026-02-07T14:00:00Z"
    }
  ],
  "total": 2
}
```

### 5.4 理解度チェックAPI（`backend/app/api/quiz.py` — 既存`idea_sparring.py`を改修）

| メソッド | パス | 認証 | 説明 |
|---------|------|------|------|
| POST | `/api/quiz/{project_id}/generate` | 要 | 開発ログからクイズ生成 |
| GET | `/api/quiz/{project_id}` | 要 | プロジェクトのクイズ一覧 |
| POST | `/api/quiz/{question_id}/answer` | 要 | クイズに回答 |
| GET | `/api/quiz/scores` | 要 | 技術別スコア一覧 |

#### POST `/api/quiz/{project_id}/generate` リクエスト
```json
{
  "count": 5,
  "difficulty": "medium",
  "technologies": ["React Router", "TypeScript"]
}
```
`technologies` が未指定の場合、プロジェクトの全開発ログから使用技術を自動収集する。

#### POST `/api/quiz/{project_id}/generate` レスポンス
```json
{
  "questions": [
    {
      "id": "q-xxxx",
      "technology": "React Router",
      "question": "React Routerの<Routes>コンポーネントの役割として正しいものはどれですか？",
      "options": [
        "URLパスに基づいて表示するコンポーネントを切り替える",
        "HTTPリクエストをサーバーに送信する",
        "ブラウザの戻るボタンを無効化する",
        "CSSのルーティングルールを定義する"
      ],
      "difficulty": "easy",
      "devlog_entry_id": "entry-xxxx-xxxx"
    }
  ],
  "total_generated": 5
}
```
**注意**: `correct_answer`と`explanation`はレスポンスに含めない（回答前に正解を見せないため）。

#### POST `/api/quiz/{question_id}/answer` リクエスト
```json
{
  "selected_answer": 0,
  "time_spent_seconds": 12
}
```

#### POST `/api/quiz/{question_id}/answer` レスポンス
```json
{
  "is_correct": true,
  "correct_answer": 0,
  "explanation": "React Routerの<Routes>は現在のURLパスに基づいて、マッチする<Route>の子コンポーネントをレンダリングします。",
  "score_update": {
    "technology": "React Router",
    "previous_score": 72.0,
    "new_score": 78.5,
    "total_questions": 10,
    "correct_answers": 8
  }
}
```

#### GET `/api/quiz/scores` レスポンス
```json
{
  "scores": [
    {
      "technology": "React",
      "score": 85.0,
      "total_questions": 20,
      "correct_answers": 17,
      "last_assessed_at": "2026-02-08T10:00:00Z"
    },
    {
      "technology": "TypeScript",
      "score": 70.0,
      "total_questions": 10,
      "correct_answers": 7,
      "last_assessed_at": "2026-02-07T15:00:00Z"
    }
  ]
}
```

### 5.5 ダッシュボードAPI（`backend/app/api/dashboard.py` を改修）

| メソッド | パス | 認証 | 説明 |
|---------|------|------|------|
| GET | `/api/dashboard` | 要 | ポートフォリオ概要統計 |

#### GET `/api/dashboard` レスポンス
```json
{
  "user": {
    "display_name": "田中太郎",
    "username": "tanaka-taro",
    "bio": "情報系学部3年。Webアプリ開発に興味あり。",
    "github_url": "https://github.com/tanaka-taro"
  },
  "stats": {
    "total_projects": 5,
    "total_devlog_entries": 48,
    "total_quiz_answered": 35,
    "overall_score": 76.5
  },
  "recent_projects": [
    {
      "id": "proj-xxxx",
      "title": "面接練習AIアプリ",
      "technologies": ["React", "OpenAI API"],
      "status": "completed",
      "devlog_count": 12,
      "quiz_score": 78.5,
      "updated_at": "2026-02-08T15:30:00Z"
    }
  ],
  "top_skills": [
    { "technology": "React", "score": 85.0 },
    { "technology": "TypeScript", "score": 70.0 },
    { "technology": "FastAPI", "score": 65.0 }
  ]
}
```

### 5.6 公開ポートフォリオAPI（新規: `backend/app/api/portfolio.py`）

**認証不要** — 企業の採用担当者が閲覧する公開エンドポイント。

| メソッド | パス | 認証 | 説明 |
|---------|------|------|------|
| GET | `/api/portfolio/{username}` | 不要 | 公開プロフィール + プロジェクト一覧 |
| GET | `/api/portfolio/{username}/{project_id}` | 不要 | 公開プロジェクト詳細 + 開発ログ + クイズスコア |

#### GET `/api/portfolio/{username}` レスポンス
```json
{
  "user": {
    "display_name": "田中太郎",
    "bio": "情報系学部3年。Webアプリ開発に興味あり。",
    "github_url": "https://github.com/tanaka-taro"
  },
  "projects": [
    {
      "id": "proj-xxxx",
      "title": "面接練習AIアプリ",
      "description": "ChatGPT APIを使った模擬面接アプリ",
      "technologies": ["React", "TypeScript", "OpenAI API"],
      "repository_url": "https://github.com/user/interview-ai",
      "demo_url": "https://interview-ai.vercel.app",
      "status": "completed",
      "devlog_count": 12,
      "quiz_score": 78.5
    }
  ],
  "skills": [
    { "technology": "React", "score": 85.0 },
    { "technology": "TypeScript", "score": 70.0 }
  ]
}
```
`is_public = True` のプロジェクトのみ返す。

#### GET `/api/portfolio/{username}/{project_id}` レスポンス
```json
{
  "project": {
    "id": "proj-xxxx",
    "title": "面接練習AIアプリ",
    "description": "ChatGPT APIを使った模擬面接アプリ",
    "technologies": ["React", "TypeScript", "OpenAI API"],
    "repository_url": "https://github.com/user/interview-ai",
    "demo_url": "https://interview-ai.vercel.app",
    "status": "completed"
  },
  "devlog": [
    {
      "entry_type": "code_generation",
      "summary": "React RouterでSPA遷移を実装した",
      "technologies": ["React Router"],
      "created_at": "2026-02-07T11:30:00Z"
    }
  ],
  "quiz_summary": {
    "total_questions": 15,
    "correct_answers": 12,
    "score": 80.0,
    "by_technology": [
      { "technology": "React", "score": 90.0, "questions": 5, "correct": 5 },
      { "technology": "TypeScript", "score": 70.0, "questions": 10, "correct": 7 }
    ]
  }
}
```
公開ページでは `detail`（コード差分等）は表示しない。`summary` のみ。

---

## 6. MCPサーバー設計

### 6.1 概要

Claude Code等のAI開発ツールにMCPサーバーとして接続し、開発過程を自動的にMEX Appに記録する。

### 6.2 ディレクトリ構成

```
mex_app/
├── mcp-server/                    # 新規ディレクトリ
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts               # MCPサーバーエントリポイント
│   │   ├── tools/
│   │   │   ├── record-activity.ts  # record_dev_activity ツール
│   │   │   ├── list-projects.ts    # list_projects ツール
│   │   │   └── get-context.ts      # get_project_context ツール
│   │   ├── api-client.ts           # MEX Backend APIクライアント
│   │   └── config.ts               # 設定読み込み
│   └── README.md
```

### 6.3 技術スタック

- **言語**: TypeScript
- **MCP SDK**: `@modelcontextprotocol/sdk`
- **HTTP**: `fetch` (Node.js 18+ built-in)
- **トランスポート**: stdio（Claude Code等のローカルAIツールと接続）

### 6.4 MCPツール定義

#### `record_dev_activity`

AI開発過程の1ステップを記録する。AIコーディングツールがコード生成・修正のたびに呼び出す。

```typescript
{
  name: "record_dev_activity",
  description: "開発過程をMEX Appに記録します。コード生成、バグ修正、設計判断などの作業内容を保存します。",
  inputSchema: {
    type: "object",
    properties: {
      project_id: {
        type: "string",
        description: "記録先のプロジェクトID"
      },
      entry_type: {
        type: "string",
        enum: ["code_generation", "debug", "design_decision", "learning", "error_resolution"],
        description: "作業の種類"
      },
      summary: {
        type: "string",
        description: "作業内容の要約（日本語、1〜2文）"
      },
      detail: {
        type: "string",
        description: "詳細情報（変更したコード、使用したプロンプト等）"
      },
      technologies: {
        type: "array",
        items: { type: "string" },
        description: "この作業で使用した技術名"
      }
    },
    required: ["project_id", "entry_type", "summary", "technologies"]
  }
}
```

実装: `POST /api/devlogs/{project_id}/entries` を呼び出す。`source` は `"mcp"` を自動付与、`ai_tool` は設定ファイルから取得。

#### `list_projects`

ユーザーのプロジェクト一覧を取得する。`project_id` を確認するために使用。

```typescript
{
  name: "list_projects",
  description: "MEX Appに登録されているプロジェクトの一覧を取得します。",
  inputSchema: {
    type: "object",
    properties: {},
    required: []
  }
}
```

実装: `GET /api/projects` を呼び出す。

#### `get_project_context`

プロジェクトの概要と最近の開発ログを取得する。AIがコンテキストを理解するために使用。

```typescript
{
  name: "get_project_context",
  description: "プロジェクトの概要と最近の開発ログを取得します。",
  inputSchema: {
    type: "object",
    properties: {
      project_id: {
        type: "string",
        description: "プロジェクトID"
      }
    },
    required: ["project_id"]
  }
}
```

実装: `GET /api/projects/{project_id}` + `GET /api/devlogs/{project_id}?limit=10` を呼び出して結合。

### 6.5 認証方式

1. ユーザーがWebアプリからAPIキー（長期JWT: 有効期限365日）を発行
2. `~/.mex/config.json` にAPIキーとサーバーURLを保存:
```json
{
  "api_url": "http://localhost:8000/api",
  "api_key": "eyJhbGciOiJIUzI1NiIs...",
  "ai_tool": "claude_code"
}
```
3. MCPサーバーが各リクエストの `Authorization: Bearer <api_key>` ヘッダーに付与

### 6.6 Claude Code連携設定

ユーザーの `.claude/mcp_servers.json` に追加:

```json
{
  "mex": {
    "command": "npx",
    "args": ["mex-mcp-server"]
  }
}
```

CLAUDE.md に記録タイミングの指示を追加:
```markdown
## MCPサーバー連携
- コードを生成・修正した後、`record_dev_activity` ツールを呼んで記録する
- 設計判断をした場合は `entry_type: "design_decision"` で記録する
- エラーを解決した場合は `entry_type: "error_resolution"` で記録する
```

---

## 7. フロントエンド設計

### 7.1 ルート構成（`frontend/src/App.tsx` を改修）

```tsx
<Routes>
  {/* 公開ルート */}
  <Route path="/" element={<PublicRoute><LandingPage /></PublicRoute>} />
  <Route path="/auth" element={<PublicRoute><AuthPage /></PublicRoute>} />

  {/* 公開ポートフォリオ（認証不要） */}
  <Route path="/p/:username" element={<PublicPortfolioPage />} />
  <Route path="/p/:username/:projectId" element={<PublicProjectDetailPage />} />

  {/* 認証必須ルート */}
  <Route path="/dashboard" element={
    <ProtectedRoute><AuthenticatedLayout><DashboardPage /></AuthenticatedLayout></ProtectedRoute>
  } />
  <Route path="/projects/new" element={
    <ProtectedRoute><AuthenticatedLayout><ProjectFormPage /></AuthenticatedLayout></ProtectedRoute>
  } />
  <Route path="/projects/:id" element={
    <ProtectedRoute><AuthenticatedLayout><ProjectDetailPage /></AuthenticatedLayout></ProtectedRoute>
  } />
  <Route path="/projects/:id/quiz" element={
    <ProtectedRoute><AuthenticatedLayout><QuizPage /></AuthenticatedLayout></ProtectedRoute>
  } />

  <Route path="*" element={<Navigate to="/" replace />} />
</Routes>
```

### 7.2 ナビゲーション変更（`frontend/src/components/common/Navigation.tsx`）

```typescript
const pages = [
  { path: '/dashboard', label: 'ダッシュボード', icon: LuLayoutDashboard },
  { path: '/projects/new', label: '新規プロジェクト', icon: LuPlus },
];
```

### 7.3 コンポーネントマッピング

| 新コンポーネント | ベースとなる既存コンポーネント | 変更概要 |
|----------------|---------------------------|---------|
| `DashboardPage` | `components/Dashboard/DashboardPage.tsx` | プロジェクトカード一覧、スキルスコア表示、統計 |
| `ProjectFormPage` | `components/Retrospective/RetrospectivePage.tsx` | プロジェクト作成/編集フォーム |
| `ProjectDetailPage` | 新規（レイアウトは既存ページを参考） | プロジェクト情報 + 開発ログタイムライン + 手動追記 + クイズへのリンク |
| `QuizPage` | `components/IdeaSparring/IdeaSparringPage.tsx` | 4択クイズUI、スコア表示、既存のProgressTrackerを転用 |
| `PublicPortfolioPage` | 新規 | 公開プロフィール + プロジェクトカード + スキルスコア |
| `PublicProjectDetailPage` | 新規 | 公開プロジェクト詳細 + 開発ログ（要約のみ） + クイズスコア |

### 7.4 フロントエンド型定義（`frontend/src/types/index.ts` を全面改修）

```typescript
// ユーザー（usernameを追加）
export interface User {
  id: string;
  email: string;
  display_name: string;
  plan: 'free' | 'pro';
  username: string | null;
  bio: string | null;
  github_url: string | null;
}

// 認証レスポンス（変更なし）
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// プロジェクト
export interface Project {
  id: string;
  title: string;
  description: string | null;
  technologies: string[];
  repository_url: string | null;
  demo_url: string | null;
  status: 'in_progress' | 'completed' | 'archived';
  is_public: boolean;
  devlog_count: number;
  quiz_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreateRequest {
  title: string;
  description?: string;
  technologies?: string[];
  repository_url?: string;
  demo_url?: string;
  status?: string;
}

// 開発ログ
export interface DevLogEntry {
  id: string;
  project_id: string;
  source: 'mcp' | 'manual';
  entry_type: 'code_generation' | 'debug' | 'design_decision' | 'learning' | 'error_resolution';
  summary: string;
  detail: string | null;
  technologies: string[];
  ai_tool: string | null;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface DevLogCreateRequest {
  source?: 'manual';
  entry_type: string;
  summary: string;
  detail?: string;
  technologies: string[];
}

// クイズ
export interface QuizQuestion {
  id: string;
  technology: string;
  question: string;
  options: string[];  // 4択
  difficulty: 'easy' | 'medium' | 'hard';
  devlog_entry_id: string | null;
}

export interface QuizAnswerRequest {
  selected_answer: number;  // 0-3
  time_spent_seconds?: number;
}

export interface QuizAnswerResponse {
  is_correct: boolean;
  correct_answer: number;
  explanation: string;
  score_update: {
    technology: string;
    previous_score: number;
    new_score: number;
    total_questions: number;
    correct_answers: number;
  };
}

export interface SkillScore {
  technology: string;
  score: number;
  total_questions: number;
  correct_answers: number;
  last_assessed_at: string | null;
}

// ダッシュボード
export interface DashboardData {
  user: {
    display_name: string;
    username: string | null;
    bio: string | null;
    github_url: string | null;
  };
  stats: {
    total_projects: number;
    total_devlog_entries: number;
    total_quiz_answered: number;
    overall_score: number;
  };
  recent_projects: Project[];
  top_skills: SkillScore[];
}

// 公開ポートフォリオ
export interface PublicPortfolio {
  user: {
    display_name: string;
    bio: string | null;
    github_url: string | null;
  };
  projects: Project[];
  skills: SkillScore[];
}

export interface PublicProjectDetail {
  project: Project;
  devlog: Pick<DevLogEntry, 'entry_type' | 'summary' | 'technologies' | 'created_at'>[];
  quiz_summary: {
    total_questions: number;
    correct_answers: number;
    score: number;
    by_technology: {
      technology: string;
      score: number;
      questions: number;
      correct: number;
    }[];
  };
}
```

### 7.5 APIクライアント関数（`frontend/src/api/` を改修）

既存の `frontend/src/api/client.ts` の `apiGet`, `apiPost`, `apiPut`, `apiDelete` はそのまま使用。

**新規/改修ファイル:**

`frontend/src/api/projects.ts`:
```typescript
import { apiGet, apiPost, apiPut, apiDelete } from './client';
import { Project, ProjectCreateRequest } from '../types';

export const getProjects = () => apiGet<{ projects: Project[] }>('/projects');
export const getProject = (id: string) => apiGet<Project>(`/projects/${id}`);
export const createProject = (data: ProjectCreateRequest) => apiPost<Project, ProjectCreateRequest>('/projects', data);
export const updateProject = (id: string, data: Partial<ProjectCreateRequest>) => apiPut<Project, Partial<ProjectCreateRequest>>(`/projects/${id}`, data);
export const deleteProject = (id: string) => apiDelete<void>(`/projects/${id}`);
```

`frontend/src/api/devlogs.ts`:
```typescript
import { apiGet, apiPost, apiPut, apiDelete } from './client';
import { DevLogEntry, DevLogCreateRequest } from '../types';

export const getDevLogs = (projectId: string) => apiGet<{ entries: DevLogEntry[]; total: number }>(`/devlogs/${projectId}`);
export const createDevLog = (projectId: string, data: DevLogCreateRequest) => apiPost<DevLogEntry, DevLogCreateRequest>(`/devlogs/${projectId}/entries`, data);
export const updateDevLog = (entryId: string, data: Partial<DevLogCreateRequest>) => apiPut<DevLogEntry, Partial<DevLogCreateRequest>>(`/devlogs/entries/${entryId}`, data);
export const deleteDevLog = (entryId: string) => apiDelete<void>(`/devlogs/entries/${entryId}`);
```

`frontend/src/api/quiz.ts`:
```typescript
import { apiGet, apiPost } from './client';
import { QuizQuestion, QuizAnswerRequest, QuizAnswerResponse, SkillScore } from '../types';

export const generateQuiz = (projectId: string, data: { count?: number; difficulty?: string; technologies?: string[] }) =>
  apiPost<{ questions: QuizQuestion[]; total_generated: number }, typeof data>(`/quiz/${projectId}/generate`, data);
export const getQuizQuestions = (projectId: string) => apiGet<{ questions: QuizQuestion[] }>(`/quiz/${projectId}`);
export const answerQuiz = (questionId: string, data: QuizAnswerRequest) =>
  apiPost<QuizAnswerResponse, QuizAnswerRequest>(`/quiz/${questionId}/answer`, data);
export const getSkillScores = () => apiGet<{ scores: SkillScore[] }>('/quiz/scores');
```

`frontend/src/api/portfolio.ts`:
```typescript
import { apiGet } from './client';
import { PublicPortfolio, PublicProjectDetail } from '../types';

export const getPublicPortfolio = (username: string) => apiGet<PublicPortfolio>(`/portfolio/${username}`);
export const getPublicProjectDetail = (username: string, projectId: string) =>
  apiGet<PublicProjectDetail>(`/portfolio/${username}/${projectId}`);
```

`frontend/src/api/dashboard.ts`（既存を改修）:
```typescript
import { apiGet } from './client';
import { DashboardData } from '../types';

export const getDashboard = () => apiGet<DashboardData>('/dashboard');
```

---

## 8. クイズ生成のLLMプロンプト設計

既存の `backend/app/domain/question/question_generator.py` の `_build_prompt()` を改修する。

### 8.1 新プロンプト

```python
def _build_quiz_prompt(self, devlog_entries: list[dict], technologies: list[str], count: int, difficulty: str) -> str:
    entries_text = "\n".join(
        f"- [{e['entry_type']}] {e['summary']} (技術: {', '.join(e['technologies'])})"
        for e in devlog_entries
    )

    return f"""
あなたは技術面接官です。以下の開発ログに基づいて、開発者が使用した技術を
本当に理解しているかを確認するための4択クイズを生成してください。

## 開発ログ
{entries_text}

## 対象技術
{', '.join(technologies)}

## 要求
- {count}問の4択クイズを生成
- 難易度: {difficulty}
- 各問題は開発ログの内容に関連すること
- 「なんとなくAIに作らせた」だけでは答えられない、技術の本質的な理解を問う問題にすること
- 正解は1つのみ

以下のJSON形式で回答してください：
{{
    "questions": [
        {{
            "technology": "React Router",
            "question": "React Routerの<Routes>コンポーネントの役割として正しいものはどれですか？",
            "options": [
                "URLパスに基づいて表示するコンポーネントを切り替える",
                "HTTPリクエストをサーバーに送信する",
                "ブラウザの戻るボタンを無効化する",
                "CSSのルーティングルールを定義する"
            ],
            "correct_answer": 0,
            "explanation": "React Routerの<Routes>は現在のURLパスに基づいて、マッチする<Route>の子コンポーネントをレンダリングします。",
            "difficulty": "easy"
        }}
    ]
}}
"""
```

---

## 9. ランディングページのコピー方針

`frontend/src/components/Landing/LandingPage.tsx` を全面書き換え。

### 9.1 ヒーローセクション

- **タイトル**: 「AIで作ったものを、自分の学びに変えよう」
- **サブタイトル**: 「開発過程を自動記録し、理解度を証明する新しいポートフォリオ」
- **CTA**: 「無料で始める」→ `/auth`

### 9.2 特徴セクション（3カード）

1. **開発過程の自動記録** — MCPサーバーでAI開発の過程を自動キャプチャ。手入力の手間なし。
2. **技術ドキュメント自動生成** — コミットからNotionにWHY・HOWの解説+Q&A付きドキュメントを自動生成。使った技術を深く理解できる。
3. **自分の言葉で残すポートフォリオ** — ドキュメントで学んだことを自分の言葉で記録。面接官が「本当に理解しているか」を判別できる。

### 9.3 プライシング

Free プランのみ強調（学生向けのため無料を前面に）。Pro プランは「Coming Soon」表記。

---

## 10. 実装フェーズ順序

各フェーズは独立してデプロイ可能。

### フェーズ1: 基盤改修（DBモデル + デッドコード削除）

**対象ファイル:**
- `backend/app/infrastructure/database/models.py` — 新モデル定義
- `backend/app/api/draft_reviews.py` — 削除
- `backend/app/api/gate_reviews.py` — 削除
- `backend/app/api/postmortems.py` — 削除
- `backend/app/application/draft_review_service.py` — 削除
- `backend/app/application/gate_review_service.py` — 削除
- Alembicマイグレーション作成・実行

**完了条件:** `alembic upgrade head` が成功し、新テーブルが作成される

### フェーズ2: プロジェクト管理API + 開発ログAPI

**対象ファイル:**
- `backend/app/api/projects.py` — 新規
- `backend/app/api/devlogs.py` — 新規（`retrospectives.py` ベース）
- `backend/app/application/project_service.py` — 新規
- `backend/app/application/devlog_service.py` — 新規（`retrospective_service.py` ベース）
- `backend/app/api/__init__.py` — ルーター登録変更

**完了条件:** curl/httpie でプロジェクトCRUDと開発ログ追加ができる

### フェーズ3: フロントエンド改修（ダッシュボード + プロジェクト画面）

**対象ファイル:**
- `frontend/src/App.tsx` — ルート変更
- `frontend/src/types/index.ts` — 型定義全面改修
- `frontend/src/api/projects.ts`, `devlogs.ts`, `dashboard.ts` — 新規/改修
- `frontend/src/components/Dashboard/DashboardPage.tsx` — ポートフォリオ概要に改修
- `frontend/src/components/Retrospective/RetrospectivePage.tsx` → `ProjectDetailPage.tsx` に改修
- `frontend/src/components/common/Navigation.tsx` — ラベル変更
- `frontend/src/components/Landing/LandingPage.tsx` — コピー全面書き換え

**完了条件:** ブラウザでプロジェクト作成・開発ログ手動追記・ダッシュボード表示ができる

### フェーズ4: 理解度チェック

**対象ファイル:**
- `backend/app/api/quiz.py` — 新規（`idea_sparring.py` ベース）
- `backend/app/application/quiz_service.py` — 新規（`idea_sparring_service.py` ベース）
- `backend/app/domain/question/question_generator.py` — プロンプト改修
- `frontend/src/api/quiz.ts` — 新規
- `frontend/src/components/IdeaSparring/` → `frontend/src/components/Quiz/QuizPage.tsx` に改修

**完了条件:** プロジェクトの開発ログからクイズが生成され、回答してスコアが計算される

### フェーズ5: MCPサーバー

**対象ファイル:**
- `mcp-server/` — 全て新規

**完了条件:** Claude Codeから `record_dev_activity` ツールで開発ログがMEX Appに記録される

### フェーズ6: 公開ポートフォリオ

**対象ファイル:**
- `backend/app/api/portfolio.py` — 新規
- `frontend/src/api/portfolio.ts` — 新規
- `frontend/src/components/Portfolio/PublicPortfolioPage.tsx` — 新規
- `frontend/src/components/Portfolio/PublicProjectDetailPage.tsx` — 新規

**完了条件:** `/p/:username` でプロジェクト一覧とスキルスコアが閲覧できる

---

## 11. 注意事項

### セキュリティ

- 公開ポートフォリオAPI (`/api/portfolio/*`) は認証不要だが、`is_public = true` のプロジェクトのみ返すこと
- 開発ログの `detail` フィールドには機密コードが含まれる可能性があるため、公開ポートフォリオでは `summary` のみ返す
- MCPサーバー用の長期トークンは専用のスコープ（`devlog:write`, `project:read`）を持たせ、アカウント操作はできないようにする

### パフォーマンス

- 開発ログはMCPから頻繁に書き込まれるため、`POST /api/devlogs/{project_id}/entries` はレスポンスを軽量にする
- クイズ生成はLLM呼び出しを伴うため、非同期処理またはタイムアウト（60秒）を設定する
- 公開ポートフォリオは閲覧頻度が高い可能性があるため、キャッシュを検討する

### 既存データのマイグレーション

- 現状の `decision_cases` / `idea_memos` にデータがある場合、マイグレーション時に `projects` + `devlog_entries` に変換するスクリプトを用意する
- データがない（開発環境）場合は、単純にテーブルを削除して再作成する
