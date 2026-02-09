"""
アプリケーション設定
環境変数からの設定読み込み
"""
from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# プロジェクトルートの .env を確実に参照するため、絶対パスで指定
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        enable_decoding=False,
    )

    # Application
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/mex_app"

    # Qdrant - ローカル（host/port）またはCloud（url/api_key）のいずれかを使用
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_url: str | None = None  # Qdrant Cloud URL (例: https://xxx.qdrant.io:6333)
    qdrant_api_key: str | None = None  # Qdrant Cloud APIキー

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

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_pro_price_id: str = ""

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
