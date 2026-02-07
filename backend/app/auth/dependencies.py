"""
認証依存関係
個人開発版: tenant_idを削除し、planを追加
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from .jwt import JWTService, TokenExpiredError, InvalidTokenError


class AuthenticationError(Exception):
    """認証エラー"""
    pass


class CurrentUser(BaseModel):
    """現在のユーザー情報 - tenant_id削除、plan追加"""
    user_id: str
    plan: str = "free"


# JWTサービスのシングルトン
_jwt_service = JWTService()

# HTTPBearerスキーム
security = HTTPBearer(auto_error=False)


def get_current_user(authorization: str) -> CurrentUser:
    """
    認可ヘッダーからユーザー情報を取得

    Args:
        authorization: Authorization headerの値

    Returns:
        CurrentUser: ユーザー情報

    Raises:
        AuthenticationError: 認証失敗
    """
    if not authorization.startswith("Bearer "):
        raise AuthenticationError("Invalid authorization header format")

    token = authorization[7:]  # "Bearer " を除去

    try:
        payload = _jwt_service.decode_token(token)
        return CurrentUser(
            user_id=payload.get("sub", ""),
            plan=payload.get("plan", "free"),
        )
    except (TokenExpiredError, InvalidTokenError) as e:
        raise AuthenticationError(str(e))


async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> CurrentUser:
    """
    FastAPI依存関係としてのユーザー取得

    Returns:
        CurrentUser: ユーザー情報

    Raises:
        HTTPException: 認証失敗時
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return get_current_user(f"Bearer {credentials.credentials}")
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


# オプショナル認証（認証なしでもアクセス可能）
async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> CurrentUser | None:
    """
    オプショナル認証

    Returns:
        CurrentUser | None: ユーザー情報（認証なしの場合はNone）
    """
    if credentials is None:
        return None

    try:
        return get_current_user(f"Bearer {credentials.credentials}")
    except AuthenticationError:
        return None
