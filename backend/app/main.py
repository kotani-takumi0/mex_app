"""
FastAPIアプリケーションのエントリーポイント
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.infrastructure.vectordb.qdrant_client import get_qdrant_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションの起動・終了時の処理"""
    # 起動時: Qdrantコレクションの自動初期化
    qdrant = get_qdrant_client()
    created = qdrant.ensure_collection()
    if created:
        print(f"Qdrantコレクション '{qdrant.config.collection_name}' を作成しました")
    else:
        print(f"Qdrantコレクション '{qdrant.config.collection_name}' は既に存在します")
    yield


app = FastAPI(
    title="MEX App - 企画立案OS",
    description="過去の意思決定ログを活用した企画支援システム",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # フロントエンド開発サーバー
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターを登録
app.include_router(api_router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "MEX App API", "version": "0.1.0"}
