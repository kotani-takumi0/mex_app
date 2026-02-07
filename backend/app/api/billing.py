"""
決済APIエンドポイント
Stripe Checkout Session / Customer Portal / Webhook
"""
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from app.auth.dependencies import CurrentUser, get_current_user_dependency
from app.application.billing_service import BillingService
from app.config import get_settings

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
async def stripe_webhook(request: Request):
    """Stripe Webhook処理"""
    settings = get_settings()
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    service = get_service()

    if event["type"] == "checkout.session.completed":
        await service.handle_checkout_completed(event["data"]["object"])
    elif event["type"] in (
        "customer.subscription.updated",
        "customer.subscription.deleted",
    ):
        await service.handle_subscription_updated(event["data"]["object"])

    return {"status": "ok"}
