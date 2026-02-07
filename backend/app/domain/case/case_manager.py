"""
意思決定ケースマネージャー
タスク2.3: 意思決定ケースマネージャーの実装

Design.mdに基づく仕様:
- 意思決定ケースのCRUD操作
- PostgreSQLへのメタデータ保存とQdrantへのベクトル保存の連携
- 類似ケース検索のファサード
- 失敗パターンタグの管理
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from qdrant_client.http import models as qdrant_models

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import (
    DecisionCase as DBDecisionCase,
    FailurePatternTag as DBFailurePatternTag,
    CaseFailurePattern as DBCaseFailurePattern,
)
from app.infrastructure.vectordb.qdrant_client import QdrantClientWrapper, COLLECTION_NAME
from app.domain.embedding.embedding_service import EmbeddingService
from app.domain.similarity.similarity_engine import SimilarityEngine, HybridSearchInput, CaseFilter


class CaseOutcome(Enum):
    """ケースの結果"""
    ADOPTED = "adopted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    CANCELLED = "cancelled"


@dataclass
class GoNoGoDecision:
    """Go/NoGo判断"""
    decision: str  # "go" or "no_go"
    reason: str  # 1-3文


@dataclass
class FailurePatternTag:
    """失敗パターンタグ"""
    id: str
    name: str
    description: str | None
    category: str  # financial, operational, market, technical, organizational


@dataclass
class CaseCreateInput:
    """ケース作成入力"""
    title: str
    purpose: str
    outcome: CaseOutcome
    decision: GoNoGoDecision
    target_market: str | None = None
    business_model: str | None = None
    failed_hypotheses: list[dict[str, Any]] = field(default_factory=list)
    discussions: list[dict[str, Any]] = field(default_factory=list)
    user_id: str = ""


@dataclass
class DecisionCase:
    """意思決定ケース"""
    id: str
    title: str
    purpose: str
    target_market: str | None
    business_model: str | None
    outcome: CaseOutcome
    decision: GoNoGoDecision
    failed_hypotheses: list[dict[str, Any]]
    discussions: list[dict[str, Any]]
    failure_patterns: list[FailurePatternTag]
    created_at: datetime
    updated_at: datetime


@dataclass
class SimilarCase:
    """類似ケース"""
    case_id: str
    title: str
    purpose: str
    outcome: CaseOutcome
    score: float
    matched_segments: list[str]


class CaseManager:
    """
    意思決定ケースマネージャー

    ケースのライフサイクル管理と類似検索のファサードを提供
    """

    def __init__(
        self,
        qdrant_client: QdrantClientWrapper | None = None,
        embedding_service: EmbeddingService | None = None,
        similarity_engine: SimilarityEngine | None = None,
    ):
        """
        初期化

        Args:
            qdrant_client: Qdrantクライアント
            embedding_service: 埋め込みサービス
            similarity_engine: 類似検索エンジン
        """
        self._qdrant = qdrant_client or QdrantClientWrapper()
        self._embedding = embedding_service or EmbeddingService()
        self._similarity = similarity_engine or SimilarityEngine()

    async def create_case(self, input_data: CaseCreateInput) -> DecisionCase:
        """
        ケースを作成

        PostgreSQLにメタデータを保存し、Qdrantにベクトルを保存
        """
        db = SessionLocal()

        try:
            case_id = str(uuid.uuid4())

            db_case = DBDecisionCase(
                id=case_id,
                user_id=input_data.user_id,
                title=input_data.title,
                purpose=input_data.purpose,
                target_market=input_data.target_market,
                business_model=input_data.business_model,
                outcome=input_data.outcome.value,
                decision_type=input_data.decision.decision,
                decision_reason=input_data.decision.reason,
                failed_hypotheses=input_data.failed_hypotheses,
                discussions=input_data.discussions,
            )
            db.add(db_case)
            db.commit()
            db.refresh(db_case)

            # 埋め込みを生成
            text_for_embedding = f"{input_data.title} {input_data.purpose}"
            if input_data.target_market:
                text_for_embedding += f" {input_data.target_market}"
            if input_data.business_model:
                text_for_embedding += f" {input_data.business_model}"

            embedding_result = await self._embedding.embed_text(text_for_embedding)

            # Qdrantに保存（user_idをペイロードに含める）
            self._qdrant.client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    qdrant_models.PointStruct(
                        id=case_id,
                        vector=embedding_result.embedding,
                        payload={
                            "case_id": case_id,
                            "user_id": input_data.user_id,
                            "outcome": input_data.outcome.value,
                            "failure_patterns": [],
                        },
                    )
                ],
            )

            return self._db_to_domain(db_case)

        finally:
            db.close()

    async def get_case_by_id(self, case_id: str) -> DecisionCase | None:
        """
        IDでケースを取得

        Args:
            case_id: ケースID

        Returns:
            DecisionCase | None: 見つかったケース、またはNone
        """
        db = SessionLocal()

        try:
            db_case = db.query(DBDecisionCase).filter(DBDecisionCase.id == case_id).first()

            if db_case is None:
                return None

            return self._db_to_domain(db_case)

        finally:
            db.close()

    async def find_similar_cases(
        self,
        query_text: str,
        limit: int = 10,
        filters: CaseFilter | None = None,
        user_id: str = "",
    ) -> list[SimilarCase]:
        """
        類似ケースを検索（user_idでデータ分離）

        Args:
            query_text: 検索クエリ
            limit: 取得件数
            filters: フィルター条件
            user_id: ユーザーID（データ分離用）
        """
        # ハイブリッド検索を実行
        input_data = HybridSearchInput(
            query_text=query_text,
            limit=limit,
            filters=filters,
            user_id=user_id,
        )
        search_results = await self._similarity.hybrid_search(input_data)

        # ケース詳細を取得して返す
        similar_cases = []
        for result in search_results:
            case = await self.get_case_by_id(result.case_id)
            if case:
                similar_cases.append(
                    SimilarCase(
                        case_id=case.id,
                        title=case.title,
                        purpose=case.purpose,
                        outcome=case.outcome,
                        score=result.score,
                        matched_segments=result.matched_segments,
                    )
                )

        return similar_cases

    async def add_failure_pattern_tag(
        self,
        case_id: str,
        tag: FailurePatternTag,
    ) -> None:
        """
        ケースに失敗パターンタグを追加

        Args:
            case_id: ケースID
            tag: 追加するタグ
        """
        db = SessionLocal()

        try:
            # ケースの存在確認
            db_case = db.query(DBDecisionCase).filter(DBDecisionCase.id == case_id).first()
            if db_case is None:
                raise ValueError(f"Case not found: {case_id}")

            # タグの存在確認
            db_tag = db.query(DBFailurePatternTag).filter(DBFailurePatternTag.id == tag.id).first()
            if db_tag is None:
                # タグが存在しない場合は作成
                db_tag = DBFailurePatternTag(
                    id=tag.id,
                    name=tag.name,
                    description=tag.description,
                    category=tag.category,
                )
                db.add(db_tag)
                db.commit()

            # 関連を作成
            association = DBCaseFailurePattern(case_id=case_id, tag_id=tag.id)
            db.add(association)
            db.commit()

            # Qdrantのペイロードを更新
            current_patterns = []
            try:
                points = self._qdrant.client.retrieve(
                    collection_name=COLLECTION_NAME,
                    ids=[case_id],
                )
                if points:
                    current_patterns = points[0].payload.get("failure_patterns", [])
            except Exception:
                pass

            if tag.category not in current_patterns:
                current_patterns.append(tag.category)
                self._qdrant.client.set_payload(
                    collection_name=COLLECTION_NAME,
                    payload={"failure_patterns": current_patterns},
                    points=[case_id],
                )

        finally:
            db.close()

    def _db_to_domain(self, db_case: DBDecisionCase) -> DecisionCase:
        """DBモデルをドメインモデルに変換"""
        failure_patterns = []
        for assoc in db_case.failure_patterns:
            tag = assoc.tag
            failure_patterns.append(
                FailurePatternTag(
                    id=tag.id,
                    name=tag.name,
                    description=tag.description,
                    category=tag.category,
                )
            )

        return DecisionCase(
            id=db_case.id,
            title=db_case.title,
            purpose=db_case.purpose,
            target_market=db_case.target_market,
            business_model=db_case.business_model,
            outcome=CaseOutcome(db_case.outcome),
            decision=GoNoGoDecision(
                decision=db_case.decision_type,
                reason=db_case.decision_reason,
            ),
            failed_hypotheses=db_case.failed_hypotheses or [],
            discussions=db_case.discussions or [],
            failure_patterns=failure_patterns,
            created_at=db_case.created_at,
            updated_at=db_case.updated_at,
        )
