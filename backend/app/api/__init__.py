"""API Layer - RESTful APIエンドポイント（MEX App）"""

from fastapi import APIRouter

from .auth import router as auth_router
from .billing import router as billing_router
from .dashboard import router as dashboard_router
from .devlogs import router as devlogs_router
from .portfolio import router as portfolio_router
from .projects import router as projects_router
from .quiz import router as quiz_router

router = APIRouter(prefix="/api")

# サブルーターを登録
router.include_router(auth_router)
router.include_router(projects_router)
router.include_router(devlogs_router)
router.include_router(quiz_router)
router.include_router(portfolio_router)
router.include_router(dashboard_router)
router.include_router(billing_router)


# Health check endpoint
@router.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}
