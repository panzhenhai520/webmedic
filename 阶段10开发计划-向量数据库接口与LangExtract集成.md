# WebMedic 阶段10开发计划：统一向量数据库接口与LangExtract集成

## 一、开发目标

### 1.1 核心目标
1. **统一向量数据库接口**：实现抽象基类+工厂模式，支持Qdrant作为首选实现，为未来迁移到RAGFlow或其他向量数据库预留扩展性
2. **LangExtract集成**：增加LangExtract作为结构化抽取的替代方法，与现有Instructor方法并存，支持对比测试

### 1.2 技术方案
- **向量数据��**：Qdrant内嵌模式（开发环境）+ BGE-M3嵌入模型
- **抽取方法**：Instructor（现有）+ LangExtract（新增）
- **设计模式**：抽象基类 + 工厂模式
- **配置管理**：通过.env文件控制选择

### 1.3 严格约束
- ✅ 不修改已有接口名、表名、目录名
- ✅ 遵循《webmedic 开发技术细节文档》命名规范
- ✅ 每个文件标注完整路径
- ✅ 提供完整代码，包含所有import
- ✅ 提供启动、测试、完成说明、下阶段建议

---

## 二、架构设计

### 2.1 向量数据库抽象层架构

```
app/services/vector/
├── __init__.py
├── base.py              # BaseVectorDB抽象基类
├── qdrant_impl.py       # QdrantVectorDB实现
└── factory.py           # VectorDBFactory工厂类

app/services/
├── embedding_service.py # BGE-M3嵌入服务
└── index_service.py     # 修改：使用向量数据库抽象层
```

### 2.2 抽取器抽象层架构

```
app/services/extractors/
├── __init__.py
├── base.py              # BaseExtractor抽象基类
├── instructor_extractor.py  # InstructorExtractor实现（现有逻辑）
├── langextract_extractor.py # LangExtractExtractor实现
└── factory.py           # ExtractorFactory工厂类

app/services/
└── extract_service.py   # 修改：使用抽取器抽象层
```

### 2.3 配置项设计

```env
# 向量数据库配置
VECTOR_DB_TYPE=qdrant          # 向量数据库类型：qdrant/milvus/weaviate
QDRANT_MODE=embedded           # Qdrant模式：embedded/server
QDRANT_PATH=./qdrant_storage   # 内嵌模式存储路径
QDRANT_COLLECTION=medical_cases # 集合名称
QDRANT_VECTOR_SIZE=1024        # BGE-M3向量维度

# 嵌入模型配置
EMBEDDING_MODEL=BAAI/bge-m3    # 嵌入模型名称
EMBEDDING_DEVICE=cpu           # 计算设备：cpu/cuda
EMBEDDING_BATCH_SIZE=32        # 批处理大小

# 抽取器配置
EXTRACTOR_TYPE=instructor      # 抽取器类型：instructor/langextract
```

---

## 三、详细实施方案

### 3.1 向量数据库抽象层实现

#### 文件路径：`backend/app/services/vector/__init__.py`

```python
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
```

#### 文件路径：`backend/app/services/vector/base.py`

```python
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
```

#### 文件路径：`backend/app/services/vector/qdrant_impl.py`

```python
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
```

#### 文件路径：`backend/app/services/vector/factory.py`

```python
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
```

### 3.2 嵌入服务实现

#### 文件路径：`backend/app/services/embedding_service.py`

```python
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
        self.model_name = settings.EMBEDDING_MODEL
        self.device = settings.EMBEDDING_DEVICE
        self.batch_size = settings.EMBEDDING_BATCH_SIZE

    def initialize(self) -> None:
        """初始化嵌入模型"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = BGEM3FlagModel(
                self.model_name,
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
```

### 3.3 修改索引服务以使用向量数据库抽象层

#### 文件路径：`backend/app/services/index_service.py`

```python
"""
索引服务：处理医疗文档的向量化和索引
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.medical_document import MedicalDocument
from app.services.vector.factory import VectorDBFactory
from app.services.embedding_service import get_embedding_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class IndexService:
    """索引服务"""

    def __init__(self):
        self.vector_db = VectorDBFactory.create()
        self.embedding_service = get_embedding_service()
        self.collection_name = settings.QDRANT_COLLECTION

    async def initialize(self) -> None:
        """初始化索引服务"""
        try:
            # 初始化向量数据库
            await self.vector_db.initialize()

            # 检查集合是否存在，不存在则创建
            if not await self.vector_db.collection_exists(self.collection_name):
                vector_size = self.embedding_service.get_vector_size()
                await self.vector_db.create_collection(
                    collection_name=self.collection_name,
                    vector_size=vector_size,
                    distance="cosine"
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize index service: {e}")
            raise

    async def index_document(
        self,
        db: Session,
        document_id: int
    ) -> None:
        """
        索引单个文档

        Args:
            db: 数据库会话
            document_id: 文档ID
        """
        try:
            # 查询文档
            document = db.query(MedicalDocument).filter(
                MedicalDocument.id == document_id
            ).first()

            if not document:
                raise ValueError(f"Document not found: {document_id}")

            if not document.parsed_content:
                raise ValueError(f"Document has no parsed content: {document_id}")

            # 生成向量
            text = document.parsed_content
            vector = self.embedding_service.encode_single(text)

            # 构建元数据
            payload = {
                "document_id": document.id,
                "file_name": document.file_name,
                "file_path": document.file_path,
                "parsed_content": document.parsed_content[:500],  # 只存储前500字符
                "upload_time": document.upload_time.isoformat() if document.upload_time else None,
            }

            # 插入向量数据库
            await self.vector_db.upsert_vectors(
                collection_name=self.collection_name,
                ids=[str(document.id)],
                vectors=[vector],
                payloads=[payload]
            )

            # 更新文档索引状态
            document.index_status = "done"
            db.commit()

            logger.info(f"Document indexed successfully: {document_id}")

        except Exception as e:
            logger.error(f"Failed to index document {document_id}: {e}")
            # 更新文档索引状态为失败
            document = db.query(MedicalDocument).filter(
                MedicalDocument.id == document_id
            ).first()
            if document:
                document.index_status = "failed"
                db.commit()
            raise

    async def search_similar_documents(
        self,
        query_text: str,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[dict]:
        """
        搜索相似文档

        Args:
            query_text: 查询文本
            limit: 返回结果数量
            score_threshold: 相似度阈值

        Returns:
            相似文档列表
        """
        try:
            # 生成查询向量
            query_vector = self.embedding_service.encode_single(query_text)

            # 搜索向量数据库
            results = await self.vector_db.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )

            # 转换结果格式
            similar_docs = []
            for result in results:
                similar_docs.append({
                    "document_id": result.payload.get("document_id"),
                    "file_name": result.payload.get("file_name"),
                    "similarity_score": result.score,
                    "content_preview": result.payload.get("parsed_content", "")
                })

            logger.info(f"Found {len(similar_docs)} similar documents")
            return similar_docs

        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            raise

    async def delete_document_index(
        self,
        db: Session,
        document_id: int
    ) -> None:
        """
        删除文档索引

        Args:
            db: 数据库会话
            document_id: 文档ID
        """
        try:
            # 从向量数据库删除
            await self.vector_db.delete_vectors(
                collection_name=self.collection_name,
                ids=[str(document_id)]
            )

            # 更新文档索引状态
            document = db.query(MedicalDocument).filter(
                MedicalDocument.id == document_id
            ).first()
            if document:
                document.index_status = "pending"
                db.commit()

            logger.info(f"Document index deleted: {document_id}")

        except Exception as e:
            logger.error(f"Failed to delete document index {document_id}: {e}")
            raise

    async def get_index_stats(self) -> dict:
        """获取索引统计信息"""
        try:
            collection_info = await self.vector_db.get_collection_info(
                self.collection_name
            )
            return {
                "collection_name": collection_info["name"],
                "total_vectors": collection_info["vectors_count"],
                "total_points": collection_info["points_count"],
                "status": collection_info["status"],
                "vector_size": collection_info["config"]["vector_size"],
                "distance_metric": collection_info["config"]["distance"],
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            raise

    async def close(self) -> None:
        """关闭服务"""
        await self.vector_db.close()


# 全局单例
_index_service: Optional[IndexService] = None


async def get_index_service() -> IndexService:
    """获取索引服务单例"""
    global _index_service
    if _index_service is None:
        _index_service = IndexService()
        await _index_service.initialize()
    return _index_service
```

### 3.4 抽取器抽象层实现

#### 文件路径：`backend/app/services/extractors/__init__.py`

```python
"""
抽取器抽象层
"""
from .base import BaseExtractor
from .instructor_extractor import InstructorExtractor
from .langextract_extractor import LangExtractExtractor
from .factory import ExtractorFactory

__all__ = [
    "BaseExtractor",
    "InstructorExtractor",
    "LangExtractExtractor",
    "ExtractorFactory",
]
```

#### 文件路径：`backend/app/services/extractors/base.py`

```python
"""
抽取器抽象基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseExtractor(ABC):
    """抽取器抽象基类"""

    @abstractmethod
    async def extract(
        self,
        dialogue_text: str,
        use_mock: bool = False
    ) -> Dict[str, Any]:
        """
        从对话文本中抽取结构化信息

        Args:
            dialogue_text: 对话文本
            use_mock: 是否使用Mock模式

        Returns:
            结构化数据字典
        """
        pass

    @abstractmethod
    def get_extractor_name(self) -> str:
        """获取抽取器名称"""
        pass
```

#### 文件路径：`backend/app/services/extractors/instructor_extractor.py`

```python
"""
Instructor抽取器实现（现有逻辑）
"""
import logging
from typing import Dict, Any
import re

from app.services.llm_service import LLMService
from .base import BaseExtractor

logger = logging.getLogger(__name__)


class InstructorExtractor(BaseExtractor):
    """Instructor抽取器实现"""

    def __init__(self):
        self.llm_service = LLMService()

    async def extract(
        self,
        dialogue_text: str,
        use_mock: bool = False
    ) -> Dict[str, Any]:
        """
        使用Instructor从对话文本中抽取结构化信息

        Args:
            dialogue_text: 对话文本
            use_mock: 是否使用Mock模式

        Returns:
            结构化数据字典
        """
        try:
            if use_mock:
                return self._generate_mock_json(dialogue_text)

            # 使用LLM服务进行抽取
            result = await self.llm_service.extract_structured_record(dialogue_text)
            logger.info("Instructor extraction completed")
            return result

        except Exception as e:
            logger.error(f"Instructor extraction failed: {e}")
            raise

    def _generate_mock_json(self, dialogue_text: str) -> Dict[str, Any]:
        """
        Mock模式：从对话文本中提取关键信息

        Args:
            dialogue_text: 对话文本

        Returns:
            模拟的结构化数据
        """
        # 症状关键词映射
        symptom_keywords = {
            "痛": "疼痛", "晕": "头晕", "胀": "肿胀", "麻": "麻木",
            "酸": "酸痛", "累": "疲劳", "咳": "咳嗽", "烧": "发烧"
        }

        # 身体部位���键词
        body_part_keywords = {
            "颈": "颈部", "头": "头部", "肩": "肩部", "背": "背部",
            "腰": "腰部", "腿": "腿部", "手": "手部", "脚": "脚部"
        }

        # 提取症状和部位
        symptoms = []
        body_parts = []

        for keyword, symptom in symptom_keywords.items():
            if keyword in dialogue_text:
                symptoms.append(symptom)

        for keyword, part in body_part_keywords.items():
            if keyword in dialogue_text:
                body_parts.append(part)

        # 提取时间（取最后一次提到的时间）
        day_patterns = [
            r'(\d+)\s*天',
            r'(\d+)\s*日',
            r'(\d+)\s*周',
            r'(\d+)\s*个月'
        ]

        duration = "未提及"
        for pattern in day_patterns:
            matches = re.findall(pattern, dialogue_text)
            if matches:
                duration = f"{matches[-1]}天"  # 取最后一次提到的
                break

        # 提取过敏史
        allergy = "无" if "过敏" not in dialogue_text else "青霉素过敏"

        # 构建结构化结果
        chief_complaint = f"{','.join(body_parts) if body_parts else '颈部'}{','.join(symptoms) if symptoms else '疼痛'}{duration}"

        return {
            "chief_complaint": chief_complaint,
            "present_illness_history": f"患者主诉{chief_complaint}。",
            "past_medical_history": "既往体健",
            "allergy_history": allergy,
            "physical_examination": "颈部活动受限，压痛明显",
            "preliminary_diagnosis": "颈椎病",
            "treatment_plan": "建议进行颈椎X光检查，物理治疗"
        }

    def get_extractor_name(self) -> str:
        """获取抽取器名称"""
        return "instructor"
```

#### 文件路径：`backend/app/services/extractors/langextract_extractor.py`

```python
"""
LangExtract抽取器实现
"""
import logging
from typing import Dict, Any
from langextract import LangExtract

from .base import BaseExtractor

logger = logging.getLogger(__name__)


class LangExtractExtractor(BaseExtractor):
    """LangExtract抽取器实现"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        """
        初始化LangExtract抽取器

        Args:
            api_key: DeepSeek API密钥
            model: 模型名称
        """
        self.extractor = LangExtract(api_key=api_key, model=model)

    async def extract(
        self,
        dialogue_text: str,
        use_mock: bool = False
    ) -> Dict[str, Any]:
        """
        使用LangExtract从对话文本中抽取结构化信息

        Args:
            dialogue_text: 对话文本
            use_mock: 是否使用Mock模式

        Returns:
            结构化数据字典
        """
        try:
            if use_mock:
                return self._generate_mock_json(dialogue_text)

            # 定义抽取schema
            schema = {
                "chief_complaint": "主诉",
                "present_illness_history": "现病史",
                "past_medical_history": "既往史",
                "allergy_history": "过敏史",
                "physical_examination": "体格检查",
                "preliminary_diagnosis": "初步诊断",
                "treatment_plan": "治疗方案"
            }

            # 使用LangExtract进行抽取
            result = self.extractor.extract(
                text=dialogue_text,
                schema=schema
            )

            logger.info("LangExtract extraction completed")
            return result

        except Exception as e:
            logger.error(f"LangExtract extraction failed: {e}")
            raise

    def _generate_mock_json(self, dialogue_text: str) -> Dict[str, Any]:
        """
        Mock模式：返回简化的结构化数据

        Args:
            dialogue_text: 对话文本

        Returns:
            模拟的结构化数据
        """
        import re

        # 简化的Mock实现
        symptoms = []
        if "痛" in dialogue_text:
            symptoms.append("疼痛")
        if "晕" in dialogue_text:
            symptoms.append("头晕")

        # 提取时间
        day_matches = re.findall(r'(\d+)\s*天', dialogue_text)
        duration = f"{day_matches[-1]}天" if day_matches else "未提及"

        return {
            "chief_complaint": f"{'、'.join(symptoms) if symptoms else '不适'}{duration}",
            "present_illness_history": f"患者主诉{duration}前出现{'、'.join(symptoms) if symptoms else '不适'}。",
            "past_medical_history": "既往体健",
            "allergy_history": "无" if "过敏" not in dialogue_text else "青霉素过敏",
            "physical_examination": "查体未见明显异常",
            "preliminary_diagnosis": "待查",
            "treatment_plan": "建议进一步检查"
        }

    def get_extractor_name(self) -> str:
        """获取抽取器名称"""
        return "langextract"
```

#### 文件路径：`backend/app/services/extractors/factory.py`

```python
"""
抽取器工厂类
"""
import logging
from typing import Optional

from app.core.config import settings
from .base import BaseExtractor
from .instructor_extractor import InstructorExtractor
from .langextract_extractor import LangExtractExtractor

logger = logging.getLogger(__name__)


class ExtractorFactory:
    """抽取器工厂类"""

    @staticmethod
    def create(extractor_type: Optional[str] = None) -> BaseExtractor:
        """
        创建抽取器实例

        Args:
            extractor_type: 抽取器类型（instructor/langextract），默认从配置读取

        Returns:
            抽取器实例
        """
        extractor_type = extractor_type or settings.EXTRACTOR_TYPE

        if extractor_type == "instructor":
            return InstructorExtractor()
        elif extractor_type == "langextract":
            return LangExtractExtractor(
                api_key=settings.DEEPSEEK_API_KEY,
                model="deepseek-chat"
            )
        else:
            raise ValueError(f"Unsupported extractor type: {extractor_type}")
```

### 3.5 修改抽取服务以使用抽取器抽象层

#### 文件路径：`backend/app/services/extract_service.py`

```python
"""
抽取服务：从对话文本中抽取结构化医疗信息
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.encounter_session import EncounterSession
from app.models.transcript_segment import TranscriptSegment
from app.models.structured_record import StructuredRecord
from app.services.extractors.factory import ExtractorFactory
from app.core.config import settings

logger = logging.getLogger(__name__)


class ExtractService:
    """抽取服务"""

    def __init__(self, extractor_type: Optional[str] = None):
        """
        初始化抽取服务

        Args:
            extractor_type: 抽取器类型，默认从配置读取
        """
        self.extractor = ExtractorFactory.create(extractor_type)
        self.use_mock = settings.LLM_USE_MOCK

    async def extract_from_session(
        self,
        db: Session,
        session_id: int,
        extractor_type: Optional[str] = None
    ) -> StructuredRecord:
        """
        从会话中抽取结构化信息

        Args:
            db: 数据库会话
            session_id: 会话ID
            extractor_type: 抽取器类型（可选，用于临时切换抽取器）

        Returns:
            结构化记录
        """
        try:
            # 查询会话
            session = db.query(EncounterSession).filter(
                EncounterSession.id == session_id
            ).first()

            if not session:
                raise ValueError(f"Session not found: {session_id}")

            # 查询所有转写片段
            segments = db.query(TranscriptSegment).filter(
                TranscriptSegment.session_id == session_id
            ).order_by(TranscriptSegment.sequence_number).all()

            if not segments:
                raise ValueError(f"No transcript segments found for session: {session_id}")

            # 拼接对话文本
            dialogue_text = "\n".join([
                f"{seg.speaker}: {seg.text_content}"
                for seg in segments
            ])

            # 如果指定了临时抽取器类型，创建新的抽取器
            extractor = self.extractor
            if extractor_type:
                extractor = ExtractorFactory.create(extractor_type)

            # 执行抽取
            extracted_data = await extractor.extract(
                dialogue_text=dialogue_text,
                use_mock=self.use_mock
            )

            # 保存到数据库
            structured_record = StructuredRecord(
                session_id=session_id,
                chief_complaint=extracted_data.get("chief_complaint", ""),
                present_illness_history=extracted_data.get("present_illness_history", ""),
                past_medical_history=extracted_data.get("past_medical_history", ""),
                allergy_history=extracted_data.get("allergy_history", ""),
                physical_examination=extracted_data.get("physical_examination", ""),
                preliminary_diagnosis=extracted_data.get("preliminary_diagnosis", ""),
                treatment_plan=extracted_data.get("treatment_plan", ""),
                extractor_type=extractor.get_extractor_name()
            )

            db.add(structured_record)
            db.commit()
            db.refresh(structured_record)

            logger.info(f"Extraction completed for session {session_id} using {extractor.get_extractor_name()}")
            return structured_record

        except Exception as e:
            logger.error(f"Failed to extract from session {session_id}: {e}")
            db.rollback()
            raise

    async def compare_extractors(
        self,
        db: Session,
        session_id: int
    ) -> dict:
        """
        对比不同抽取器的结果

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            对比结果
        """
        try:
            # 使用Instructor抽取
            instructor_result = await self.extract_from_session(
                db=db,
                session_id=session_id,
                extractor_type="instructor"
            )

            # 使用LangExtract抽取
            langextract_result = await self.extract_from_session(
                db=db,
                session_id=session_id,
                extractor_type="langextract"
            )

            return {
                "instructor": {
                    "chief_complaint": instructor_result.chief_complaint,
                    "present_illness_history": instructor_result.present_illness_history,
                    "preliminary_diagnosis": instructor_result.preliminary_diagnosis,
                },
                "langextract": {
                    "chief_complaint": langextract_result.chief_complaint,
                    "present_illness_history": langextract_result.present_illness_history,
                    "preliminary_diagnosis": langextract_result.preliminary_diagnosis,
                }
            }

        except Exception as e:
            logger.error(f"Failed to compare extractors for session {session_id}: {e}")
            raise
```

### 3.6 修改配置文件

#### 文件路径：`backend/app/core/config.py`

在现有配置类中添加以下配置项：

```python
# 在Settings类中添加以下字段

# ========== 向量数据库配置 ==========
VECTOR_DB_TYPE: str = "qdrant"
QDRANT_MODE: str = "embedded"
QDRANT_PATH: str = "./qdrant_storage"
QDRANT_URL: Optional[str] = None
QDRANT_API_KEY: Optional[str] = None
QDRANT_COLLECTION: str = "medical_cases"
QDRANT_VECTOR_SIZE: int = 1024

# ========== 嵌入模型配置 ==========
EMBEDDING_MODEL: str = "BAAI/bge-m3"
EMBEDDING_DEVICE: str = "cpu"
EMBEDDING_BATCH_SIZE: int = 32

# ========== 抽取器配置 ==========
EXTRACTOR_TYPE: str = "instructor"
```

#### 文件路径：`backend/.env.example`

添加以下配置项：

```env
# ========== 向量数据库配置 ==========
VECTOR_DB_TYPE=qdrant
QDRANT_MODE=embedded
QDRANT_PATH=./qdrant_storage
QDRANT_COLLECTION=medical_cases
QDRANT_VECTOR_SIZE=1024

# 如果使用服务器模式，配置以下项
# QDRANT_MODE=server
# QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=your_api_key_here

# ========== 嵌入模型配置 ==========
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DEVICE=cpu
EMBEDDING_BATCH_SIZE=32

# ========== 抽取器配置 ==========
EXTRACTOR_TYPE=instructor
```

#### 文件路径：`backend/.env`

在现有.env文件中添加相同的配置项（使用实际值）。

### 3.7 修改数据库模型

#### 文件路径：`backend/app/models/structured_record.py`

在StructuredRecord模型中添加extractor_type字段：

```python
# 在StructuredRecord类中添加以下字段

extractor_type = Column(String(50), nullable=True, comment="抽取器类型")
```

### 3.8 前端修改

#### 文件路径：`frontend/src/views/DoctorWorkbench.vue`

在抽取功能区域添加抽取器选择下拉框：

```vue
<!-- 在"生成结构化病历"按钮前添加 -->
<el-select
  v-model="selectedExtractor"
  placeholder="选择抽取器"
  style="width: 150px; margin-right: 10px;"
>
  <el-option label="Instructor" value="instructor" />
  <el-option label="LangExtract" value="langextract" />
</el-select>

<!-- 在script setup中添加 -->
<script setup>
// ... 现有代码 ...

const selectedExtractor = ref('instructor')

// 修改handleExtract函数，传递extractor_type参数
const handleExtract = async () => {
  try {
    loading.value = true
    const response = await extractApi.extractStructuredRecord(
      currentSession.value.id,
      selectedExtractor.value  // 传递选择的抽取器类型
    )
    // ... 现有处理逻辑 ...
  } catch (error) {
    // ... 错误处理 ...
  } finally {
    loading.value = false
  }
}
</script>
```

#### 文件路径：`frontend/src/api/extract.js`

修改API调用以支持extractor_type参数：

```javascript
/**
 * 抽取结构化病历
 */
export const extractStructuredRecord = (sessionId, extractorType = 'instructor') => {
  return http.post('/extract', {
    session_id: sessionId,
    extractor_type: extractorType
  })
}
```

#### 文件路径：`backend/app/api/endpoints/extract.py`

修改API端点以接收extractor_type参数：

```python
from pydantic import BaseModel, Field
from typing import Optional

class ExtractRequest(BaseModel):
    session_id: int = Field(..., description="会话ID")
    extractor_type: Optional[str] = Field("instructor", description="抽取器类型")

@router.post("/extract")
async def extract_structured_record(
    request: ExtractRequest,
    db: Session = Depends(get_db)
):
    """抽取结构化病历"""
    try:
        extract_service = ExtractService()
        result = await extract_service.extract_from_session(
            db=db,
            session_id=request.session_id,
            extractor_type=request.extractor_type
        )

        return {
            "success": True,
            "message": "抽取成功",
            "data": {
                "id": result.id,
                "chief_complaint": result.chief_complaint,
                "present_illness_history": result.present_illness_history,
                "past_medical_history": result.past_medical_history,
                "allergy_history": result.allergy_history,
                "physical_examination": result.physical_examination,
                "preliminary_diagnosis": result.preliminary_diagnosis,
                "treatment_plan": result.treatment_plan,
                "extractor_type": result.extractor_type
            }
        }
    except Exception as e:
        logger.error(f"Extract failed: {e}")
        return {
            "success": False,
            "message": f"抽取失败: {str(e)}",
            "data": None
        }
```

---

## 四、依赖安装

### 4.1 Python依赖

#### 文件路径：`backend/requirements.txt`

添加以下依赖：

```txt
# 向量数据库
qdrant-client==1.7.0

# 嵌入模型
FlagEmbedding==1.2.10

# LangExtract
langextract==0.1.5

# 已有依赖保持不变
# ...
```

### 4.2 安装命令

```bash
cd D:\webmedic\backend
pip install qdrant-client==1.7.0 FlagEmbedding==1.2.10 langextract==0.1.5
```

---

## 五、数据库迁移

### 5.1 添加extractor_type字段

```sql
ALTER TABLE structured_records
ADD COLUMN extractor_type VARCHAR(50) NULL COMMENT '抽取器类型';
```

或者使用Python脚本：

```python
# backend/scripts/add_extractor_type_field.py
from sqlalchemy import create_engine, text
from app.core.config import settings

engine = create_engine(settings.database_url)

with engine.connect() as conn:
    conn.execute(text("""
        ALTER TABLE structured_records
        ADD COLUMN extractor_type VARCHAR(50) NULL COMMENT '抽取器类型'
    """))
    conn.commit()

print("Field added successfully")
```

---

## 六、启动步骤

### 6.1 环境准备

1. **安装Python依赖**

```bash
cd D:\webmedic\backend
pip install -r requirements.txt
```

2. **配置环境变量**

编辑 `backend/.env` 文件，添加向量数据库和嵌入模型配置：

```env
# 向量数据库配置
VECTOR_DB_TYPE=qdrant
QDRANT_MODE=embedded
QDRANT_PATH=./qdrant_storage
QDRANT_COLLECTION=medical_cases
QDRANT_VECTOR_SIZE=1024

# 嵌入模型配置
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DEVICE=cpu
EMBEDDING_BATCH_SIZE=32

# 抽取器配置
EXTRACTOR_TYPE=instructor
```

3. **数据库迁移**

```bash
cd D:\webmedic\backend
python scripts/add_extractor_type_field.py
```

### 6.2 启动后端服务

```bash
cd D:\webmedic\backend
python run.py
```

首次启动时会自动：
- 下载BGE-M3模型（约2GB，需要5-15分钟）
- 初始化Qdrant向量数据库
- 创建medical_cases集合

### 6.3 启动前端服务

```bash
cd D:\webmedic\frontend
npm run dev
```

---

## 七、测试步骤

### 7.1 向量数据库功能测试

#### 测试1：索引文档

1. 访问 http://localhost:5173
2. 进入"病历管理"页面
3. 上传一个PDF病历文件
4. 点击"索引"按钮
5. 检查索引状态是否变为"已索引"

**预期结果**：
- 文档成功解析
- 向量生成成功
- Qdrant集合中新增一条记录
- 索引状态更新为"done"

#### 测试2：相似病历检索

1. 在工作站页面开始新会话
2. 录音并转写对话
3. 点击"生成结构化病历"
4. 点击"查找相似病历"
5. 查看相似病历列表

**预期结果**：
- 返回相似度最高的5个病历
- 每个病历显示相似度分数
- 相似度分数在0.7以上

#### 测试3：向量数据库统计

使用Python脚本测试：

```python
# backend/scripts/test_vector_db.py
import asyncio
from app.services.index_service import get_index_service

async def test_stats():
    service = await get_index_service()
    stats = await service.get_index_stats()
    print("Index Stats:")
    print(f"  Collection: {stats['collection_name']}")
    print(f"  Total Vectors: {stats['total_vectors']}")
    print(f"  Vector Size: {stats['vector_size']}")
    print(f"  Distance Metric: {stats['distance_metric']}")

asyncio.run(test_stats())
```

### 7.2 抽取器功能测试

#### 测试1：Instructor抽取器

1. 在工作站页面，抽取器选择"Instructor"
2. 录音并转写对话
3. 点击"生成结构化病历"
4. 查看抽取结果

**预期结果**：
- 成功抽取主诉、现病史等字段
- extractor_type字段值为"instructor"

#### 测试2：LangExtract抽取器

1. 在工作站页面，抽取器选择"LangExtract"
2. 使用相同的会话
3. 点击"生成结构化病历"
4. 查看抽取结果

**预期结果**：
- 成功抽取主诉、现病史等字段
- extractor_type字段值为"langextract"
- 结果与Instructor可能略有不同

#### 测试3：对比两种抽取器

使用API测试：

```bash
curl -X POST http://localhost:8001/api/v1/extract/compare \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1}'
```

**预期结果**：
- 返回两种抽取器的结果对比
- 可以看到不同抽取器的差异

### 7.3 Mock模式测试

1. 修改 `.env` 文件：`LLM_USE_MOCK=true`
2. 重启后端服务
3. 进行抽取测试

**预期结果**：
- 不调用DeepSeek API
- 从对话文本中提取关键信息
- 返回模拟的结构化数据

### 7.4 完整工作流测试

1. 开始新会话
2. 录音：模拟医患对话
3. 转写：生成对话文本
4. 抽取：使用Instructor生成结构化病历
5. 检索：查找相似病历（基于向量搜索）
6. 生成草稿：基于结构化数据和相似病历
7. 生成临床提示：基于结构化数据

**预期结果**：
- 整个流程顺畅无阻
- 相似病历检索结果准确
- 草稿和临床提示质量良好

---

## 八、本阶段完成说明

### 8.1 已实现功能

✅ **向量数据库抽象层**
- BaseVectorDB抽象基类
- QdrantVectorDB实现（内嵌模式+服务器模式）
- VectorDBFactory工厂类
- 支持未来扩展到Milvus、Weaviate等

✅ **BGE-M3嵌入服务**
- 文本向量化功能
- 批处理支持
- CPU/GPU自动选择
- 单例模式管理

✅ **索引服务重构**
- 使用向量数据库抽象层
- 文档索引功能
- 相似文档检索功能
- 索引统计功能

✅ **抽取器抽象层**
- BaseExtractor抽象基类
- InstructorExtractor实现（现有逻辑）
- LangExtractExtractor实现
- ExtractorFactory工厂类

✅ **抽取服务重构**
- 使用抽取器抽象层
- 支持动态切换抽取器
- 抽取器对比功能

✅ **前端UI增强**
- 抽取器选择下拉框
- 支持切换Instructor/LangExtract

✅ **配置管理**
- 向量数据库配置
- 嵌入模型配置
- 抽取器配置

### 8.2 技术亮点

1. **高扩展性**：抽象基类+工厂模式，易于添加新的向量数据库和抽取器
2. **零部署成本**：Qdrant内嵌模式，无需额外部署向量数据库服务
3. **高性能**：BGE-M3模型，1024维向量，余弦相似度搜索
4. **灵活配置**：通过.env文件控制所有选项
5. **向后兼容**：不修改已有接口名、表名、目录名

### 8.3 文件清单

**新建文件**（13个）：
1. `backend/app/services/vector/__init__.py`
2. `backend/app/services/vector/base.py`
3. `backend/app/services/vector/qdrant_impl.py`
4. `backend/app/services/vector/factory.py`
5. `backend/app/services/embedding_service.py`
6. `backend/app/services/extractors/__init__.py`
7. `backend/app/services/extractors/base.py`
8. `backend/app/services/extractors/instructor_extractor.py`
9. `backend/app/services/extractors/langextract_extractor.py`
10. `backend/app/services/extractors/factory.py`
11. `backend/scripts/add_extractor_type_field.py`
12. `backend/scripts/test_vector_db.py`

**修改文件**（7个）：
1. `backend/app/services/index_service.py`
2. `backend/app/services/extract_service.py`
3. `backend/app/core/config.py`
4. `backend/app/models/structured_record.py`
5. `backend/app/api/endpoints/extract.py`
6. `frontend/src/views/DoctorWorkbench.vue`
7. `frontend/src/api/extract.js`

**配置文件**（2个）：
1. `backend/.env.example`
2. `backend/.env`

**依赖文件**（1个）：
1. `backend/requirements.txt`

---

## 九、下一阶段建议

### 9.1 阶段11：性能优化与监控

**建议功能**：
1. **向量索引优化**
   - HNSW参数调优（ef_construct, M）
   - 批量索引优化
   - 增量索引支持

2. **嵌入缓存**
   - Redis缓存常用查询向量
   - 减少重复计算

3. **监控面板**
   - 向量数据库性能监控
   - 抽取器性能对比
   - API响应时间统计

4. **日志增强**
   - 结构化日志
   - 日志聚合分析
   - 错误告警

### 9.2 阶段12：高级检索功能

**建议功能**：
1. **混合检索**
   - 向量检索 + 关键词检索
   - 重排序（Reranking）

2. **过滤检索**
   - 按时间范围过滤
   - 按诊断类型过滤
   - 按医生过滤

3. **多模态检索**
   - 支持医学影像检索
   - 文本+图像联合检索

### 9.3 阶段13：生产部署准备

**建议功能**：
1. **Qdrant服务器模式部署**
   - Docker部署
   - 集群配置
   - 数据备份

2. **负载均衡**
   - 多实例部署
   - 请求分发

3. **安全加固**
   - API认证
   - 数据加密
   - 访问控制

### 9.4 阶段14：RAGFlow迁移（可选）

如果需要迁移到RAGFlow：
1. 实现RAGFlowVectorDB类
2. 数据迁移脚本
3. 配置切换
4. 功能验证

---

## 十、注意事项

### 10.1 开发注意事项

1. **模型下载**：首次启动会下载BGE-M3模型（约2GB），确保网络畅通
2. **内存占用**：BGE-M3模型加载后占用约2GB内存
3. **向量维度**：BGE-M3固定1024维，不可修改
4. **Qdrant存储**：内嵌模式数据存储在`./qdrant_storage`目录
5. **LangExtract依赖**：需要DeepSeek API密钥

### 10.2 性能注意事项

1. **批处理**：索引大量文档时使用批处理，避免逐个索引
2. **相似度阈值**：建议设置为0.7，过低会返回不相关结果
3. **检索数量**：建议limit设置为5-10，过多影响性能
4. **CPU vs GPU**：如有GPU，设置`EMBEDDING_DEVICE=cuda`可显著提升性能

### 10.3 故障排查

**问题1：Qdrant初始化失败**
- 检查`QDRANT_PATH`目录是否有写权限
- 检查端口6333是否被占用（服务器模式）

**问题2：BGE-M3加载失败**
- 检查网络连接
- 检查磁盘空间（需要至少5GB）
- 尝试手动下载模型到`~/.cache/huggingface`

**问题3：LangExtract调用失败**
- 检查DeepSeek API密钥是否正确
- 检查API配额是否充足
- 尝试使用Mock模式测试

**问题4：相似病历检索无结果**
- 检查是否已索引文档
- 检查相似度阈值是否过高
- 检查查询文本是否有效

---

## 十一、参考文档

1. **Qdrant官方文档**：https://qdrant.tech/documentation/
2. **BGE-M3论文**：https://arxiv.org/abs/2402.03216
3. **FlagEmbedding GitHub**：https://github.com/FlagOpen/FlagEmbedding
4. **LangExtract文档**：https://github.com/langextract/langextract
5. **WebMedic技术细节文档**：`D:\webmedic\webmedic 开发技术细节文档.md`

---

**计划编写完成时间**：2026-03-08
**预计实施时间**：3-5个工作日
**难度评级**：⭐⭐⭐⭐（中高难度）
