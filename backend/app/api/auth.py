"""
認証APIエンドポイント
メール/パスワードによるユーザー登録・ログイン・プロフィール編集・APIトークン発行
"""
import logging
import re
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from sqlalchemy.exc import OperationalError

from app.auth.jwt import JWTService
from app.auth.dependencies import CurrentUser, get_current_user_dependency
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)

# パスワードハッシュ
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWTサービス
_jwt_service = JWTService()


# リクエスト/レスポンススキーマ
class RegisterRequest(BaseModel):
    """ユーザー登録リクエスト"""
    email: str = Field(..., description="メールアドレス")
    password: str = Field(..., min_length=8, description="パスワード（8文字以上）")
    display_name: str = Field(..., min_length=1, max_length=100, description="表示名")


class LoginRequest(BaseModel):
    """ログインリクエスト"""
    email: str = Field(..., description="メールアドレス")
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


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    ユーザー登録

    メールアドレスとパスワードで新規ユーザーを作成し、
    JWTトークンを返却する
    """
    db = SessionLocal()
    try:
        # メールアドレスの重複チェック
        existing = db.query(User).filter(User.email == request.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="このメールアドレスは既に登録されています",
            )

        # ユーザー作成
        user = User(
            email=request.email,
            display_name=request.display_name,
            hashed_password=pwd_context.hash(request.password),
            auth_provider="email",
            plan="free",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # トークン生成
        token = _jwt_service.create_access_token(
            data={"sub": user.id, "plan": user.plan}
        )

        return AuthResponse(
            access_token=token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                plan=user.plan,
                username=user.username,
                bio=user.bio,
                github_url=user.github_url,
            ),
        )

    except OperationalError as e:
        logger.exception("Database error during register")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during register")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or repr(e),
        )
    finally:
        db.close()


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    ログイン

    メールアドレスとパスワードで認証し、JWTトークンを返却する
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == request.email).first()

        if user is None or user.hashed_password is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが正しくありません",
            )

        if not pwd_context.verify(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが正しくありません",
            )

        # トークン生成
        token = _jwt_service.create_access_token(
            data={"sub": user.id, "plan": user.plan}
        )

        return AuthResponse(
            access_token=token,
            user=UserResponse(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                plan=user.plan,
                username=user.username,
                bio=user.bio,
                github_url=user.github_url,
            ),
        )

    except OperationalError as e:
        logger.exception("Database error during login")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or repr(e),
        )
    finally:
        db.close()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUser = Depends(get_current_user_dependency)):
    """
    現在のユーザー情報を取得
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == current_user.user_id).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません",
            )

        return UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            plan=user.plan,
            username=user.username,
            bio=user.bio,
            github_url=user.github_url,
        )
    finally:
        db.close()


# --- MCP用長寿命APIトークン ---

# usernameバリデーション: 英小文字・数字・ハイフン、3〜30文字
_USERNAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9\-]{1,28}[a-z0-9]$")


class ApiTokenResponse(BaseModel):
    """APIトークンレスポンス"""
    api_token: str
    expires_in_days: int


@router.post("/api-token", response_model=ApiTokenResponse)
async def create_api_token(
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """
    MCP Server 等の外部ツール向けに長寿命APIトークン（30日間有効）を発行する。
    通常のJWTは60分で切れるため、開発中にMCPからの呼び出しが途切れる問題を解消する。
    """
    expires_days = 30
    token = _jwt_service.create_access_token(
        data={"sub": current_user.user_id, "plan": current_user.plan},
        expires_delta=timedelta(days=expires_days),
    )
    return ApiTokenResponse(api_token=token, expires_in_days=expires_days)


# --- プロフィール編集 ---


class ProfileUpdateRequest(BaseModel):
    """プロフィール更新リクエスト"""
    username: str | None = Field(None, min_length=3, max_length=30, description="ユーザー名（公開URL用）")
    display_name: str | None = Field(None, min_length=1, max_length=100, description="表示名")
    bio: str | None = Field(None, max_length=500, description="自己紹介")
    github_url: str | None = Field(None, max_length=500, description="GitHub URL")


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user_dependency),
):
    """
    プロフィール情報を更新する。
    usernameは公開ポートフォリオのURLパスに使用されるため、
    英小文字・数字・ハイフンのみ許可し、一意性を検証する。
    """
    db = SessionLocal()
    try:
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
            existing = (
                db.query(User)
                .filter(User.username == username, User.id != user.id)
                .first()
            )
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

        return UserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            plan=user.plan,
            username=user.username,
            bio=user.bio,
            github_url=user.github_url,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during profile update")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or repr(e),
        )
    finally:
        db.close()
