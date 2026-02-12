"""
フロントエンド・バックエンド統合テスト
ピボット後のポートフォリオアプリ向けに更新
"""

import pytest
from fastapi.testclient import TestClient

from app.auth.jwt import JWTService
from app.main import app


class TestCORSConfiguration:
    """CORS設定のテスト"""

    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)

    def test_cors_allows_localhost_3000(self, client):
        """localhost:3000からのリクエストを許可"""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

    def test_cors_allows_credentials(self, client):
        """認証情報を許可"""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.headers.get("access-control-allow-credentials") == "true"


class TestAPIEndpointsIntegration:
    """APIエンドポイント統合テスト"""

    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)

    @pytest.fixture
    def auth_headers(self):
        """認証ヘッダー"""
        service = JWTService()
        token = service.create_access_token(data={"sub": "test-user", "plan": "free"})
        return {"Authorization": f"Bearer {token}"}

    def test_health_check_no_auth_required(self, client):
        """ヘルスチェックは認証不要"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_auth_register_endpoint_accessible(self, client):
        """認証登録エンドポイントにアクセス可能"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "display_name": "Test User",
            },
        )
        # 201（成功）、409（重複）、503（DB未起動）のいずれか
        assert response.status_code in [201, 409, 503]


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)

    def test_404_returns_json(self, client):
        """404エラーはJSONを返す"""
        response = client.get("/api/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_422_validation_error_returns_json(self, client):
        """422バリデーションエラーはJSONを返す"""
        response = client.post(
            "/api/auth/register",
            json={
                # required fieldsが不足（emailのみ）
                "email": "test@example.com",
            },
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_method_not_allowed_returns_json(self, client):
        """405エラーはJSONを返す"""
        response = client.delete("/api/health")
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data


class TestTokenIntegrity:
    """トークン整合性のテスト"""

    def test_token_contains_plan(self):
        """トークンにプランが含まれる"""
        service = JWTService()
        token = service.create_access_token(data={"sub": "user123", "plan": "pro"})
        payload = service.decode_token(token)
        assert payload["plan"] == "pro"

    def test_different_plans_get_different_tokens(self):
        """異なるプランは異なるトークンを取得"""
        service = JWTService()
        token1 = service.create_access_token(data={"sub": "user1", "plan": "free"})
        token2 = service.create_access_token(data={"sub": "user1", "plan": "pro"})
        assert token1 != token2
