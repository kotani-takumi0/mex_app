"""
TDD: プロジェクト構造のテスト
タスク1.1: 開発環境とプロジェクト構造の初期化
"""
import importlib
import os
from pathlib import Path


class TestProjectStructure:
    """プロジェクト構造が正しくセットアップされているかを検証"""

    def test_backend_directory_structure_exists(self):
        """バックエンドのレイヤードアーキテクチャに従ったディレクトリ構造"""
        backend_root = Path(__file__).parent.parent

        required_dirs = [
            "app",
            "app/api",           # API Layer
            "app/application",   # Application Layer
            "app/domain",        # Domain Layer
            "app/infrastructure", # Infrastructure Layer
            "tests",
        ]

        for dir_path in required_dirs:
            full_path = backend_root / dir_path
            assert full_path.exists(), f"ディレクトリが存在しません: {dir_path}"
            assert full_path.is_dir(), f"ディレクトリではありません: {dir_path}"

    def test_app_package_is_importable(self):
        """appパッケージがインポート可能"""
        import app
        assert app is not None

    def test_fastapi_app_exists(self):
        """FastAPIアプリケーションインスタンスが存在"""
        from app.main import app
        assert app is not None
        assert hasattr(app, "routes")

    def test_api_router_exists(self):
        """APIルーターが存在"""
        from app.api import router
        assert router is not None


class TestFastapiConfiguration:
    """FastAPI設定のテスト"""

    def test_cors_middleware_configured(self):
        """CORSミドルウェアが設定されている"""
        from app.main import app

        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    def test_api_prefix_configured(self):
        """APIプレフィックス /api が設定されている"""
        from app.main import app

        api_routes = [route.path for route in app.routes if hasattr(route, 'path')]
        # /api プレフィックスのルートが存在することを確認
        assert any(route.startswith("/api") for route in api_routes)


class TestHealthEndpoint:
    """ヘルスチェックエンドポイントのテスト"""

    def test_health_endpoint_exists(self):
        """ヘルスチェックエンドポイントが存在"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_endpoint_returns_status(self):
        """ヘルスチェックがステータスを返す"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/api/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
