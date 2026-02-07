"""
JWT認証サービス
個人開発版: tenant_idを削除し、planを追加
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pydantic import BaseModel


class TokenExpiredError(Exception):
    """トークン有効期限切れエラー"""
    pass


class InvalidTokenError(Exception):
    """無効なトークンエラー"""
    pass


class JWTConfig(BaseModel):
    """JWT設定"""
    secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


class TokenPayload(BaseModel):
    """トークンペイロード - tenant_id削除、plan追加"""
    sub: str  # ユーザーID
    plan: str = "free"  # ユーザープラン（free/pro）
    exp: datetime | None = None


class JWTService:
    """JWTサービス"""

    def __init__(self, config: JWTConfig | None = None):
        self.config = config or JWTConfig()

    def create_access_token(
        self,
        data: dict[str, Any],
        expires_delta: timedelta | None = None,
    ) -> str:
        """
        アクセストークンを生成

        Args:
            data: ペイロードデータ（sub, plan等）
            expires_delta: 有効期限

        Returns:
            JWTトークン文字列
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.config.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            self.config.secret_key,
            algorithm=self.config.algorithm,
        )

        return encoded_jwt

    def decode_token(self, token: str) -> dict[str, Any]:
        """
        トークンをデコード

        Returns:
            デコードされたペイロード

        Raises:
            TokenExpiredError: トークン有効期限切れ
            InvalidTokenError: 無効なトークン
        """
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")
