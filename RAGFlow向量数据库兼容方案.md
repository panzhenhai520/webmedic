# RAGFlow 向量数据库兼容方案

## RAGFlow 架构分析

RAGFlow 是一个开源的 RAG（检索增强生成）系统，支持多种向量数据库：

### RAGFlow 支持的向量数据库

1. **Elasticsearch**（默认）
   - RAGFlow 默认使用 Elasticsearch 作为向量数据库
   - 支持全文检索和向量检索
   - 需要安装 Elasticsearch 服务

2. **Milvus**（可选）
   - 专业的向量数据库
   - 性能更好
   - 需要单独配置

3. **Qdrant**（可选）
   - 轻量级向量数据库
   - 易于部署
   - 与我们推荐的方案一致

---

## 兼容方案

### 方案1：直接使用 RAGFlow 的向量数据库（推荐）

如果您已经部署了 RAGFlow，可以直接复用其向量数据库。

#### 1.1 如果 RAGFlow 使用 Elasticsearch

**优点**：
- 无需额外部署
- 复用现有基础设施
- Elasticsearch 功能强大

**实现方式**：
```python
# backend/app/services/vector_db_service.py
from elasticsearch import Elasticsearch

class ElasticsearchVectorDB:
    """使用 Elasticsearch 作为向量数据库"""

    def __init__(self):
        # 连接到 RAGFlow 的 Elasticsearch
        self.client = Elasticsearch(
            hosts=["http://localhost:9200"],
            # 如果 RAGFlow 有认证，添加认证信息
            # basic_auth=("username", "password")
        )
        self.index_name = "medical_records"
        self._ensure_index()

    def _ensure_index(self):
        """创建索引（如果不存在）"""
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(
                index=self.index_name,
                body={
                    "mappings": {
                        "properties": {
                            "text": {"type": "text"},
                            "vector": {
                                "type": "dense_vector",
                                "dims": 1024,  # BGE-M3 维度
                                "index": True,
                                "similarity": "cosine"
                            },
                            "metadata": {"type": "object"}
                        }
                    }
                }
            )

    def index_document(self, doc_id: int, text: str, vector: list, metadata: dict):
        """索引文档"""
        self.client.index(
            index=self.index_name,
            id=doc_id,
            body={
                "text": text,
                "vector": vector,
                "metadata": metadata
            }
        )

    def search(self, query_vector: list, limit: int = 10, score_threshold: float = 0.7):
        """检索相似文档"""
        response = self.client.search(
            index=self.index_name,
            body={
                "knn": {
                    "field": "vector",
                    "query_vector": query_vector,
                    "k": limit,
                    "num_candidates": limit * 2
                },
                "min_score": score_threshold
            }
        )

        results = []
        for hit in response['hits']['hits']:
            results.append({
                'id': int(hit['_id']),
                'score': hit['_score'],
                'payload': hit['_source']['metadata']
            })

        return results
```

**配置**：
```env
# .env
VECTOR_DB_TYPE=elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USER=
ELASTICSEARCH_PASSWORD=
```

#### 1.2 如果 RAGFlow 使用 Milvus

**优点**：
- 专业向量数据库
- 性能优秀
- 功能丰富

**实现方式**：
```python
# backend/app/services/vector_db_service.py
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

class MilvusVectorDB:
    """使用 Milvus 作为向量数据库"""

    def __init__(self):
        # 连接到 RAGFlow 的 Milvus
        connections.connect(
            alias="default",
            host="localhost",
            port="19530"
        )
        self.collection_name = "medical_records"
        self._ensure_collection()

    def _ensure_collection(self):
        """创建集合（如果不存在）"""
        from pymilvus import utility

        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            ]
            schema = CollectionSchema(fields, description="Medical records")
            collection = Collection(self.collection_name, schema)

            # 创建索引
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 128}
            }
            collection.create_index("vector", index_params)

        self.collection = Collection(self.collection_name)
        self.collection.load()

    def index_document(self, doc_id: int, text: str, vector: list, metadata: dict):
        """索引文档"""
        self.collection.insert([
            [doc_id],
            [vector],
            [text]
        ])

    def search(self, query_vector: list, limit: int = 10, score_threshold: float = 0.7):
        """检索相似文档"""
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}

        results = self.collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=limit,
            expr=None
        )

        formatted_results = []
        for hits in results:
            for hit in hits:
                if hit.score >= score_threshold:
                    formatted_results.append({
                        'id': hit.id,
                        'score': hit.score,
                        'payload': {}
                    })

        return formatted_results
```

**配置**：
```env
# .env
VECTOR_DB_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

#### 1.3 如果 RAGFlow 使用 Qdrant

**最佳情况**：
- 与我们推荐的方案完全一致
- 直接复用即可

**实现方式**：
```python
# 直接使用之前提供的 Qdrant 实现
# 只需要连接到 RAGFlow 的 Qdrant 实例
client = QdrantClient(
    host="localhost",  # RAGFlow 的 Qdrant 地址
    port=6333
)
```

---

### 方案2：独立部署（推荐）

**为什么推荐独立部署**：
1. **数据隔离**：医疗数据与 RAGFlow 数据分离
2. **配置独立**：可以针对医疗场景优化
3. **维护简单**：不影响 RAGFlow 的使用
4. **灵活性高**：可以随时切换向量数据库

**实现方式**：
- 使用 Qdrant 内嵌模式（无需安装）
- 或使用独立的 Docker 容器

```python
# 独立的 Qdrant 实例
client = QdrantClient(path="./webmedic_qdrant_data")
```

---

### 方案3：统一向量数据库接口（最灵活）

**设计思路**：
- 定义统一的向量数据库接口
- 支持多种向量数据库实现
- 可以根据配置切换

**实现方式**：
```python
# backend/app/services/vector_db/base.py
from abc import ABC, abstractmethod

class BaseVectorDB(ABC):
    """向量数据库基类"""

    @abstractmethod
    def index_document(self, doc_id: int, text: str, vector: list, metadata: dict):
        pass

    @abstractmethod
    def search(self, query_vector: list, limit: int, score_threshold: float):
        pass

# backend/app/services/vector_db/qdrant_impl.py
class QdrantVectorDB(BaseVectorDB):
    """Qdrant 实现"""
    # ... 实现 ...

# backend/app/services/vector_db/elasticsearch_impl.py
class ElasticsearchVectorDB(BaseVectorDB):
    """Elasticsearch 实现"""
    # ... 实现 ...

# backend/app/services/vector_db/milvus_impl.py
class MilvusVectorDB(BaseVectorDB):
    """Milvus 实现"""
    # ... 实现 ...

# backend/app/services/vector_db/factory.py
class VectorDBFactory:
    """向量数据库工厂"""

    @staticmethod
    def create(db_type: str) -> BaseVectorDB:
        if db_type == "qdrant":
            return QdrantVectorDB()
        elif db_type == "elasticsearch":
            return ElasticsearchVectorDB()
        elif db_type == "milvus":
            return MilvusVectorDB()
        else:
            raise ValueError(f"不支持的向量数据库类型: {db_type}")
```

**配置**：
```env
# .env
VECTOR_DB_TYPE=qdrant  # 或 elasticsearch, milvus

# Qdrant 配置
QDRANT_MODE=embedded  # embedded, server, cloud
QDRANT_PATH=./webmedic_qdrant_data
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Elasticsearch 配置（如果使用 RAGFlow 的 ES）
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200

# Milvus 配置（如果使用 RAGFlow 的 Milvus）
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

---

## 推荐方案总结

### 如果您已经部署了 RAGFlow

**推荐方案**：
1. **查看 RAGFlow 使用的向量数据库**
   ```bash
   # 查看 RAGFlow 的配置文件
   cat ragflow/docker-compose.yml
   # 或
   cat ragflow/conf/service_conf.yaml
   ```

2. **根据 RAGFlow 的向量数据库选择**：
   - 如果是 **Elasticsearch**：实现 Elasticsearch 适配器，复用 RAGFlow 的 ES
   - 如果是 **Milvus**：实现 Milvus 适配器，复用 RAGFlow 的 Milvus
   - 如果是 **Qdrant**：直接使用，完美兼容

### 如果您还没有部署 RAGFlow

**推荐方案**：
- 使用 **Qdrant 内嵌模式**
- 无需安装任何服务
- 开箱即用

```python
# 一行代码，无需安装
client = QdrantClient(path="./webmedic_qdrant_data")
```

---

## 性能对比

| 向量数据库 | 性能 | 易用性 | 功能 | 与 RAGFlow 兼容性 |
|-----------|------|--------|------|-------------------|
| Qdrant | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Elasticsearch | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Milvus | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 下一步行动

1. **确认 RAGFlow 的向量数据库类型**
   - 查看 RAGFlow 配置文件
   - 或告诉我您的 RAGFlow 配置

2. **选择实施方案**
   - 复用 RAGFlow 的向量数据库
   - 或独立部署 Qdrant（推荐）

3. **开始实现**
   - 我可以根据您的选择提供具体实现代码

请告诉我：
1. 您是否已经部署了 RAGFlow？
2. 如果已部署，RAGFlow 使用的是哪种向量数据库？
3. 您倾向于复用 RAGFlow 的数据库，还是独立部署？
