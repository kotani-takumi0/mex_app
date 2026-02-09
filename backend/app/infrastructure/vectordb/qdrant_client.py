# このファイルは非推奨です。pgvectorへの移行に伴い、Qdrantは使用されなくなりました。
# 参照していたコードは similarity_engine.py (pgvector版) に移行済みです。
raise ImportError(
    "Qdrant client is deprecated. Use pgvector via SQLAlchemy instead. "
    "See backend/app/domain/similarity/similarity_engine.py"
)
