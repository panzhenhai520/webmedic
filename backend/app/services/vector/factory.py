"""
向量数据库工厂类
"""
import logging
from typing import Optional

from app.core.config import settings
from .base import BaseVectorDB
from .qdrant_impl import QdrantVectorDB

logger = logging.getLogger(__name__)


class VectorDBFactory:
    """向量数据库工厂类"""

    @staticmethod
    def create(db_type: Optional[str] = None) -> BaseVectorDB:
        """
        创建向量数据库实例

        Args:
            db_type: 数据库类型（qdrant/milvus/weaviate），默认从配置读取

        Returns:
            向量数据库实例
        """
        db_type = db_type or settings.VECTOR_DB_TYPE

        if db_type == "qdrant":
            return QdrantVectorDB(
                mode=settings.QDRANT_MODE,
                path=settings.QDRANT_PATH if settings.QDRANT_MODE == "embedded" else None,
                url=settings.QDRANT_URL if settings.QDRANT_MODE == "server" else None,
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_MODE == "server" else None
            )
        elif db_type == "milvus":
            # 未来实现
            raise NotImplementedError("Milvus implementation not available yet")
        elif db_type == "weaviate":
            # 未来实现
            raise NotImplementedError("Weaviate implementation not available yet")
        else:
            raise ValueError(f"Unsupported vector database type: {db_type}")
