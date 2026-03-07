"""
向量数据库抽象层
"""
from .base import BaseVectorDB, VectorSearchResult
from .qdrant_impl import QdrantVectorDB
from .factory import VectorDBFactory

__all__ = [
    "BaseVectorDB",
    "VectorSearchResult",
    "QdrantVectorDB",
    "VectorDBFactory",
]
