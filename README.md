# MEX App - 個人開発アイデア壁打ちアプリ

過去のプロジェクト知識を活用して、新しい開発アイデアの質を上げるAI壁打ちアプリ。

## 必要環境

- Python 3.10+
- Node.js 20+
- Docker & Docker Compose
- OpenAI API キー

## セットアップ

### 1. 環境変数

```bash
cp .env.example .env
# .env を編集して OPENAI_API_KEY を設定
```

### 2. インフラ起動（PostgreSQL）

```bash
docker compose up -d
```

PostgreSQL が `localhost:5432` で起動します。

### 3. バックエンド

```bash
cd backend
pip install -e ".[dev]"
alembic upgrade head    # DBマイグレーション
```

### 4. フロントエンド

```bash
cd frontend
npm install
```

## 起動

ターミナルを2つ開いて、それぞれ実行します。

**バックエンド** (port 8000):

```bash
cd backend
uvicorn app.main:app --reload
```

**フロントエンド** (port 3000):

```bash
cd frontend
npm start
```

ブラウザで http://localhost:3000 を開きます。

## 主な機能

| 機能 | パス | 説明 |
|------|------|------|
| ダッシュボード | `/dashboard` | 利用量・最近のプロジェクト一覧 |
| アイデア壁打ち | `/sparring` | AIが類似ケース・懸念点・問いを提示 |
| 振り返り | `/retrospective` | プロジェクトの学びをナレッジとして蓄積 |

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| フロントエンド | React 19, TypeScript, React Router 7 |
| バックエンド | FastAPI, SQLAlchemy 2, Alembic |
| データベース | PostgreSQL 16 |
| ベクトルDB | Qdrant |
| AI | OpenAI API |
| 決済 | Stripe |

## 開発コマンド

```bash
# バックエンド
cd backend
pytest                          # テスト実行
ruff check app/                 # Lint
ruff check app/ --fix           # Lint自動修正

# フロントエンド
cd frontend
npm run build                   # 本番ビルド
npm test                        # テスト実行
npm run lint                    # Lint
```
