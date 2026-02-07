"""
TDD: ゲートレビューAPIエンドポイントのテスト
タスク4.2: ゲートレビューAPIエンドポイントの実装
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestGateReviewEndpoints:
    """ゲートレビューAPIエンドポイントのテスト"""

    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)

    def test_generate_agenda_endpoint_exists(self, client):
        """POST /api/gate-reviews/agenda エンドポイントが存在する"""
        response = client.post(
            "/api/gate-reviews/agenda",
            json={
                "project_id": "proj-001",
                "current_phase": "validation",
                "hypothesis_status": [],
            },
        )
        assert response.status_code in [200, 422, 500]

    def test_search_decision_reasons_endpoint_exists(self, client):
        """GET /api/gate-reviews/decision-reasons エンドポイントが存在する"""
        response = client.get(
            "/api/gate-reviews/decision-reasons",
            params={"query": "収益性"},
        )
        assert response.status_code in [200, 500]

    def test_generate_agenda_requires_project_id(self, client):
        """project_idは必須"""
        response = client.post(
            "/api/gate-reviews/agenda",
            json={
                "current_phase": "validation",
            },
        )
        assert response.status_code == 422

    def test_generate_agenda_requires_current_phase(self, client):
        """current_phaseは必須"""
        response = client.post(
            "/api/gate-reviews/agenda",
            json={
                "project_id": "proj-001",
            },
        )
        assert response.status_code == 422

    def test_decision_reasons_requires_query(self, client):
        """queryは必須"""
        response = client.get("/api/gate-reviews/decision-reasons")
        assert response.status_code == 422
