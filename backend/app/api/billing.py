"""
決済APIエンドポイント
Stripe Checkout Session / Customer Portal / Webhook
"""

import logging

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.application.billing_service import BillingService
from app.auth.dependencies import CurrentUser, get_current_user_dependency
from app.config import get_settings
from app.infrastructure.database.models import StripeWebhookEvent
from app.infrastructure.database.session import get_db
from app.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])

# サービスインスタンス
_service: BillingService | None = None


def get_service() -> BillingService:
    global _service
    if _service is None:
        _service = BillingService()
    return _service


class CheckoutRequest(BaseModel):
    """Checkoutリクエスト"""

    success_url: str = Field(..., description="決済成功時のリダイレクトURL")
    cancel_url: str = Field(..., description="キャンセル時のリダイレクトURL")


class CheckoutResponse(BaseModel):
    """Checkoutレスポンス"""

    checkout_url: str


class PortalRequest(BaseModel):
    """Portalリクエスト"""

    return_url: str = Field(..., description="Portal終了後のリダイレクトURL")


class PortalResponse(BaseModel):
    """Portalレスポンス"""

    portal_url: str


class PlanInfoResponse(BaseModel):
    """プラン情報レスポンス"""

    plan: str
    project_limit: int | None
    project_count: int
    llm_model: str
    subscription_status: str | None
    current_period_end: str | None


@router.get("/plan-info", response_model=PlanInfoResponse)
async def get_plan_info(
    current_user: CurrentUser = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    """現在のプラン情報と利用状況を返す"""
    from app.auth.plan_guards import FREE_PROJECT_LIMIT
    from app.infrastructure.database.models import Project, Subscription, User

    user = db.query(User).filter(User.id == current_user.user_id).first()
    plan = user.plan if user else "free"

    project_count = db.query(Project).filter(Project.user_id == current_user.user_id).count()

    sub = db.query(Subscription).filter(Subscription.user_id == current_user.user_id).first()

    is_free = plan == "free"

    return PlanInfoResponse(
        plan=plan,
        project_limit=FREE_PROJECT_LIMIT if is_free else None,
        project_count=project_count,
        llm_model="gpt-4o-mini" if is_free else "gpt-4o",
        subscription_status=sub.status if sub else None,
        current_period_end=sub.current_period_end.isoformat()
        if sub and sub.current_period_end
        else None,
    )


@router.post("/checkout-session", response_model=CheckoutResponse)
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """Stripe Checkout Sessionを作成"""
    try:
        service = get_service()
        url = await service.create_checkout_session(
            user_id=current_user.user_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
        )
        return CheckoutResponse(checkout_url=url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/portal", response_model=PortalResponse)
async def create_portal_session(
    request: PortalRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """Stripe Customer Portalセッションを作成"""
    try:
        service = get_service()
        url = await service.create_portal_session(
            user_id=current_user.user_id,
            return_url=request.return_url,
        )
        return PortalResponse(portal_url=url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/webhook")
@limiter.limit("30/minute")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Stripe Webhook処理（冪等性保証付き）"""
    settings = get_settings()
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # --- 冪等性チェック: 同一イベントの二重処理を防止 ---
    stripe_event_id = event["id"]
    existing = (
        db.query(StripeWebhookEvent)
        .filter(StripeWebhookEvent.stripe_event_id == stripe_event_id)
        .first()
    )
    if existing:
        logger.info("Stripe webhook event already processed: %s", stripe_event_id)
        return {"status": "ok", "duplicate": True}

    service = get_service()

    if event["type"] == "checkout.session.completed":
        await service.handle_checkout_completed(event["data"]["object"])
    elif event["type"] in (
        "customer.subscription.updated",
        "customer.subscription.deleted",
    ):
        await service.handle_subscription_updated(event["data"]["object"])

    # 処理完了後にイベントを記録
    db.add(
        StripeWebhookEvent(
            stripe_event_id=stripe_event_id,
            event_type=event["type"],
        )
    )
    db.commit()

    logger.info("Stripe webhook processed: %s (%s)", stripe_event_id, event["type"])
    return {"status": "ok"}
