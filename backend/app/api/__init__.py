"""API Layer - RESTful APIエンドポイント"""
from fastapi import APIRouter

from .draft_reviews import router as draft_reviews_router
from .gate_reviews import router as gate_reviews_router
from .postmortems import router as postmortems_router

router = APIRouter(prefix="/api")

# サブルーターを登録
router.include_router(draft_reviews_router)
router.include_router(gate_reviews_router)
router.include_router(postmortems_router)

# Health check endpoint
@router.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}
