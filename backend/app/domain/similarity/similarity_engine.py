"""
類似検索エンジン（pgvector版）

PostgreSQL + pgvector を使用したベクトル類似検索。
Qdrantは廃止され、embeddingはdevlog_entriesテーブルに直接保存される。
"""
from dataclasses import dataclass, field

from sqlalchemy import text

from app.domain.embedding.embedding_service import EmbeddingService
from app.infrastructure.database.session import get_db


@dataclass
class SimilarityConfig:
    """類似検索設定"""
    vector_weight: float = 0.7
    text_weight: float = 0.3
    default_limit: int = 10


@dataclass
class DevLogFilter:
    """開発ログ検索フィルター"""
    entry_types: list[str] | None = None
    technologies: list[str] | None = None


@dataclass
class SimilarityResult:
    """類似検索結果"""
    devlog_id: str
    project_id: str
    score: float
    summary: str
    entry_type: str


class SimilarityEngine:
    """
    類似検索エンジン（pgvector版）

    PostgreSQLのpgvector拡張を使用してベクトル類似検索を実行する。
    devlog_entriesテーブルのembeddingカラムに対してコサイン距離検索を行う。
    """

    def __init__(
        self,
        config: SimilarityConfig | None = None,
        embedding_service: EmbeddingService | None = None,
    ):
        self.config = config or SimilarityConfig()
        self._embedding = embedding_service or EmbeddingService()

    async def search_similar_devlogs(
        self,
        query_text: str,
        user_id: str,
        limit: int = 10,
        filters: DevLogFilter | None = None,
    ) -> list[SimilarityResult]:
        """
        クエリテキストに類似した開発ログをベクトル検索で取得する。

        Args:
            query_text: 検索クエリテキスト
            user_id: ユーザーID（データ分離用）
            limit: 取得件数
            filters: フィルター条件

        Returns:
            類似度スコア順の開発ログリスト
        """
        # クエリテキストのembeddingを生成
        embedding_result = await self._embedding.embed_text(query_text)
        embedding_str = "[" + ",".join(str(v) for v in embedding_result.embedding) + "]"

        # pgvector コサイン距離検索
        sql = """
            SELECT
                id,
                project_id,
                summary,
                entry_type,
                1 - (embedding <=> :query_embedding::vector) AS similarity_score
            FROM devlog_entries
            WHERE user_id = :user_id
              AND embedding IS NOT NULL
        """

        params: dict = {
            "query_embedding": embedding_str,
            "user_id": user_id,
        }

        if filters:
            if filters.entry_types:
                sql += " AND entry_type = ANY(:entry_types)"
                params["entry_types"] = filters.entry_types
            if filters.technologies:
                sql += " AND technologies ?| :technologies"
                params["technologies"] = filters.technologies

        sql += " ORDER BY embedding <=> :query_embedding::vector LIMIT :limit"
        params["limit"] = limit

        db_gen = get_db()
        db = next(db_gen)
        try:
            result = db.execute(text(sql), params)
            rows = result.fetchall()

            return [
                SimilarityResult(
                    devlog_id=row[0],
                    project_id=row[1],
                    score=float(row[4]) if row[4] is not None else 0.0,
                    summary=row[2],
                    entry_type=row[3],
                )
                for row in rows
            ]
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

    async def find_similar_in_project(
        self,
        query_text: str,
        user_id: str,
        project_id: str,
        limit: int = 5,
    ) -> list[SimilarityResult]:
        """
        同一プロジェクト内の類似開発ログを検索する。

        Args:
            query_text: 検索クエリテキスト
            user_id: ユーザーID
            project_id: プロジェクトID
            limit: 取得件数
        """
        embedding_result = await self._embedding.embed_text(query_text)
        embedding_str = "[" + ",".join(str(v) for v in embedding_result.embedding) + "]"

        sql = """
            SELECT
                id,
                project_id,
                summary,
                entry_type,
                1 - (embedding <=> :query_embedding::vector) AS similarity_score
            FROM devlog_entries
            WHERE user_id = :user_id
              AND project_id = :project_id
              AND embedding IS NOT NULL
            ORDER BY embedding <=> :query_embedding::vector
            LIMIT :limit
        """

        db_gen = get_db()
        db = next(db_gen)
        try:
            result = db.execute(text(sql), {
                "query_embedding": embedding_str,
                "user_id": user_id,
                "project_id": project_id,
                "limit": limit,
            })
            rows = result.fetchall()

            return [
                SimilarityResult(
                    devlog_id=row[0],
                    project_id=row[1],
                    score=float(row[4]) if row[4] is not None else 0.0,
                    summary=row[2],
                    entry_type=row[3],
                )
                for row in rows
            ]
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass
