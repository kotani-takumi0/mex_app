"""
認証APIエンドポイント
メール/パスワードによるユーザー登録・ログイン
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext

from app.auth.jwt import JWTService
from app.auth.dependencies import CurrentUser, get_current_user_dependency
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

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

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
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
