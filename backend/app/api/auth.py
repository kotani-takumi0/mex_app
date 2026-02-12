"""
認証APIエンドポイント
メール/パスワードによるユーザー登録・ログイン・プロフィール編集・APIトークン発行・MCPトークン管理
"""

import hashlib
import logging
import re
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.auth.dependencies import CurrentUser, get_current_user_dependency
from app.auth.jwt import JWTService
from app.infrastructure.database.models import MCPToken, User, utc_now
from app.infrastructure.database.session import get_db
from app.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

# パスワードハッシュ
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWTサービス
_jwt_service = JWTService()


# リクエスト/レスポンススキーマ
class RegisterRequest(BaseModel):
    """ユーザー登録リクエスト"""

    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(
        ...,
        min_length=10,
        max_length=128,
        description="パスワード（10文字以上、英大文字・小文字・数字・記号を含む）",
    )
    display_name: str = Field(..., min_length=1, max_length=100, description="表示名")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("パスワードには英大文字を1文字以上含めてください")
        if not any(c.islower() for c in v):
            raise ValueError("パスワードには英小文字を1文字以上含めてください")
        if not any(c.isdigit() for c in v):
            raise ValueError("パスワードには数字を1文字以上含めてください")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+\[\]~`]', v):
            raise ValueError("パスワードには記号を1文字以上含めてください")
        return v


class LoginRequest(BaseModel):
    """ログインリクエスト"""

    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(..., description="パスワード")


class AuthResponse(BaseModel):
    """認証レスポンス"""

    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """ユーザー情報レスポンス"""

    id: str
    email: str
    display_name: str
    plan: str
    username: str | None
    bio: str | None
    github_url: str | None


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        plan=user.plan,
        username=user.username,
        bio=user.bio,
        github_url=user.github_url,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    """
    ユーザー登録

    メールアドレスとパスワードで新規ユーザーを作成し、
    JWTトークンを返却する
    """
    try:
        existing = db.query(User).filter(User.email == body.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="このメールアドレスは既に登録されています",
            )

        user = User(
            email=body.email,
            display_name=body.display_name,
            hashed_password=pwd_context.hash(body.password),
            auth_provider="email",
            plan="free",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token = _jwt_service.create_access_token(data={"sub": user.id, "plan": user.plan})

        return AuthResponse(access_token=token, user=_user_response(user))

    except OperationalError:
        logger.exception("Database error during register")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error during register")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    """
    ログイン

    メールアドレスとパスワードで認証し、JWTトークンを返却する
    """
    try:
        user = db.query(User).filter(User.email == body.email).first()

        if user is None or user.hashed_password is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが正しくありません",
            )

        if not pwd_context.verify(body.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが正しくありません",
            )

        token = _jwt_service.create_access_token(data={"sub": user.id, "plan": user.plan})

        return AuthResponse(access_token=token, user=_user_response(user))

    except OperationalError:
        logger.exception("Database error during login")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error during login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    """現在のユーザー情報を取得"""
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )
    return _user_response(user)


# --- MCP用長寿命APIトークン ---

# usernameバリデーション: 英小文字・数字・ハイフン、3〜30文字
_USERNAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-]{1,28}[a-z0-9]$")


class ApiTokenRequest(BaseModel):
    """APIトークン発行リクエスト"""

    name: str | None = Field(
        None, max_length=100, description="トークンの識別名（例: MacBook Pro）"
    )


class ApiTokenResponse(BaseModel):
    """APIトークンレスポンス"""

    api_token: str
    token_id: str
    expires_in_days: int


class MCPTokenInfo(BaseModel):
    """MCPトークン情報"""

    id: str
    name: str | None
    scope: str
    created_at: str
    revoked_at: str | None


class MCPTokenListResponse(BaseModel):
    """MCPトークン一覧レスポンス"""

    tokens: list[MCPTokenInfo]


class RevokeTokenRequest(BaseModel):
    """トークン無効化リクエスト"""

    token_id: str = Field(..., description="無効化するトークンのID")


def _hash_token(token: str) -> str:
    """トークンのSHA-256ハッシュを生成（DB保存用）"""
    return hashlib.sha256(token.encode()).hexdigest()


@router.post("/api-token", response_model=ApiTokenResponse)
async def create_api_token(
    request: ApiTokenRequest | None = None,
    current_user: CurrentUser = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    """
    MCP Server 等の外部ツール向けに長寿命APIトークン（30日間有効）を発行する。
    """
    expires_days = 30
    token = _jwt_service.create_access_token(
        data={"sub": current_user.user_id, "plan": current_user.plan},
        expires_delta=timedelta(days=expires_days),
    )

    try:
        mcp_token = MCPToken(
            user_id=current_user.user_id,
            token_hash=_hash_token(token),
            name=request.name if request else None,
        )
        db.add(mcp_token)
        db.commit()
        db.refresh(mcp_token)
        token_id = mcp_token.id
    except Exception:
        logger.exception("Failed to store MCP token record")
        db.rollback()
        # トークン自体は発行済みなので、DB記録失敗でもトークンは返す
        token_id = ""

    return ApiTokenResponse(api_token=token, token_id=token_id, expires_in_days=expires_days)


@router.get("/mcp-tokens", response_model=MCPTokenListResponse)
async def list_mcp_tokens(
    current_user: CurrentUser = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    """現在のユーザーが発行したMCPトークンの一覧を返す。"""
    tokens = (
        db.query(MCPToken)
        .filter(MCPToken.user_id == current_user.user_id)
        .order_by(MCPToken.created_at.desc())
        .all()
    )

    return MCPTokenListResponse(
        tokens=[
            MCPTokenInfo(
                id=t.id,
                name=t.name,
                scope=t.scope,
                created_at=t.created_at.isoformat() if t.created_at else "",
                revoked_at=t.revoked_at.isoformat() if t.revoked_at else None,
            )
            for t in tokens
        ]
    )


@router.post("/mcp-token/revoke", status_code=status.HTTP_200_OK)
async def revoke_mcp_token(
    request: RevokeTokenRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    """MCPトークンを無効化する。"""
    token_record = (
        db.query(MCPToken)
        .filter(
            MCPToken.id == request.token_id,
            MCPToken.user_id == current_user.user_id,
        )
        .first()
    )

    if token_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="トークンが見つかりません",
        )

    if token_record.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="このトークンは既に無効化されています",
        )

    token_record.revoked_at = utc_now()
    db.commit()

    return {"message": "トークンを無効化しました", "token_id": request.token_id}


# --- プロフィール編集 ---


class ProfileUpdateRequest(BaseModel):
    """プロフィール更新リクエスト"""

    username: str | None = Field(
        None, min_length=3, max_length=30, description="ユーザー名（公開URL用）"
    )
    display_name: str | None = Field(None, min_length=1, max_length=100, description="表示名")
    bio: str | None = Field(None, max_length=500, description="自己紹介")
    github_url: str | None = Field(None, max_length=500, description="GitHub URL")


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
    db: Session = Depends(get_db),
):
    """プロフィール情報を更新する。"""
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    if request.username is not None:
        username = request.username.lower().strip()
        if not _USERNAME_PATTERN.match(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ユーザー名は英小文字・数字・ハイフンのみ、3〜30文字で指定してください",
            )
        existing = db.query(User).filter(User.username == username, User.id != user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="このユーザー名は既に使用されています",
            )
        user.username = username

    if request.display_name is not None:
        user.display_name = request.display_name
    if request.bio is not None:
        user.bio = request.bio
    if request.github_url is not None:
        user.github_url = request.github_url

    db.commit()
    db.refresh(user)

    return _user_response(user)
