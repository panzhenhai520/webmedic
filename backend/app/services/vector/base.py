"""
向量数据库抽象基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class VectorSearchResult:
    """向量搜索结果"""
    id: str
    score: float
    payload: Dict[str, Any]


class BaseVectorDB(ABC):
    """向量数据库抽象基类"""

    @abstractmethod
    async def initialize(self) -> None:
        """初始化向量数据库连接"""
        pass

    @abstractmethod
    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "cosine"
    ) -> None:
        """
        创建集合

        Args:
            collection_name: 集合名称
            vector_size: 向量维度
            distance: 距离度量方式（cosine/euclidean/dot）
        """
        pass

    @abstractmethod
    async def collection_exists(self, collection_name: str) -> bool:
        """检查集合是否存在"""
        pass

    @abstractmethod
    async def upsert_vectors(
        self,
        collection_name: str,
        ids: List[str],
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]]
    ) -> None:
        """
        插入或更新向量

        Args:
            collection_name: 集合名称
            ids: 向量ID列表
            vectors: 向量列表
            payloads: 元数据列表
        """
        pass

    @abstractmethod
    async def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[VectorSearchResult]:
        """
        向量搜索

        Args:
            collection_name: 集合名称
            query_vector: 查询向量
            limit: 返回结果数量
            score_threshold: 相似度阈值
            filter_conditions: 过滤条件

        Returns:
            搜索结果列表
        """
        pass

    @abstractmethod
    async def delete_vectors(
        self,
        collection_name: str,
        ids: List[str]
    ) -> None:
        """删除向量"""
        pass

    @abstractmethod
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """获取集合信息"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭连接"""
        pass
