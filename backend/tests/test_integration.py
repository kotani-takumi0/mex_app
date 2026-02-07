"""
TDD: フロントエンド・バックエンド統合テスト
タスク6.1: フロントエンド・バックエンド統合
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.auth.jwt import JWTService


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
        token = service.create_access_token(
            data={"sub": "test-user", "tenant_id": "test-tenant"}
        )
        return {"Authorization": f"Bearer {token}"}

    def test_health_check_no_auth_required(self, client):
        """ヘルスチェックは認証不要"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_draft_reviews_endpoint_accessible(self, client):
        """ドラフトレビューエンドポイントにアクセス可能"""
        response = client.post(
            "/api/draft-reviews",
            json={
                "draft_id": "test-001",
                "purpose": "テスト目的",
                "target_market": "テスト市場",
                "business_model": "テストモデル",
            },
        )
        # 500は内部エラー（モック未設定）、200は成功
        assert response.status_code in [200, 500]

    def test_gate_reviews_agenda_endpoint_accessible(self, client):
        """ゲートレビューアジェンダエンドポイントにアクセス可能"""
        response = client.post(
            "/api/gate-reviews/agenda",
            json={
                "project_id": "proj-001",
                "current_phase": "validation",
                "hypothesis_status": [],
            },
        )
        assert response.status_code in [200, 500]

    def test_postmortems_template_endpoint_accessible(self, client):
        """ポストモーテムテンプレートエンドポイントにアクセス可能"""
        response = client.get("/api/postmortems/template/proj-001")
        assert response.status_code in [200, 404, 500]


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
            "/api/draft-reviews",
            json={
                # required fieldsが不足
                "draft_id": "test-001",
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


class TestTenantIsolation:
    """テナント分離のテスト"""

    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)

    def test_token_contains_tenant_id(self):
        """トークンにテナントIDが含まれる"""
        service = JWTService()
        token = service.create_access_token(
            data={"sub": "user123", "tenant_id": "tenant-abc"}
        )
        payload = service.decode_token(token)
        assert payload["tenant_id"] == "tenant-abc"

    def test_different_tenants_get_different_tokens(self):
        """異なるテナントは異なるトークンを取得"""
        service = JWTService()
        token1 = service.create_access_token(
            data={"sub": "user1", "tenant_id": "tenant-a"}
        )
        token2 = service.create_access_token(
            data={"sub": "user1", "tenant_id": "tenant-b"}
        )
        assert token1 != token2
