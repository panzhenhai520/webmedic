"""
嵌入服务：使用BGE-M3模型生成文本向量
"""
import logging
from typing import List, Optional
import torch
from FlagEmbedding import BGEM3FlagModel

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """嵌入服务"""

    def __init__(self):
        self.model: Optional[BGEM3FlagModel] = None
        # 优先使用本地路径，如果没有设置则使用模型名称
        self.model_name_or_path = settings.EMBEDDING_MODEL_PATH or settings.EMBEDDING_MODEL
        self.device = settings.EMBEDDING_DEVICE
        self.batch_size = settings.EMBEDDING_BATCH_SIZE

    def initialize(self) -> None:
        """初始化嵌入模型"""
        try:
            logger.info(f"Loading embedding model: {self.model_name_or_path}")
            self.model = BGEM3FlagModel(
                self.model_name_or_path,
                use_fp16=False if self.device == "cpu" else True
            )
            logger.info(f"Embedding model loaded on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def encode(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        max_length: int = 512
    ) -> List[List[float]]:
        """
        将文本编码为向量

        Args:
            texts: 文本列表
            batch_size: 批处理大小
            max_length: 最大文本长度

        Returns:
            向量列表
        """
        if not self.model:
            raise RuntimeError("Embedding model not initialized")

        if not texts:
            return []

        batch_size = batch_size or self.batch_size

        try:
            # BGE-M3返回dense向量
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                max_length=max_length
            )['dense_vecs']

            # 转换为列表格式
            if isinstance(embeddings, torch.Tensor):
                embeddings = embeddings.cpu().numpy()

            return embeddings.tolist()

        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise

    def encode_single(self, text: str, max_length: int = 512) -> List[float]:
        """
        编码单个文本

        Args:
            text: 文本
            max_length: 最大文本长度

        Returns:
            向量
        """
        embeddings = self.encode([text], batch_size=1, max_length=max_length)
        return embeddings[0] if embeddings else []

    def get_vector_size(self) -> int:
        """获取向量维度"""
        if not self.model:
            raise RuntimeError("Embedding model not initialized")
        # BGE-M3的dense向量维度是1024
        return 1024


# 全局单例
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """获取嵌入服务单例"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
        _embedding_service.initialize()
    return _embedding_service
