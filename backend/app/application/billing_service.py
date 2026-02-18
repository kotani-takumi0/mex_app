"""
決済サービス
Stripe Checkout + Customer Portal パターン
"""

from typing import Any

import stripe

from app.config import get_settings
from app.infrastructure.database.models import Subscription, User
from app.infrastructure.database.session import SessionLocal


class BillingService:
    """
    決済サービス

    Stripeを使用したサブスクリプション管理。
    Checkout Sessionでの決済開始、Customer Portalでの管理、
    Webhookでのステータス更新を提供。
    """

    def __init__(self):
        settings = get_settings()
        stripe.api_key = settings.stripe_secret_key
        self._pro_price_id = settings.stripe_pro_price_id

    async def create_checkout_session(
        self,
        user_id: str,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """
        Stripe Checkout Sessionを作成

        Returns:
            Checkout SessionのURL
        """
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")

            # 既存のStripe Customerを取得または作成
            sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()

            customer_id = None
            if sub and sub.stripe_customer_id:
                customer_id = sub.stripe_customer_id

            session_params: dict[str, Any] = {
                "mode": "subscription",
                "line_items": [{"price": self._pro_price_id, "quantity": 1}],
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {"user_id": user_id},
            }

            if customer_id:
                session_params["customer"] = customer_id
            else:
                session_params["customer_email"] = user.email

            session = stripe.checkout.Session.create(**session_params)

            return session.url or ""
        finally:
            db.close()

    async def create_portal_session(self, user_id: str, return_url: str) -> str:
        """
        Stripe Customer Portalセッションを作成

        Returns:
            Portal SessionのURL
        """
        db = SessionLocal()
        try:
            sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()

            if not sub or not sub.stripe_customer_id:
                raise ValueError("No active subscription found")

            session = stripe.billing_portal.Session.create(
                customer=sub.stripe_customer_id,
                return_url=return_url,
            )

            return session.url
        finally:
            db.close()

    async def handle_checkout_completed(self, session: dict[str, Any]) -> None:
        """Checkout完了時の処理"""
        db = SessionLocal()
        try:
            user_id = session.get("metadata", {}).get("user_id")
            customer_id = session.get("customer")
            subscription_id = session.get("subscription")

            if not user_id:
                return

            # Subscriptionレコードを更新/作成
            sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()

            if sub:
                sub.stripe_customer_id = customer_id
                sub.stripe_subscription_id = subscription_id
                sub.plan = "pro"
                sub.status = "active"
            else:
                sub = Subscription(
                    user_id=user_id,
                    stripe_customer_id=customer_id,
                    stripe_subscription_id=subscription_id,
                    plan="pro",
                    status="active",
                )
                db.add(sub)

            # ユーザーのプランを更新
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.plan = "pro"

            db.commit()
        finally:
            db.close()

    async def handle_subscription_updated(self, subscription: dict[str, Any]) -> None:
        """サブスクリプション更新時の処理"""
        db = SessionLocal()
        try:
            stripe_sub_id = subscription.get("id")
            status = subscription.get("status")

            sub = (
                db.query(Subscription)
                .filter(Subscription.stripe_subscription_id == stripe_sub_id)
                .first()
            )

            if not sub:
                return

            sub.status = status

            # current_period_end を保存（フロントエンドでの次回請求日表示用）
            period_end = subscription.get("current_period_end")
            if period_end:
                from datetime import datetime, timezone

                sub.current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc)

            # キャンセル時はプランをfreeに戻す
            if status in ("canceled", "unpaid"):
                sub.plan = "free"
                user = db.query(User).filter(User.id == sub.user_id).first()
                if user:
                    user.plan = "free"

            db.commit()
        finally:
            db.close()
