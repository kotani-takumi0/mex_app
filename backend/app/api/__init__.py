"""API Layer - RESTful APIエンドポイント（個人開発版）"""
from fastapi import APIRouter

from .auth import router as auth_router
from .idea_sparring import router as idea_sparring_router
from .retrospectives import router as retrospectives_router
from .dashboard import router as dashboard_router
from .billing import router as billing_router

router = APIRouter(prefix="/api")

# サブルーターを登録
router.include_router(auth_router)
router.include_router(idea_sparring_router)
router.include_router(retrospectives_router)
router.include_router(dashboard_router)
router.include_router(billing_router)


# Health check endpoint
@router.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}
