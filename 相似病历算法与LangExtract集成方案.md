# 相似病历算法设计建议 & LangExtract 集成方案

## 第一部分：相似病历算法设计

### 当前实现分析

**现状**：
- 使用 Mock 实现，随机选择文档
- 生成随机相似度分数（0.75-0.95）
- 使用固定的原因模板

**问题**：
- 与实际病历内容无关
- 无法真正找到相似病历
- 无法用于临床决策支持

---

### 推荐方案：基于向量的语义相似度检索

#### 方案架构

```
病历文档 → PDF解析 → 文本提取 → Embedding → 向量数据库
                                              ↓
当前病历 → 结构化信息 → 查询文本 → Embedding → 相似度检索 → Top-K 结果
```

#### 核心组件

**1. Embedding 模型**

推荐使用中文医疗领域优化的模型：

| 模型 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **BGE-M3** | 多语言、效果好、开源 | 模型较大（2.3GB） | ⭐⭐⭐⭐⭐ |
| **M3E-base** | 中文优化、轻量 | 效果略逊 | ⭐⭐⭐⭐ |
| **OpenAI text-embedding-3** | 效果好、API调用 | 需要付费、网络依赖 | ⭐⭐⭐⭐ |
| **BGE-large-zh** | 中文效果好 | 模型较大（1.3GB） | ⭐⭐⭐⭐ |

**推荐：BGE-M3**
- 多语言支持（中英文混合病历）
- 效果优秀（MTEB 排行榜前列）
- 开源免费
- 支持本地部署

**2. 向量数据库**

| 数据库 | 优点 | 缺点 | 推荐度 |
|--------|------|------|--------|
| **Qdrant** | 轻量、易部署、Python友好 | 功能相对简单 | ⭐⭐⭐⭐⭐ |
| **Milvus** | 功能强大、性能好 | 部署复杂、资源占用大 | ⭐⭐⭐⭐ |
| **Chroma** | 极简、内嵌式 | 性能一般 | ⭐⭐⭐ |
| **FAISS** | 性能极好、Meta开源 | 需要自己管理数据 | ⭐⭐⭐⭐ |

**推荐：Qdrant**
- 轻量级，易于集成
- Docker 一键部署
- Python SDK 友好
- 支持过滤和混合检索

**3. 检索策略**

**基础检索**：
```python
# 1. 构建查询文本
query_text = f"""
主诉：{structured_record.chief_complaint}
现病史：{structured_record.present_illness}
初步诊断：{structured_record.preliminary_diagnosis}
"""

# 2. 生成查询向量
query_vector = embedding_model.encode(query_text)

# 3. 向量检索
results = vector_db.search(
    collection_name="medical_records",
    query_vector=query_vector,
    limit=10,
    score_threshold=0.7
)
```

**混合检索**（推荐）：
```python
# 结合语义相似度 + 关键词匹配
results = vector_db.search(
    collection_name="medical_records",
    query_vector=query_vector,
    query_filter={
        "must": [
            {"key": "diagnosis", "match": {"value": "颈椎病"}}
        ]
    },
    limit=10
)
```

**重排序**（可选）：
```python
# 使用 Rerank 模型进行精排
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('BAAI/bge-reranker-base')
scores = reranker.predict([
    (query_text, doc.content) for doc in results
])
```

---

### 实施步骤

#### 阶段1：基础实现（1-2天）

**1. 安装依赖**

```bash
# Embedding 模型
pip install sentence-transformers

# 向量数据库
pip install qdrant-client

# PDF 解析（已有）
pip install pymupdf
```

**2. 启动 Qdrant**

```bash
# Docker 方式（推荐）
docker run -p 6333:6333 qdrant/qdrant

# 或使用内嵌模式（开发测试）
# 无需额外安装，直接使用 Python SDK
```

**3. 创建 Embedding 服务**

```python
# backend/app/services/embedding_service.py
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """文本向量化服务"""

    def __init__(self):
        # 使用 BGE-M3 模型
        self.model = SentenceTransformer('BAAI/bge-m3')
        logger.info("Embedding 模型加载成功")

    def encode(self, text: str) -> list:
        """将文本转换为向量"""
        vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    def encode_batch(self, texts: list) -> list:
        """批量转换"""
        vectors = self.model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()

# 全局实例
_embedding_service = None

def get_embedding_service():
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
```

**4. 创建向量数据库服务**

```python
# backend/app/services/vector_db_service.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging

logger = logging.getLogger(__name__)

class VectorDBService:
    """向量数据库服务"""

    def __init__(self):
        # 使用内嵌模式（开发）或连接服务器（生产）
        self.client = QdrantClient(path="./qdrant_data")  # 内嵌模式
        # self.client = QdrantClient(host="localhost", port=6333)  # 服务器模式

        self.collection_name = "medical_records"
        self._ensure_collection()

    def _ensure_collection(self):
        """确保集合存在"""
        collections = self.client.get_collections().collections
        if self.collection_name not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1024,  # BGE-M3 向量维度
                    distance=Distance.COSINE
                )
            )
            logger.info(f"创建向量集合: {self.collection_name}")

    def index_document(self, doc_id: int, text: str, vector: list, metadata: dict):
        """索引文档"""
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=doc_id,
                    vector=vector,
                    payload={
                        "text": text,
                        **metadata
                    }
                )
            ]
        )

    def search(self, query_vector: list, limit: int = 10, score_threshold: float = 0.7):
        """检索相似文档"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold
        )
        return results

# 全局实例
_vector_db_service = None

def get_vector_db_service():
    global _vector_db_service
    if _vector_db_service is None:
        _vector_db_service = VectorDBService()
    return _vector_db_service
```

**5. 修改 IndexService**

```python
# backend/app/services/index_service.py
from app.services.embedding_service import get_embedding_service
from app.services.vector_db_service import get_vector_db_service
from app.services.document_service import DocumentService
import pymupdf  # PyMuPDF

class IndexService:

    @staticmethod
    def rebuild_index(db: Session) -> Tuple[int, int]:
        """重建索引 - 真实实现"""
        embedding_service = get_embedding_service()
        vector_db = get_vector_db_service()

        # 获取所有待索引的文档
        documents = db.query(MedicalDocument).filter(
            MedicalDocument.index_status.in_(["pending", "failed"])
        ).all()

        indexed_count = 0

        for doc in documents:
            try:
                # 1. 解析 PDF
                pdf_doc = pymupdf.open(doc.file_path)
                text = ""
                for page in pdf_doc:
                    text += page.get_text()
                pdf_doc.close()

                # 2. 生成向量
                vector = embedding_service.encode(text)

                # 3. 索引到向量数据库
                vector_db.index_document(
                    doc_id=doc.id,
                    text=text,
                    vector=vector,
                    metadata={
                        "file_name": doc.file_name,
                        "source_type": doc.source_type
                    }
                )

                # 4. 更新状态
                doc.parse_status = "done"
                doc.index_status = "done"
                indexed_count += 1

            except Exception as e:
                logger.error(f"索引文档失败 {doc.id}: {e}")
                doc.index_status = "failed"

        db.commit()
        return len(documents), indexed_count

    @staticmethod
    def search_similar_cases(
        db: Session,
        session_id: int,
        top_k: int = 3
    ) -> List[SimilarCaseMatch]:
        """检索相似病历 - 真实实现"""
        embedding_service = get_embedding_service()
        vector_db = get_vector_db_service()

        # 获取结构化记录
        structured_record = db.query(StructuredRecord).filter(
            StructuredRecord.session_id == session_id
        ).order_by(StructuredRecord.created_at.desc()).first()

        if not structured_record:
            raise ValueError("没有结构化记录")

        # 构建查询文本
        query_text = f"""
        主诉：{structured_record.chief_complaint}
        现病史：{structured_record.present_illness}
        初步诊断：{structured_record.preliminary_diagnosis}
        """

        # 生成查询向量
        query_vector = embedding_service.encode(query_text)

        # 向量检索
        results = vector_db.search(
            query_vector=query_vector,
            limit=top_k * 2,  # 多检索一些，后续可以过滤
            score_threshold=0.6
        )

        # 删除旧匹配记录
        db.query(SimilarCaseMatch).filter(
            SimilarCaseMatch.session_id == session_id
        ).delete()

        # 创建新匹配记录
        matches = []
        for rank, result in enumerate(results[:top_k], start=1):
            doc = db.query(MedicalDocument).filter(
                MedicalDocument.id == result.id
            ).first()

            if doc:
                match = SimilarCaseMatch(
                    session_id=session_id,
                    document_id=doc.id,
                    score=result.score,
                    reason_text=f"语义相似度: {result.score:.2%}",
                    rank_no=rank
                )
                db.add(match)
                matches.append(match)

        db.commit()
        return matches
```

#### 阶段2：优化改进（3-5天）

**1. 添加混合检索**
- 结合语义相似度和关键词匹配
- 支持按诊断、症状过滤

**2. 添加 Rerank**
- 使用 BGE-reranker 进行重排序
- 提高 Top-K 结果的准确性

**3. 添加缓存**
- 缓存常见查询的结果
- 减少重复计算

**4. 性能优化**
- 批量索引
- 异步处理
- 增量更新

---

### 配置建议

```env
# .env 文件
# 向量检索配置
VECTOR_DB_TYPE=qdrant  # qdrant, milvus, faiss
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=6333
VECTOR_DB_PATH=./qdrant_data  # 内嵌模式路径

# Embedding 模型
EMBEDDING_MODEL=BAAI/bge-m3  # 或 BAAI/bge-large-zh
EMBEDDING_DEVICE=cpu  # cpu 或 cuda

# 检索参数
SEARCH_TOP_K=10
SEARCH_SCORE_THRESHOLD=0.6
```

---

## 第二部分：LangExtract 集成方案

### LangExtract 简介

LangExtract 是一个结构化信息抽取工具，特点：
- 基于 LangChain
- 支持多种 LLM
- 灵活的 Schema 定义
- 易于集成

### 集成架构

```
前端选择抽取方式
    ↓
后端接收参数
    ↓
根据选择调用不同的抽取器
    ├─ Instructor + DeepSeek（当前）
    └─ LangExtract + 可选 LLM（新增）
    ↓
返回统一格式的结果
```

### 实施步骤

#### 1. 安装依赖

```bash
pip install langchain langchain-openai langchain-community
```

#### 2. 创建抽取器接口

```python
# backend/app/services/extractors/base_extractor.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseExtractor(ABC):
    """抽取器基类"""

    @abstractmethod
    def extract(self, dialogue_text: str, patient_info: dict) -> Dict[str, Any]:
        """
        抽取结构化信息

        Args:
            dialogue_text: 对话文本
            patient_info: 患者信息

        Returns:
            结构化数据字典
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """获取抽取器名称"""
        pass
```

#### 3. 实现 Instructor 抽取器

```python
# backend/app/services/extractors/instructor_extractor.py
from app.services.extractors.base_extractor import BaseExtractor
from app.services.llm_service import get_llm_service

class InstructorExtractor(BaseExtractor):
    """基于 Instructor 的抽取器（当前实现）"""

    def extract(self, dialogue_text: str, patient_info: dict) -> Dict[str, Any]:
        llm_service = get_llm_service()

        # 构建 prompt
        prompt = self._build_prompt(dialogue_text, patient_info)

        # 调用 LLM
        result = llm_service.generate_json(prompt)

        return result

    def get_name(self) -> str:
        return "Instructor + DeepSeek"

    def _build_prompt(self, dialogue_text: str, patient_info: dict) -> str:
        # 当前的 prompt 构建逻辑
        pass
```

#### 4. 实现 LangExtract 抽取器

```python
# backend/app/services/extractors/langextract_extractor.py
from langchain.chains import create_extraction_chain
from langchain_openai import ChatOpenAI
from app.services.extractors.base_extractor import BaseExtractor

class LangExtractExtractor(BaseExtractor):
    """基于 LangExtract 的抽取器"""

    def __init__(self, llm_provider: str = "deepseek"):
        self.llm_provider = llm_provider
        self._init_llm()

    def _init_llm(self):
        """初始化 LLM"""
        if self.llm_provider == "deepseek":
            self.llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL
            )
        elif self.llm_provider == "openai":
            self.llm = ChatOpenAI(
                model="gpt-4",
                api_key=settings.OPENAI_API_KEY
            )

    def extract(self, dialogue_text: str, patient_info: dict) -> Dict[str, Any]:
        # 定义抽取 Schema
        schema = {
            "properties": {
                "chief_complaint": {"type": "string", "description": "主诉"},
                "present_illness": {"type": "string", "description": "现病史"},
                "past_history": {"type": "string", "description": "既往史"},
                "allergy_history": {"type": "string", "description": "过敏史"},
                "physical_exam": {"type": "string", "description": "体格检查"},
                "preliminary_diagnosis": {"type": "string", "description": "初步诊断"},
                "suggested_exams": {"type": "string", "description": "建议检查"},
                "warning_flags": {"type": "string", "description": "风险标记"}
            },
            "required": ["chief_complaint", "present_illness"]
        }

        # 创建抽取链
        chain = create_extraction_chain(schema, self.llm)

        # 执行抽取
        result = chain.run(dialogue_text)

        # 格式化结果
        if result and len(result) > 0:
            return result[0]
        else:
            return self._empty_result()

    def get_name(self) -> str:
        return f"LangExtract + {self.llm_provider}"

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "chief_complaint": "未提及",
            "present_illness": "未提及",
            "past_history": "未提及",
            "allergy_history": "未提及",
            "physical_exam": "未提及",
            "preliminary_diagnosis": "未提及",
            "suggested_exams": "未提及",
            "warning_flags": "未提及"
        }
```

#### 5. 创建抽取器工厂

```python
# backend/app/services/extractors/extractor_factory.py
from app.services.extractors.base_extractor import BaseExtractor
from app.services.extractors.instructor_extractor import InstructorExtractor
from app.services.extractors.langextract_extractor import LangExtractExtractor

class ExtractorFactory:
    """抽取器工厂"""

    @staticmethod
    def create(extractor_type: str, **kwargs) -> BaseExtractor:
        """
        创建抽取器

        Args:
            extractor_type: 抽取器类型
                - "instructor": Instructor + DeepSeek
                - "langextract_deepseek": LangExtract + DeepSeek
                - "langextract_openai": LangExtract + OpenAI

        Returns:
            抽取器实例
        """
        if extractor_type == "instructor":
            return InstructorExtractor()
        elif extractor_type == "langextract_deepseek":
            return LangExtractExtractor(llm_provider="deepseek")
        elif extractor_type == "langextract_openai":
            return LangExtractExtractor(llm_provider="openai")
        else:
            raise ValueError(f"未知的抽取器类型: {extractor_type}")

    @staticmethod
    def list_extractors() -> list:
        """列出所有可用的抽取器"""
        return [
            {
                "type": "instructor",
                "name": "Instructor + DeepSeek",
                "description": "当前使用的抽取方式"
            },
            {
                "type": "langextract_deepseek",
                "name": "LangExtract + DeepSeek",
                "description": "使用 LangChain 抽取，DeepSeek 模型"
            },
            {
                "type": "langextract_openai",
                "name": "LangExtract + OpenAI GPT-4",
                "description": "使用 LangChain 抽取，OpenAI GPT-4 模型"
            }
        ]
```

#### 6. 修改 ExtractService

```python
# backend/app/services/extract_service.py
from app.services.extractors.extractor_factory import ExtractorFactory

class ExtractService:

    @staticmethod
    def extract_structured_record(
        db: Session,
        session_id: int,
        extractor_type: str = "instructor"  # 新增参数
    ) -> StructuredRecord:
        """
        从会话对话中抽取结构化病历

        Args:
            db: 数据库会话
            session_id: 会话ID
            extractor_type: 抽取器类型
        """
        # ... 获取会话、患者、对话记录 ...

        # 创建抽取器
        extractor = ExtractorFactory.create(extractor_type)

        # 执行抽取
        result_json = extractor.extract(
            dialogue_text=dialogue_text,
            patient_info={
                "name": patient.patient_name,
                "gender": patient.gender,
                "age": patient.age
            }
        )

        # ... 保存到数据库 ...
```

#### 7. 修改 API 端点

```python
# backend/app/api/endpoints/extract.py
@router.post("/{session_id}", response_model=dict)
async def extract_structured_record(
    session_id: int,
    extractor_type: str = "instructor",  # 新增参数
    db: Session = Depends(get_db)
):
    """
    根据当前会话重新抽取结构化病历

    Args:
        session_id: 会话ID
        extractor_type: 抽取器类型（instructor, langextract_deepseek, langextract_openai）
    """
    try:
        record = ExtractService.extract_structured_record(
            db=db,
            session_id=session_id,
            extractor_type=extractor_type
        )
        # ... 返回结果 ...
```

#### 8. 前端添加选择界面

```vue
<!-- frontend/src/components/workbench/ControlPanel.vue -->
<template>
  <div class="control-panel">
    <!-- 抽取方式选择 -->
    <el-card class="extractor-selector">
      <template #header>
        <span>抽取方式</span>
      </template>
      <el-select v-model="selectedExtractor" placeholder="选择抽取方式">
        <el-option
          v-for="extractor in extractors"
          :key="extractor.type"
          :label="extractor.name"
          :value="extractor.type"
        >
          <span>{{ extractor.name }}</span>
          <span class="extractor-desc">{{ extractor.description }}</span>
        </el-option>
      </el-select>
    </el-card>

    <!-- 其他控制按钮 -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getExtractors } from '@/api/extract'

const selectedExtractor = ref('instructor')
const extractors = ref([])

// 加载可用的抽取器列表
onMounted(async () => {
  const response = await getExtractors()
  extractors.value = response.data.extractors
})

// 抽取时使用选择的抽取器
const handleExtract = async () => {
  const response = await extractStructuredRecord(
    sessionId,
    selectedExtractor.value  // 传递抽取器类型
  )
  // ...
}
</script>
```

#### 9. 添加对比功能

```vue
<!-- frontend/src/components/workbench/ExtractorComparison.vue -->
<template>
  <el-dialog v-model="visible" title="抽取结果对比" width="90%">
    <el-row :gutter="20">
      <el-col :span="12">
        <h3>Instructor + DeepSeek</h3>
        <div class="result-panel">
          <!-- 显示结果1 -->
        </div>
      </el-col>
      <el-col :span="12">
        <h3>LangExtract + DeepSeek</h3>
        <div class="result-panel">
          <!-- 显示结果2 -->
        </div>
      </el-col>
    </el-row>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button type="primary" @click="runComparison">运行对比</el-button>
    </template>
  </el-dialog>
</template>
```

---

### 配置建议

```env
# .env 文件
# 抽取器配置
DEFAULT_EXTRACTOR=instructor  # instructor, langextract_deepseek, langextract_openai

# LangChain 配置
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
```

---

## 总结

### 相似病历算法

**推荐方案**：BGE-M3 + Qdrant
- **优点**：效果好、易部署、成本低
- **实施周期**：1-2天基础实现，3-5天优化
- **成本**：开源免费，仅需服务器资源

### LangExtract 集成

**推荐方案**：抽取器工厂模式
- **优点**：灵活切换、易于对比、可扩展
- **实施周期**：2-3天
- **成本**：与当前相同（使用相同的 LLM API）

### 下一步行动

1. **优先级1**：实现相似病历算法（影响临床价值）
2. **优先级2**：集成 LangExtract（提供对比选择）
3. **优先级3**：添加对比分析功能（评估效果）

需要我开始实现哪个部分？
