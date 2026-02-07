"""
TDD: JWT認証のテスト
タスク6.1: フロントエンド・バックエンド統合
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch


class TestJWTConfig:
    """JWT設定のテスト"""

    def test_jwt_config_has_secret_key(self):
        """JWT設定にシークレットキーが含まれる"""
        from app.auth.jwt import JWTConfig

        config = JWTConfig()
        assert hasattr(config, "secret_key")
        assert config.secret_key is not None

    def test_jwt_config_has_algorithm(self):
        """JWT設定にアルゴリズムが含まれる"""
        from app.auth.jwt import JWTConfig

        config = JWTConfig()
        assert config.algorithm == "HS256"

    def test_jwt_config_has_expiration(self):
        """JWT設定に有効期限が含まれる"""
        from app.auth.jwt import JWTConfig

        config = JWTConfig()
        assert hasattr(config, "access_token_expire_minutes")
        assert config.access_token_expire_minutes > 0


class TestJWTService:
    """JWTサービスのテスト"""

    def test_create_access_token(self):
        """アクセストークンを生成できる"""
        from app.auth.jwt import JWTService

        service = JWTService()
        token = service.create_access_token(
            data={"sub": "user123", "tenant_id": "tenant001"}
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """有効なトークンをデコードできる"""
        from app.auth.jwt import JWTService

        service = JWTService()
        token = service.create_access_token(
            data={"sub": "user123", "tenant_id": "tenant001"}
        )
        payload = service.decode_token(token)
        assert payload["sub"] == "user123"
        assert payload["tenant_id"] == "tenant001"

    def test_decode_expired_token_raises_error(self):
        """期限切れトークンはエラーを発生させる"""
        from app.auth.jwt import JWTService, TokenExpiredError

        service = JWTService()
        # 過去の時間で有効期限が切れたトークンを作成
        token = service.create_access_token(
            data={"sub": "user123"},
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(TokenExpiredError):
            service.decode_token(token)

    def test_decode_invalid_token_raises_error(self):
        """無効なトークンはエラーを発生させる"""
        from app.auth.jwt import JWTService, InvalidTokenError

        service = JWTService()
        with pytest.raises(InvalidTokenError):
            service.decode_token("invalid.token.here")


class TestTokenPayload:
    """トークンペイロードのテスト"""

    def test_token_payload_has_user_id(self):
        """ペイロードにユーザーIDが含まれる"""
        from app.auth.jwt import TokenPayload

        payload = TokenPayload(sub="user123", tenant_id="tenant001")
        assert payload.sub == "user123"

    def test_token_payload_has_tenant_id(self):
        """ペイロードにテナントIDが含まれる"""
        from app.auth.jwt import TokenPayload

        payload = TokenPayload(sub="user123", tenant_id="tenant001")
        assert payload.tenant_id == "tenant001"


class TestAuthDependency:
    """認証依存関係のテスト"""

    def test_get_current_user_from_valid_token(self):
        """有効なトークンからユーザーを取得できる"""
        from app.auth.dependencies import get_current_user
        from app.auth.jwt import JWTService

        service = JWTService()
        token = service.create_access_token(
            data={"sub": "user123", "tenant_id": "tenant001"}
        )
        # Authorization headerのフォーマットでテスト
        user = get_current_user(f"Bearer {token}")
        assert user.user_id == "user123"
        assert user.tenant_id == "tenant001"

    def test_get_current_user_without_bearer_raises_error(self):
        """Bearerプレフィックスがない場合エラー"""
        from app.auth.dependencies import get_current_user, AuthenticationError

        with pytest.raises(AuthenticationError):
            get_current_user("invalid_token")

    def test_get_current_user_with_invalid_token_raises_error(self):
        """無効なトークンでエラー"""
        from app.auth.dependencies import get_current_user, AuthenticationError

        with pytest.raises(AuthenticationError):
            get_current_user("Bearer invalid.token.here")
