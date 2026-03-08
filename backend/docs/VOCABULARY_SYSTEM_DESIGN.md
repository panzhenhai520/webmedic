# 词库维护系统实施文档

## 概述

本文档描述了 WebMedic 系统的词库维护功能设计与实施方案。

## 一、系统架构

### 1.1 技术决策

**采用数据库表存储（而非 Python 文件）**

理由：
- ✅ 动态加载，无需重启服务
- ✅ 支持多用户并发维护
- ✅ 可记录修改历史
- ✅ 支持权限控制
- ✅ 便于导入导出

### 1.2 数据库设计

#### 表1：medical_vocabulary（医学词汇表）
```sql
CREATE TABLE medical_vocabulary (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    category VARCHAR(50) NOT NULL COMMENT '分类: body_parts/symptoms/diseases/directions',
    standard_name VARCHAR(100) NOT NULL COMMENT '标准名称',
    keywords TEXT NOT NULL COMMENT '关键词列表(JSON数组)',
    description TEXT COMMENT '描述说明',
    specialty VARCHAR(50) COMMENT '专科分类: 骨科/心内科/消化科等',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/inactive',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_standard_name (standard_name),
    INDEX idx_specialty (specialty)
);
```

**分类说明：**
- `body_parts`: 身体部位（含骨骼、关节、脏器）
- `symptoms`: 症状
- `diseases`: 疾病
- `directions`: 方位词

**专科分类示例：**
- 骨科、心内科、消化科、呼吸科、神经科等

#### 表2：icd_codes（ICD疾病编码表）
```sql
CREATE TABLE icd_codes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    icd_code VARCHAR(20) UNIQUE NOT NULL COMMENT 'ICD编码',
    icd_name_cn VARCHAR(200) NOT NULL COMMENT '中文名称',
    icd_name_en VARCHAR(200) COMMENT '英文名称',
    category VARCHAR(100) COMMENT '章节分类',
    description TEXT COMMENT '描述说明',
    keywords TEXT COMMENT '搜索关键词(JSON数组)',
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_icd_code (icd_code),
    INDEX idx_icd_name_cn (icd_name_cn)
);
```

**ICD-10 章节分类：**
- 消化系统疾病 (K00-K93)
- 循环系统疾病 (I00-I99)
- 呼吸系统疾病 (J00-J99)
- 肌肉骨骼系统疾病 (M00-M99)
- 内分泌疾病 (E00-E90)
- 等等...

#### 表3：surgery_codes（手术编码表）
```sql
CREATE TABLE surgery_codes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    surgery_code VARCHAR(20) UNIQUE NOT NULL COMMENT '手术编码',
    surgery_name VARCHAR(200) NOT NULL COMMENT '手术名称',
    category VARCHAR(100) COMMENT '手术分类',
    description TEXT COMMENT '描述说明',
    keywords TEXT COMMENT '搜索关键词(JSON数组)',
    difficulty_level VARCHAR(20) COMMENT '难度等级: 1/2/3/4级',
    status VARCHAR(20) DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_surgery_code (surgery_code),
    INDEX idx_surgery_name (surgery_name)
);
```

**手术分类：**
- 消化系统手术
- 骨科手术
- 心血管手术
- 普通外科
- 等等...

**难度等级：**
- 1级：简单手术
- 2级：中等手术
- 3级：复杂手术
- 4级：高难度手术

## 二、后端实现

### 2.1 已创建文件

1. **模型层**
   - `app/models/medical_vocabulary.py` - 医学词汇模型
   - `app/models/icd_code.py` - ICD编码模型
   - `app/models/surgery_code.py` - 手术编码模型

2. **Schema层**
   - `app/schemas/vocabulary.py` - 词库相关数据模型

3. **服务层**
   - `app/services/vocabulary_service.py` - 词库管理服务

4. **API层**
   - `app/api/endpoints/vocabulary.py` - 词库管理接口

5. **脚本**
   - `scripts/init_vocabulary_data.py` - 数据初始化脚本

### 2.2 核心功能

#### 医学词汇管理
- ✅ 列表查询（分页、筛选、搜索）
- ✅ 详情查看
- ✅ 相似词检查（基于编辑距离算法）
- ✅ 新增词汇（自动检测重复）
- ✅ 更新词汇
- ✅ 删除词汇（软删除）

#### 相似度算法
使用 Python 的 `difflib.SequenceMatcher` 计算文本相似度：
- 阈值：0.8（80%相似度）
- 检查标准名称和所有关键词
- 返回相似度最高的前N个结果

## 三、前端实现（待开发）

### 3.1 菜单结构

```
顶部导航栏
├── 工作站
├── 会话历史
├── 病历管理
└── 系统维护 ⭐ 新增
    ├── 医学词库维护
    ├── ICD编码维护
    └── 手术编码维护
```

### 3.2 页面设计

#### 医学词库维护页面

**布局：**
```
┌─────────────────────────────────────────────────────┐
│ 医学词库维护                                          │
├─────────────────────────────────────────────────────┤
│ [分类筛选▼] [专科筛选▼] [搜索框] [+ 新增词汇]        │
├─────────────────────────────────────────────────────┤
│ 标准名称 │ 分类 │ 专科 │ 关键词 │ 状态 │ 操作        │
├─────────────────────────────────────────────────────┤
│ 肱骨     │ 身体 │ 骨科 │ 肱骨   │ 启用 │ [编辑][删除]│
│ 颈椎     │ 身体 │ 骨科 │ 颈椎.. │ 启用 │ [编辑][删除]│
│ ...                                                  │
├─────────────────────────────────────────────────────┤
│ 共 121 条 │ 第 1/7 页 │ [上一页] [下一页]           │
└─────────────────────────────────────────────────────┘
```

**新增/编辑对话框：**
```
┌─────────────────────────────────────┐
│ 新增医学词汇                         │
├─────────────────────────────────────┤
│ 分类：      [身体部位 ▼]             │
│ 专科：      [骨科 ▼]                 │
│ 标准名称：  [_____________]          │
│             ⚠️ 存在相似词：肱骨       │
│ 关键词：    [肱骨] [+添加]           │
│             [肱骨] [×]               │
│ 描述：      [_______________]        │
│                                      │
│         [取消]  [保存]               │
└─────────────────────────────────────┘
```

**关键功能：**
1. 实时相似词检查（输入标准名称时）
2. 关键词标签化管理
3. 分类和专科级联选择
4. 批量导入功能（Excel/CSV）
5. 批量导出功能

#### ICD编码维护页面

类似设计，字段包括：
- ICD编码
- 中文名称
- 英文名称
- 章节分类
- 关键词
- 描述

#### 手术编码维护页面

类似设计，字段包括：
- 手术编码
- 手术名称
- 手术分类
- 难度等级
- 关键词
- 描述

### 3.3 前端技术栈

- Vue 3 + Composition API
- Element Plus（UI组件库）
- Axios（HTTP客户端）

### 3.4 需要创建的文件

1. **API客户端**
   - `frontend/src/api/vocabulary.js`

2. **页面组件**
   - `frontend/src/views/VocabularyManagement.vue`
   - `frontend/src/views/ICDManagement.vue`
   - `frontend/src/views/SurgeryManagement.vue`

3. **路由配置**
   - 更新 `frontend/src/router/index.js`

4. **导航菜单**
   - 更新 `frontend/src/views/DoctorWorkbench.vue`

## 四、数据初始化

### 4.1 运行初始化脚本

```bash
cd D:\webmedic\backend

# 创建数据库表（需要先运行数据库迁移）
venv\Scripts\python.exe scripts\create_tables.py

# 初始化词库数据
venv\Scripts\python.exe scripts\init_vocabulary_data.py
```

### 4.2 初始数据统计

- 医学词汇：121条
  - 身体部位：74条（含骨科专业词汇）
  - 症状：16条
  - 疾病：22条
  - 方位词：9条

- ICD编码：15条（示例数据）
  - 消化系统：5条
  - 循环系统：2条
  - 呼吸系统：2条
  - 骨骼肌肉：3条
  - 内分泌：2条

- 手术编码：12条（示例数据）
  - 消化系统手术：4条
  - 骨科手术：4条
  - 心血管手术：2条
  - 普通外科：2条

## 五、Mock模式集成

### 5.1 动态加载词库

修改 `app/utils/medical_vocabulary.py`，从数据库动态加载：

```python
def load_vocabulary_from_db():
    """从数据库加载词库"""
    db = SessionLocal()
    try:
        vocabs = db.query(MedicalVocabulary).filter(
            MedicalVocabulary.status == "active"
        ).all()

        # 转换为字典格式
        body_parts = {}
        symptoms = {}
        diseases = {}
        directions = {}

        for vocab in vocabs:
            keywords = json.loads(vocab.keywords)
            if vocab.category == "body_parts":
                body_parts[vocab.standard_name] = keywords
            elif vocab.category == "symptoms":
                symptoms[vocab.standard_name] = keywords
            # ...

        return body_parts, symptoms, diseases, directions
    finally:
        db.close()
```

### 5.2 缓存机制

为避免每次抽取都查询数据库，实现缓存：

```python
from functools import lru_cache
from datetime import datetime, timedelta

_cache_time = None
_cache_data = None

def get_vocabulary_cached():
    """获取缓存的词库（5分钟过期）"""
    global _cache_time, _cache_data

    now = datetime.now()
    if _cache_data is None or (now - _cache_time) > timedelta(minutes=5):
        _cache_data = load_vocabulary_from_db()
        _cache_time = now

    return _cache_data
```

## 六、实施步骤

### 阶段1：数据库和后端（已完成）
- ✅ 创建数据库表模型
- ✅ 创建Schema定义
- ✅ 实现服务层
- ✅ 实现API接口
- ✅ 注册路由
- ✅ 创建初始化脚本

### 阶段2：数据初始化（待执行）
- ⏳ 运行数据库迁移
- ⏳ 执行数据初始化脚本
- ⏳ 验证数据正确性

### 阶段3：前端开发（待开发）
- ⏳ 创建API客户端
- ⏳ 开发词库维护页面
- ⏳ 开发ICD维护页面
- ⏳ 开发手术编码维护页面
- ⏳ 更新导航菜单
- ⏳ 测试功能

### 阶段4：Mock模式集成（待开发）
- ⏳ 修改Mock抽取器从数据库加载
- ⏳ 实现缓存机制
- ⏳ 测试抽取功能

## 七、API接口文档

### 7.1 医学词汇

#### 获取词汇列表
```
POST /api/v1/vocabulary/vocabulary/list
Content-Type: application/json

{
  "page": 1,
  "page_size": 20,
  "category": "body_parts",  // 可选
  "specialty": "骨科",        // 可选
  "keyword": "肱骨",          // 可选
  "status": "active"
}
```

#### 检查相似词
```
POST /api/v1/vocabulary/vocabulary/check-similar
Content-Type: application/json

{
  "text": "肱骨",
  "category": "body_parts"  // 可选
}
```

#### 新增词汇
```
POST /api/v1/vocabulary/vocabulary
Content-Type: application/json

{
  "category": "body_parts",
  "standard_name": "肱骨",
  "keywords": ["肱骨"],
  "description": "上臂骨",
  "specialty": "骨科"
}
```

#### 更新词汇
```
PUT /api/v1/vocabulary/vocabulary/{vocab_id}
Content-Type: application/json

{
  "keywords": ["肱骨", "上臂骨"],
  "description": "上臂的长骨"
}
```

#### 删除词汇
```
DELETE /api/v1/vocabulary/vocabulary/{vocab_id}
```

### 7.2 ICD编码和手术编码

类似的CRUD接口（待完整实现）

## 八、注意事项

1. **权限控制**：后续可添加管理员权限验证
2. **审计日志**：记录所有修改操作
3. **数据备份**：定期备份词库数据
4. **版本管理**：考虑实现词库版本控制
5. **批量操作**：支持Excel导入导出

## 九、扩展建议

1. **AI辅助**：使用LLM自动生成关键词
2. **协同编辑**：多人同时编辑时的冲突处理
3. **审核流程**：新增词汇需要审核后才生效
4. **统计分析**：词库使用频率统计
5. **智能推荐**：根据使用情况推荐相关词汇
