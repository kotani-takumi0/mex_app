"""
FastAPIアプリケーションのエントリーポイント
AI開発ポートフォリオプラットフォーム
"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションの起動・終了時の処理"""
    logger.info("MEX App starting up")
    yield


settings = get_settings()

app = FastAPI(
    title="MEX App - AI開発ポートフォリオ",
    description="開発過程と理解度を可視化するポートフォリオプラットフォーム",
    version="0.3.0",
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
    return {"message": "MEX App API - AI開発ポートフォリオ", "version": "0.3.0"}
