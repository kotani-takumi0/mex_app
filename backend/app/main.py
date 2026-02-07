"""
FastAPIアプリケーションのエントリーポイント
個人開発アイデア壁打ちアプリ
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.config import get_settings
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


settings = get_settings()

app = FastAPI(
    title="MEX App - アイデア壁打ちアプリ",
    description="過去のプロジェクト知識を活用した個人開発アイデア壁打ちアプリ",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS設定 - 環境変数から取得
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターを登録
app.include_router(api_router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "MEX App API - アイデア壁打ちアプリ", "version": "0.2.0"}
