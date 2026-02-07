"""
類似検索エンジン
タスク2.2: 類似検索エンジンの実装

Design.mdに基づく仕様:
- Qdrantへのベクトル類似検索機能
- PostgreSQLの全文検索（BM25相当）とベクトル検索のハイブリッド検索
- ベクトルスコアとテキストスコアの重み付け調整
- リランキング機能
"""
from dataclasses import dataclass, field
from typing import Any

from qdrant_client.http import models as qdrant_models

from app.infrastructure.vectordb.qdrant_client import QdrantClientWrapper, COLLECTION_NAME
from app.domain.embedding.embedding_service import EmbeddingService
from app.infrastructure.database.session import get_db


@dataclass
class SimilarityConfig:
    """類似検索設定"""
    vector_weight: float = 0.7
    text_weight: float = 0.3
    default_limit: int = 10


@dataclass
class CaseFilter:
    """ケースフィルター"""
    outcomes: list[str] | None = None
    failure_patterns: list[str] | None = None


@dataclass
class VectorSearchInput:
    """ベクトル検索入力"""
    query_embedding: list[float]
    limit: int = 10
    filters: CaseFilter | None = None


@dataclass
class HybridSearchInput:
    """ハイブリッド検索入力"""
    query_text: str
    limit: int = 10
    vector_weight: float = 0.7
    text_weight: float = 0.3
    filters: CaseFilter | None = None
    user_id: str = ""  # ユーザーデータ分離用


@dataclass
class SimilarityResult:
    """類似検索結果"""
    case_id: str
    score: float
    vector_score: float
    text_score: float
    matched_segments: list[str] = field(default_factory=list)


class SimilarityEngine:
    """
    類似検索エンジン

    ベクトル検索とテキスト検索を組み合わせたハイブリッド検索を提供
    """

    def __init__(
        self,
        config: SimilarityConfig | None = None,
        qdrant_client: QdrantClientWrapper | None = None,
        embedding_service: EmbeddingService | None = None,
    ):
        """
        初期化

        Args:
            config: 類似検索設定
            qdrant_client: Qdrantクライアント
            embedding_service: 埋め込みサービス
        """
        self.config = config or SimilarityConfig()
        self._qdrant = qdrant_client or QdrantClientWrapper()
        self._embedding = embedding_service or EmbeddingService()

    async def vector_search(
        self, input_data: VectorSearchInput, user_id: str = ""
    ) -> list[SimilarityResult]:
        """
        ベクトル類似検索（user_idでデータ分離）
        """
        # フィルター条件の構築（user_idフィルター含む）
        query_filter = self._build_qdrant_filter(input_data.filters, user_id=user_id)

        # Qdrantで検索
        response = self._qdrant.client.query_points(
            collection_name=COLLECTION_NAME,
            query=input_data.query_embedding,
            limit=input_data.limit,
            query_filter=query_filter,
        )

        # 結果の変換
        results = []
        for hit in response.points:
            case_id = hit.payload.get("case_id", str(hit.id))
            results.append(
                SimilarityResult(
                    case_id=case_id,
                    score=hit.score,
                    vector_score=hit.score,
                    text_score=0.0,
                    matched_segments=[],
                )
            )

        return results

    async def hybrid_search(self, input_data: HybridSearchInput) -> list[SimilarityResult]:
        """
        ハイブリッド検索（ベクトル + テキスト）

        Args:
            input_data: ハイブリッド検索入力

        Returns:
            list[SimilarityResult]: 類似検索結果（スコア順）
        """
        # テキストの埋め込みを生成
        embedding_result = await self._embedding.embed_text(input_data.query_text)

        # ベクトル検索（user_idでフィルター）
        vector_input = VectorSearchInput(
            query_embedding=embedding_result.embedding,
            limit=input_data.limit * 2,  # オーバーフェッチ
            filters=input_data.filters,
        )
        vector_results = await self.vector_search(vector_input, user_id=input_data.user_id)

        # テキスト検索（PostgreSQL全文検索）
        text_results = await self._text_search(
            input_data.query_text,
            input_data.limit * 2,
            input_data.filters,
        )

        # スコアの統合
        combined = self._combine_scores(
            vector_results,
            text_results,
            input_data.vector_weight,
            input_data.text_weight,
        )

        # リランキングして上位N件を返す
        reranked = self._rerank_results(combined)
        return reranked[:input_data.limit]

    async def _text_search(
        self,
        query_text: str,
        limit: int,
        filters: CaseFilter | None,
    ) -> dict[str, tuple[float, list[str]]]:
        """
        PostgreSQL全文検索

        Returns:
            dict[case_id, (score, matched_segments)]
        """
        results = {}

        try:
            # データベースセッションを取得
            db_gen = get_db()
            db = next(db_gen)

            try:
                # PostgreSQL全文検索クエリ
                # ts_rank_cd を使用してBM25相当のスコアリング
                sql = """
                    SELECT
                        id,
                        ts_rank_cd(
                            to_tsvector('simple', title || ' ' || purpose || ' ' || COALESCE(target_market, '')),
                            plainto_tsquery('simple', :query)
                        ) as rank,
                        ts_headline('simple', title || ' ' || purpose, plainto_tsquery('simple', :query)) as headline
                    FROM decision_cases
                    WHERE to_tsvector('simple', title || ' ' || purpose || ' ' || COALESCE(target_market, ''))
                          @@ plainto_tsquery('simple', :query)
                """

                # フィルター条件の追加
                if filters and filters.outcomes:
                    outcomes_str = "', '".join(filters.outcomes)
                    sql += f" AND outcome IN ('{outcomes_str}')"

                sql += " ORDER BY rank DESC LIMIT :limit"

                from sqlalchemy import text
                result = db.execute(text(sql), {"query": query_text, "limit": limit})
                rows = result.fetchall()

                for row in rows:
                    case_id, rank, headline = row
                    # スコアを0-1に正規化
                    normalized_score = min(rank, 1.0)
                    results[case_id] = (normalized_score, [headline] if headline else [])

            finally:
                try:
                    next(db_gen)
                except StopIteration:
                    pass

        except Exception:
            # データベースエラー時は空の結果を返す
            pass

        return results

    def _build_qdrant_filter(
        self, filters: CaseFilter | None, user_id: str = ""
    ) -> qdrant_models.Filter | None:
        """Qdrantフィルター条件を構築（user_idによるデータ分離含む）"""
        conditions = []

        # user_idフィルター（データ分離の要）
        if user_id:
            conditions.append(
                qdrant_models.FieldCondition(
                    key="user_id",
                    match=qdrant_models.MatchValue(value=user_id),
                )
            )

        if filters:
            if filters.outcomes:
                conditions.append(
                    qdrant_models.FieldCondition(
                        key="outcome",
                        match=qdrant_models.MatchAny(any=filters.outcomes),
                    )
                )

            if filters.failure_patterns:
                conditions.append(
                    qdrant_models.FieldCondition(
                        key="failure_patterns",
                        match=qdrant_models.MatchAny(any=filters.failure_patterns),
                    )
                )

        if not conditions:
            return None

        return qdrant_models.Filter(must=conditions)

    def _combine_scores(
        self,
        vector_results: list[SimilarityResult],
        text_results: dict[str, tuple[float, list[str]]],
        vector_weight: float,
        text_weight: float,
    ) -> list[SimilarityResult]:
        """ベクトルスコアとテキストスコアを統合"""
        # case_idでインデックス化
        combined: dict[str, SimilarityResult] = {}

        # ベクトル検索結果を追加
        for result in vector_results:
            text_score, matched = text_results.get(result.case_id, (0.0, []))
            combined_score = result.vector_score * vector_weight + text_score * text_weight

            combined[result.case_id] = SimilarityResult(
                case_id=result.case_id,
                score=combined_score,
                vector_score=result.vector_score,
                text_score=text_score,
                matched_segments=matched,
            )

        # テキスト検索のみにヒットしたケースを追加
        for case_id, (text_score, matched) in text_results.items():
            if case_id not in combined:
                combined_score = text_score * text_weight
                combined[case_id] = SimilarityResult(
                    case_id=case_id,
                    score=combined_score,
                    vector_score=0.0,
                    text_score=text_score,
                    matched_segments=matched,
                )

        return list(combined.values())

    def _rerank_results(self, results: list[SimilarityResult]) -> list[SimilarityResult]:
        """スコアによるリランキング"""
        return sorted(results, key=lambda r: r.score, reverse=True)
