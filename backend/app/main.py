"""
FastAPIアプリケーションのエントリーポイント
AI開発ポートフォリオプラットフォーム
"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import router as api_router
from app.config import get_settings
from app.rate_limit import limiter

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

# レート制限
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# セキュリティヘッダーミドルウェア
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """レスポンスにセキュリティヘッダーを付与"""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if settings.app_env == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
        return response


app.add_middleware(SecurityHeadersMiddleware)

# CORS設定 - 環境変数から取得、許可するメソッド・ヘッダーを明示的に指定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# APIルーターを登録
app.include_router(api_router)


@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {"message": "MEX App API - AI開発ポートフォリオ", "version": "0.3.0"}
