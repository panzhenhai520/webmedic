# Qdrant 迁移到 RAGFlow 指南

## 设计原则：面向接口编程

### 方案：抽象层设计

通过抽象层隔离具体实现，使迁移变得简单。

```python
# backend/app/services/retrieval/base.py
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseRetrievalService(ABC):
    """检索服务基类"""

    @abstractmethod
    def index_document(self, doc_id: int, text: str, metadata: dict):
        """索引文档"""
        pass

    @abstractmethod
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """检索相似文档"""
        pass

    @abstractmethod
    def delete_document(self, doc_id: int):
        """删除文档"""
        pass
```

### 实现1：Qdrant 实现

```python
# backend/app/services/retrieval/qdrant_impl.py
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from app.services.retrieval.base import BaseRetrievalService

class QdrantRetrievalService(BaseRetrievalService):
    """基于 Qdrant 的检索服务"""

    def __init__(self):
        self.client = QdrantClient(path="./qdrant_data")
        self.embedding_model = SentenceTransformer('BAAI/bge-m3')
        self.collection_name = "medical_records"

    def index_document(self, doc_id: int, text: str, metadata: dict):
        """索引文档"""
        vector = self.embedding_model.encode(text).tolist()
        self.client.upsert(
            collection_name=self.collection_name,
            points=[{
                "id": doc_id,
                "vector": vector,
                "payload": {"text": text, **metadata}
            }]
        )

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """检索相似文档"""
        query_vector = self.embedding_model.encode(query).tolist()
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )

        return [
            {
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text"),
                "metadata": result.payload
            }
            for result in results
        ]

    def delete_document(self, doc_id: int):
        """删除文档"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=[doc_id]
        )
```

### 实现2：RAGFlow 实现

```python
# backend/app/services/retrieval/ragflow_impl.py
import requests
from app.services.retrieval.base import BaseRetrievalService
from app.core.config import settings

class RAGFlowRetrievalService(BaseRetrievalService):
    """基于 RAGFlow 的检索服务"""

    def __init__(self):
        self.base_url = settings.RAGFLOW_API_URL
        self.api_key = settings.RAGFLOW_API_KEY
        self.dataset_id = settings.RAGFLOW_DATASET_ID

    def index_document(self, doc_id: int, text: str, metadata: dict):
        """索引文档"""
        response = requests.post(
            f"{self.base_url}/api/v1/documents",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "dataset_id": self.dataset_id,
                "doc_id": str(doc_id),
                "content": text,
                "metadata": metadata
            }
        )
        response.raise_for_status()

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """检索相似文档"""
        response = requests.post(
            f"{self.base_url}/api/v1/search",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "dataset_id": self.dataset_id,
                "query": query,
                "top_k": top_k
            }
        )
        response.raise_for_status()

        results = response.json()["data"]
        return [
            {
                "id": int(result["doc_id"]),
                "score": result["score"],
                "text": result["content"],
                "metadata": result.get("metadata", {})
            }
            for result in results
        ]

    def delete_document(self, doc_id: int):
        """删除文档"""
        response = requests.delete(
            f"{self.base_url}/api/v1/documents/{doc_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
```

### 工厂模式：统一创建

```python
# backend/app/services/retrieval/factory.py
from app.services.retrieval.base import BaseRetrievalService
from app.services.retrieval.qdrant_impl import QdrantRetrievalService
from app.services.retrieval.ragflow_impl import RAGFlowRetrievalService
from app.core.config import settings

class RetrievalServiceFactory:
    """检索服务工厂"""

    @staticmethod
    def create() -> BaseRetrievalService:
        """根据配置创建检索服务"""
        service_type = settings.RETRIEVAL_SERVICE_TYPE

        if service_type == "qdrant":
            return QdrantRetrievalService()
        elif service_type == "ragflow":
            return RAGFlowRetrievalService()
        else:
            raise ValueError(f"不支持的检索服务类型: {service_type}")
```

### 业务代码：使用工厂

```python
# backend/app/services/index_service.py
from app.services.retrieval.factory import RetrievalServiceFactory

class IndexService:
    """索引服务"""

    def __init__(self):
        # 通过工厂创建，具体实现由配置决定
        self.retrieval_service = RetrievalServiceFactory.create()

    def rebuild_index(self, db: Session):
        """重建索引"""
        documents = db.query(MedicalDocument).all()

        for doc in documents:
            # 解析 PDF
            text = self._extract_text(doc.file_path)

            # 索引文档（不关心具体实现）
            self.retrieval_service.index_document(
                doc_id=doc.id,
                text=text,
                metadata={
                    "file_name": doc.file_name,
                    "source_type": doc.source_type
                }
            )

    def search_similar_cases(self, query: str, top_k: int = 10):
        """检索相似病历"""
        # 检索（不关心具体实现）
        results = self.retrieval_service.search(query, top_k)
        return results
```

### 配置文件：一键切换

```env
# .env

# 当前使用 Qdrant
RETRIEVAL_SERVICE_TYPE=qdrant

# 迁移到 RAGFlow 时，只需修改这一行
# RETRIEVAL_SERVICE_TYPE=ragflow

# RAGFlow 配置（迁移时添加）
RAGFLOW_API_URL=http://localhost:8080
RAGFLOW_API_KEY=your-api-key
RAGFLOW_DATASET_ID=your-dataset-id
```

---

## 迁移步骤

### 从 Qdrant 迁移到 RAGFlow

**步骤1：实现 RAGFlow 适配器**
- 创建 `ragflow_impl.py`
- 实现 `BaseRetrievalService` 接口

**步骤2：数据迁移（可选）**
```python
# 如果需要迁移现有数据
def migrate_data():
    # 从 Qdrant 读取
    qdrant_service = QdrantRetrievalService()
    all_docs = qdrant_service.get_all_documents()

    # 写入 RAGFlow
    ragflow_service = RAGFlowRetrievalService()
    for doc in all_docs:
        ragflow_service.index_document(
            doc_id=doc["id"],
            text=doc["text"],
            metadata=doc["metadata"]
        )
```

**步骤3：修改配置**
```env
# 修改 .env
RETRIEVAL_SERVICE_TYPE=ragflow
```

**步骤4：重启服务**
```bash
python run.py
```

**完成！** 业务代码无需修改。

---

## 迁移工作量对比

### 方案A：直接使用 Qdrant（无抽象层）

**迁移工作量**：⭐⭐⭐⭐⭐（大）
- 需要修改所有调用 Qdrant 的代码
- 需要重新测试所有功能
- 风险高，容易出错

### 方案B：使用抽象层（推荐）

**迁移工作量**：⭐（小）
- 只需实现新的适配器
- 修改配置文件
- 业务代码无需修改
- 风险低，易于测试

---

## 总结

**问题：迁移到 RAGFlow 需要改吗？**

**答案**：
- **如果直接使用 Qdrant**：需要大量修改
- **如果使用抽象层设计**：几乎不需要修改，只需：
  1. 实现 RAGFlow 适配器（1-2小时）
  2. 修改配置文件（1分钟）
  3. 重启服务（1分钟）

**推荐**：
- 从一开始就使用抽象层设计
- 面向接口编程，而不是面向具体实现
- 这样可以随时切换底层技术，无需修改业务代码
