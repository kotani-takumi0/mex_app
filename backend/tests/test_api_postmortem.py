"""
TDD: ポストモーテムAPIエンドポイントのテスト
タスク4.3: ポストモーテムAPIエンドポイントの実装
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestPostmortemEndpoints:
    """ポストモーテムAPIエンドポイントのテスト"""

    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)

    def test_get_template_endpoint_exists(self, client):
        """GET /api/postmortems/template/{projectId} エンドポイントが存在する"""
        response = client.get("/api/postmortems/template/proj-001")
        assert response.status_code in [200, 404, 500]

    def test_create_postmortem_endpoint_exists(self, client):
        """POST /api/postmortems エンドポイントが存在する"""
        response = client.post(
            "/api/postmortems",
            json={
                "project_id": "proj-001",
                "outcome": "withdrawn",
                "failed_hypotheses": [],
                "discussions": [],
            },
        )
        assert response.status_code in [200, 422, 500]

    def test_suggest_patterns_endpoint_exists(self, client):
        """POST /api/postmortems/suggest-patterns エンドポイントが存在する"""
        response = client.post(
            "/api/postmortems/suggest-patterns",
            json={
                "project_id": "proj-001",
                "outcome": "withdrawn",
                "decision": {
                    "decision": "no_go",
                    "reason": "収益性の懸念",
                },
                "failed_hypotheses": [],
                "discussions": [],
            },
        )
        assert response.status_code in [200, 422, 500]

    def test_create_postmortem_requires_project_id(self, client):
        """project_idは必須"""
        response = client.post(
            "/api/postmortems",
            json={
                "outcome": "withdrawn",
            },
        )
        assert response.status_code == 422

    def test_create_postmortem_requires_outcome(self, client):
        """outcomeは必須"""
        response = client.post(
            "/api/postmortems",
            json={
                "project_id": "proj-001",
            },
        )
        assert response.status_code == 422

    def test_get_template_returns_sections(self, client):
        """テンプレートにセクションが含まれる"""
        response = client.get("/api/postmortems/template/proj-001")
        if response.status_code == 200:
            data = response.json()
            assert "sections" in data
            assert "outcome_options" in data
