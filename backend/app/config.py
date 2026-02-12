"""
アプリケーション設定
環境変数からの設定読み込み
"""

import logging
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# プロジェクトルートの .env を確実に参照するため、絶対パスで指定
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        enable_decoding=False,
    )

    # Application
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/mex_app"

    # OpenAI
    openai_api_key: str = ""

    # CORS - 環境変数CORS_ORIGINSでカンマ区切り指定可能
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # JWT
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # Sentry
    sentry_dsn: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """本番環境で危険なデフォルト値が使われていないことを検証"""
        if self.app_env != "production":
            return self

        # JWT秘密鍵がデフォルトのままなら起動を拒否
        if self.jwt_secret_key == "dev-secret-key-change-in-production":
            raise ValueError(
                "CRITICAL: JWT_SECRET_KEY must be changed in production. "
                'Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))"'
            )

        # JWT秘密鍵が短すぎる場合も拒否
        if len(self.jwt_secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters in production")

        # DATABASE_URLがデフォルトのままなら警告
        if "postgres:postgres@localhost" in self.database_url:
            logger.warning(
                "DATABASE_URL uses default local credentials — "
                "ensure this is intentional in production"
            )

        return self

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return []
            if cleaned.startswith("["):
                try:
                    import json

                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except Exception:
                    pass
            return [item.strip() for item in cleaned.split(",") if item.strip()]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return [str(value).strip()]


@lru_cache
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    return Settings()
