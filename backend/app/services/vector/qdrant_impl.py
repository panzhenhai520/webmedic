"""
Qdrant向量数据库实现
"""
import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from .base import BaseVectorDB, VectorSearchResult

logger = logging.getLogger(__name__)


class QdrantVectorDB(BaseVectorDB):
    """Qdrant向量数据库实现"""

    def __init__(
        self,
        mode: str = "embedded",
        path: Optional[str] = None,
        url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        初始化Qdrant客户端

        Args:
            mode: 模式（embedded/server）
            path: 内嵌模式存储路径
            url: 服务器模式URL
            api_key: 服务器模式API密钥
        """
        self.mode = mode
        self.path = path
        self.url = url
        self.api_key = api_key
        self.client: Optional[QdrantClient] = None

    async def initialize(self) -> None:
        """初始化Qdrant客户端"""
        try:
            if self.mode == "embedded":
                if not self.path:
                    raise ValueError("Embedded mode requires 'path' parameter")
                self.client = QdrantClient(path=self.path)
                logger.info(f"Qdrant initialized in embedded mode: {self.path}")
            elif self.mode == "server":
                if not self.url:
                    raise ValueError("Server mode requires 'url' parameter")
                self.client = QdrantClient(url=self.url, api_key=self.api_key)
                logger.info(f"Qdrant initialized in server mode: {self.url}")
            else:
                raise ValueError(f"Invalid mode: {self.mode}")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}")
            raise

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "cosine"
    ) -> None:
        """创建集合"""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")

        # 映射距离度量
        distance_map = {
            "cosine": Distance.COSINE,
            "euclidean": Distance.EUCLID,
            "dot": Distance.DOT,
        }

        if distance not in distance_map:
            raise ValueError(f"Invalid distance: {distance}")

        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance_map[distance]
                )
            )
            logger.info(f"Collection created: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    async def collection_exists(self, collection_name: str) -> bool:
        """检查集合是否存在"""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")

        try:
            collections = self.client.get_collections().collections
            return any(c.name == collection_name for c in collections)
        except Exception as e:
            logger.error(f"Failed to check collection existence: {e}")
            return False

    async def delete_collection(self, collection_name: str) -> None:
        """删除集合"""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")

        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Collection deleted: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise

    async def upsert_vectors(
        self,
        collection_name: str,
        ids: List[str],
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]]
    ) -> None:
        """插入或更新向量"""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")

        if len(ids) != len(vectors) != len(payloads):
            raise ValueError("ids, vectors, and payloads must have the same length")

        try:
            points = [
                PointStruct(
                    id=id_,
                    vector=vector,
                    payload=payload
                )
                for id_, vector, payload in zip(ids, vectors, payloads)
            ]

            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"Upserted {len(points)} vectors to {collection_name}")
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {e}")
            raise

    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """向量搜索"""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")

        try:
            # 构建过滤条件
            query_filter = None
            if filter_conditions:
                must_conditions = []
                for key, value in filter_conditions.items():
                    must_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                query_filter = Filter(must=must_conditions)

            # 执行搜索
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter
            )

            # 转换结果
            results = [
                VectorSearchResult(
                    id=str(hit.id),
                    score=hit.score,
                    payload=hit.payload or {}
                )
                for hit in search_result
            ]

            logger.info(f"Found {len(results)} results in {collection_name}")
            return results

        except Exception as e:
            logger.error(f"Failed to search vectors: {e}")
            raise

    async def delete_vectors(
        self,
        collection_name: str,
        ids: List[str]
    ) -> None:
        """删除向量"""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")

        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=ids
            )
            logger.info(f"Deleted {len(ids)} vectors from {collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            raise

    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """获取集合信息"""
        if not self.client:
            raise RuntimeError("Qdrant client not initialized")

        try:
            collection_info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status,
                "config": {
                    "vector_size": collection_info.config.params.vectors.size,
                    "distance": collection_info.config.params.vectors.distance.name,
                }
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise

    async def close(self) -> None:
        """关闭连接"""
        if self.client:
            # Qdrant客户端不需要显式关闭
            self.client = None
            logger.info("Qdrant client closed")
