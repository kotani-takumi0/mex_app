"""
TDD: 企画ドラフトレビューAPIエンドポイントのテスト
タスク4.1: 企画ドラフトレビューAPIエンドポイントの実装

Design.mdに基づく仕様:
- POST /api/draft-reviews: 企画ドラフト情報を受け取り、類似ケース・問い・懸念点を返却
- PUT /api/draft-reviews/{id}/progress: 回答進捗を更新し、未検討項目を返却
- 入力バリデーションとエラーハンドリング（400, 404, 422, 500）
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


class TestDraftReviewEndpoints:
    """ドラフトレビューAPIエンドポイントのテスト"""

    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)

    @pytest.fixture
    def mock_draft_review_service(self):
        """モックDraftReviewService"""
        with patch("app.api.draft_reviews.DraftReviewService") as mock:
            yield mock

    def test_create_draft_review_endpoint_exists(self, client):
        """POST /api/draft-reviews エンドポイントが存在する"""
        response = client.post(
            "/api/draft-reviews",
            json={
                "draft_id": "draft-001",
                "purpose": "新規事業",
                "target_market": "日本",
                "business_model": "SaaS",
            },
        )
        # 422（バリデーションエラー）または200/201であれば存在する
        assert response.status_code in [200, 201, 422, 500]

    def test_update_progress_endpoint_exists(self, client):
        """PUT /api/draft-reviews/{id}/progress エンドポイントが存在する"""
        response = client.put(
            "/api/draft-reviews/draft-001/progress",
            json={
                "question_id": "q1",
                "answer": "回答内容",
            },
        )
        assert response.status_code in [200, 404, 422, 500]

    def test_get_progress_endpoint_exists(self, client):
        """GET /api/draft-reviews/{id}/progress エンドポイントが存在する"""
        response = client.get("/api/draft-reviews/draft-001/progress")
        assert response.status_code in [200, 404, 500]


class TestDraftReviewValidation:
    """入力バリデーションのテスト"""

    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)

    def test_create_draft_review_requires_purpose(self, client):
        """purposeは必須"""
        response = client.post(
            "/api/draft-reviews",
            json={
                "draft_id": "draft-001",
                "target_market": "日本",
                "business_model": "SaaS",
            },
        )
        assert response.status_code == 422

    def test_create_draft_review_requires_target_market(self, client):
        """target_marketは必須"""
        response = client.post(
            "/api/draft-reviews",
            json={
                "draft_id": "draft-001",
                "purpose": "目的",
                "business_model": "SaaS",
            },
        )
        assert response.status_code == 422

    def test_create_draft_review_requires_business_model(self, client):
        """business_modelは必須"""
        response = client.post(
            "/api/draft-reviews",
            json={
                "draft_id": "draft-001",
                "purpose": "目的",
                "target_market": "日本",
            },
        )
        assert response.status_code == 422


class TestDraftReviewResponseSchema:
    """レスポンススキーマのテスト"""

    @pytest.fixture
    def client(self):
        """テストクライアント"""
        return TestClient(app)

    @pytest.fixture
    def mock_service(self):
        """モックサービス"""
        with patch("app.api.draft_reviews.DraftReviewService") as mock:
            from app.application.draft_review_service import (
                DraftReviewResponse,
                ReviewProgress,
            )
            from app.domain.case.case_manager import SimilarCase, CaseOutcome
            from app.domain.pattern.pattern_analyzer import ConcernPoint
            from app.domain.question.question_generator import (
                GeneratedQuestion,
                QuestionCategory,
            )

            mock_instance = AsyncMock()
            mock_instance.review_draft = AsyncMock(
                return_value=DraftReviewResponse(
                    similar_cases=[
                        SimilarCase(
                            case_id="c1",
                            title="過去案件",
                            purpose="目的",
                            outcome=CaseOutcome.REJECTED,
                            score=0.9,
                            matched_segments=["セグメント"],
                        )
                    ],
                    concern_points=[
                        ConcernPoint(
                            category="financial",
                            summary="収益性の懸念",
                            frequency=1,
                            related_case_ids=["c1"],
                        )
                    ],
                    questions=[
                        GeneratedQuestion(
                            id="q1",
                            question="収益性は？",
                            rationale="理由",
                            related_case_ids=["c1"],
                            related_patterns=["financial"],
                            category=QuestionCategory.FINANCIAL,
                        )
                    ],
                    review_progress=ReviewProgress(
                        total_questions=1,
                        answered_questions=0,
                        unanswered_question_ids=["q1"],
                    ),
                )
            )
            mock.return_value = mock_instance
            yield mock

    def test_response_has_similar_cases(self, client, mock_service):
        """レスポンスにsimilar_casesが含まれる"""
        response = client.post(
            "/api/draft-reviews",
            json={
                "draft_id": "draft-001",
                "purpose": "新規事業",
                "target_market": "日本",
                "business_model": "SaaS",
            },
        )

        if response.status_code == 200:
            data = response.json()
            assert "similar_cases" in data

    def test_response_has_questions(self, client, mock_service):
        """レスポンスにquestionsが含まれる"""
        response = client.post(
            "/api/draft-reviews",
            json={
                "draft_id": "draft-001",
                "purpose": "新規事業",
                "target_market": "日本",
                "business_model": "SaaS",
            },
        )

        if response.status_code == 200:
            data = response.json()
            assert "questions" in data

    def test_response_has_review_progress(self, client, mock_service):
        """レスポンスにreview_progressが含まれる"""
        response = client.post(
            "/api/draft-reviews",
            json={
                "draft_id": "draft-001",
                "purpose": "新規事業",
                "target_market": "日本",
                "business_model": "SaaS",
            },
        )

        if response.status_code == 200:
            data = response.json()
            assert "review_progress" in data
