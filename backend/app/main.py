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
from app.infrastructure.vectordb.qdrant_client import get_qdrant_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションの起動・終了時の処理"""
    # 起動時: Qdrantコレクションの自動初期化
    try:
        qdrant = get_qdrant_client()
        created = qdrant.ensure_collection()
        if created:
            logger.info(
                "Qdrantコレクション '%s' を作成しました",
                qdrant.config.collection_name,
            )
        else:
            logger.info(
                "Qdrantコレクション '%s' は既に存在します",
                qdrant.config.collection_name,
            )
    except Exception as exc:
        logger.warning(
            "Qdrant初期化をスキップしました: %s. "
            "Qdrant依存のAPIは失敗する可能性があります。",
            exc,
        )
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
