"""
アプリケーション設定
環境変数からの設定読み込み
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# プロジェクトルートの .env を確実に参照するため、絶対パスで指定
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
    )

    # Application
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/mex_app"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # OpenAI
    openai_api_key: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # JWT
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    return Settings()
