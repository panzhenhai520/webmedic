# WebMedic 项目开发技术细节文档

## 1. 项目定位

本项目是一个 **语音驱动门诊电子病历生成 Demo 系统**，用于演示以下完整链路：

1. 医生工作站页面开始问诊
2. 浏览器采集语音片段
3. 后端调用 Dolphin 进行语音识别（ASR）
4. 将医患对话实时显示在界面中
5. 使用 Instructor + DeepSeek 将对话抽取为结构化门诊病历字段
6. 对本地 PDF 病历样本建立索引
7. 用 PageIndex 检索相似病历
8. 根据当前对话和相似病历生成病历草稿
9. 基于当前症状、检查和候选用药生成“风险提示 + 追问问题 + 建议检查”
10. 由医生人工确认后形成最终病历内容

**注意：**
本项目定位为 Demo，不可宣传为临床正式诊疗系统，不可把 LLM 输出作为最终医学结论。

---

## 2. 项目目标

### 2.1 第一阶段目标（必须完成）

完成一个可以运行和演示的原型系统，至少具备：

* 固定医生和固定患者信息展示
* 医生工作站页面
* “开始问诊”按钮
* “医生说话 / 患者说话”按钮
* 音频上传与转写
* 实时显示医患对话
* 结构化抽取当前问诊内容
* 检索最相似病历
* 生成病历草稿
* 展示追问问题和风险提示

### 2.2 第二阶段目标（增强）

* 支持多份 PDF 病历上传
* 支持索引重建
* 支持会话保存和回放
* 支持对结构化结果人工修正
* 支持“使用相同检查治疗方案”按钮
* 支持提示来源说明和日志记录

---

## 3. 固定业务设定

### 3.1 固定医生

* 医生姓名：Doctor Panython

### 3.2 固定患者

* 姓名：张三
* 性别：男
* 年龄：29 岁

### 3.3 病历来源目录

本地存在一个病历样本目录，目录中包含多个 PDF 病历文件。

建议路径：

```text
D:\webmedic\medical_records\
```

### 3.4 技术约束

* 前端：Vue 3
* 后端：Python
* 数据库：MySQL
* 参考已有项目：`D:\Code\ExchangeNew`
* 可以参考其数据库连接方式、项目结构风格、配置方式
* 但本项目必须独立目录开发，不要直接污染原项目

---

## 4. 推荐项目目录结构

建议在本地建立以下目录：

```text
D:\webmedic\
├─ backend\
│  ├─ app\
│  │  ├─ api\
│  │  ├─ core\
│  │  ├─ db\
│  │  ├─ models\
│  │  ├─ schemas\
│  │  ├─ services\
│  │  ├─ utils\
│  │  └─ prompts\
│  ├─ medical_records\
│  ├─ uploads\
│  ├─ logs\
│  ├─ tests\
│  ├─ requirements.txt
│  ├─ .env
│  └─ run.py
│
├─ frontend\
│  ├─ src\
│  │  ├─ api\
│  │  ├─ components\
│  │  ├─ views\
│  │  ├─ stores\
│  │  ├─ composables\
│  │  ├─ utils\
│  │  ├─ router\
│  │  └─ assets\
│  ├─ public\
│  ├─ package.json
│  └─ vite.config.js
│
├─ docs\
│  ├─ api_spec.md
│  ├─ database_design.md
│  ├─ prompt_design.md
│  └─ development_tasks.md
│
└─ README.md
```

---

## 5. 技术栈建议

## 5.1 前端

* Vue 3
* Vite
* Pinia
* Axios
* Element Plus 或 Ant Design Vue（二选一，推荐 Element Plus）
* 浏览器录音：MediaRecorder API

### 前端页面建议

1. `DoctorWorkbench.vue`

   * 主工作站页面
2. `DocumentIndexPage.vue`

   * 病历上传与索引页面
3. `SessionHistoryPage.vue`

   * 会话记录页面
4. `SettingsPage.vue`

   * 基础配置页面

---

## 5.2 后端

推荐：FastAPI

原因：

* 天然适合 REST API
* 支持流式响应
* Pydantic 类型约束方便和 Instructor 配合
* 适合快速构建 AI Demo 服务

### 后端依赖建议

```txt
fastapi
uvicorn
sqlalchemy
pymysql
python-dotenv
pydantic
pydantic-settings
requests
httpx
python-multipart
orjson
loguru
```

如需异步能力：

```txt
aiofiles
```

如需 PDF 解析，可选：

```txt
pypdf
pdfplumber
```

如需和已有 deepseek_interface.py 风格保持一致，可额外使用：

```txt
tenacity
```

---

## 5.3 AI 相关组件

### 1）Dolphin

用途：ASR 语音识别

### 2）Instructor

用途：把 LLM 输出约束为结构化 JSON / Pydantic Schema

### 3）DeepSeek API

用途：

* 结构化抽取
* 病历草稿生成
* 风险提示生成
* 追问问题生成

### 4）PageIndex

用途：

* 解析 PDF 病历样本
* 建立层级索引
* 检索最相似病历

---

## 6. 系统模块拆分

后端必须至少拆成以下服务模块。

### 6.1 asr_service

职责：

* 接收音频文件或音频片段
* 调用 Dolphin ASR
* 返回转写文本

### 6.2 session_service

职责：

* 创建问诊会话
* 保存医患对话片段
* 管理对话顺序和说话人类型

### 6.3 extract_service

职责：

* 对当前问诊对话执行结构化抽取
* 输出门诊病历 JSON

### 6.4 index_service

职责：

* 扫描 PDF 病历目录
* 解析文件
* 建立索引
* 检索相似病历

### 6.5 draft_service

职责：

* 结合当前结构化字段和相似病历生成病历草稿
* 生成处置草稿
* 支持“使用相同检查治疗方案”按钮逻辑

### 6.6 clinical_hint_service

职责：

* 分析当前症状、病史、候选检查和用药
* 输出风险提示
* 输出需要追问的问题
* 输出建议检查项目

### 6.7 llm_service

职责：

* 统一封装 DeepSeek API 调用
* 支持流式输出
* 支持 JSON 输出
* 支持错误重试

---

## 7. 前端工作站页面设计

页面命名：`DoctorWorkbench.vue`

布局建议：三栏式。

### 左侧：患者与控制区

包含：

* 医生信息
* 患者信息
* 问诊控制按钮
* 当前会话状态

控件：

* 开始问诊
* 结束问诊
* 医生说话
* 患者说话
* 重新抽取
* 检索相似病历
* 生成病历草稿
* 使用相同检查治疗方案

### 中间：对话转写区

上下两块：

* 医生说话记录
* 患者说话记录

要求：

* 实时追加显示
* 显示时间戳
* 显示片段状态（转写中 / 完成）

### 右侧：智能辅助区

分为 4 个标签页：

* 结构化病历
* 相似病历
* 风险提示
* 追问建议

---

## 8. 数据库设计

数据库名称建议：

```sql
webmedic_demo
```

### 8.1 doctors

```sql
CREATE TABLE doctors (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    doctor_name VARCHAR(100) NOT NULL,
    title VARCHAR(100) DEFAULT NULL,
    department VARCHAR(100) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

默认初始化：Doctor Panython

### 8.2 patients

```sql
CREATE TABLE patients (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    patient_name VARCHAR(100) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    age INT NOT NULL,
    birthday DATE DEFAULT NULL,
    phone VARCHAR(50) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

默认初始化：张三，男，29 岁

### 8.3 encounter_sessions

```sql
CREATE TABLE encounter_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_no VARCHAR(64) NOT NULL UNIQUE,
    doctor_id BIGINT NOT NULL,
    patient_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'created',
    started_at DATETIME DEFAULT NULL,
    ended_at DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 8.4 transcript_segments

```sql
CREATE TABLE transcript_segments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    speaker_role VARCHAR(20) NOT NULL,
    audio_file_path VARCHAR(500) DEFAULT NULL,
    transcript_text TEXT,
    start_time_ms BIGINT DEFAULT NULL,
    end_time_ms BIGINT DEFAULT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'done',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 8.5 structured_records

```sql
CREATE TABLE structured_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    schema_version VARCHAR(50) NOT NULL,
    raw_json JSON NOT NULL,
    chief_complaint TEXT,
    present_illness TEXT,
    past_history TEXT,
    allergy_history TEXT,
    physical_exam TEXT,
    preliminary_diagnosis TEXT,
    suggested_exams TEXT,
    warning_flags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 8.6 medical_documents

```sql
CREATE TABLE medical_documents (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_hash VARCHAR(128) DEFAULT NULL,
    parse_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    index_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    source_type VARCHAR(50) DEFAULT 'pdf',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 8.7 similar_case_matches

```sql
CREATE TABLE similar_case_matches (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    document_id BIGINT NOT NULL,
    score DECIMAL(10,4) DEFAULT NULL,
    reason_text TEXT,
    rank_no INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 8.8 emr_drafts

```sql
CREATE TABLE emr_drafts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    draft_type VARCHAR(50) NOT NULL,
    content_json JSON DEFAULT NULL,
    content_text LONGTEXT,
    source_case_ids VARCHAR(500) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 8.9 clinical_hints

```sql
CREATE TABLE clinical_hints (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    hint_type VARCHAR(50) NOT NULL,
    hint_title VARCHAR(255) DEFAULT NULL,
    hint_content TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    source_model VARCHAR(100) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 9. Pydantic 结构化 Schema 设计

后端必须定义结构化病历 Schema，供 Instructor 使用。

建议文件：

```text
backend/app/schemas/encounter_schema.py
```

示例：

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class ClinicalHintItem(BaseModel):
    title: str = Field(..., description="提示标题")
    content: str = Field(..., description="提示内容")
    severity: str = Field(..., description="风险等级：info/warn/high")

class FollowupQuestionItem(BaseModel):
    question: str = Field(..., description="建议追问问题")
    reason: Optional[str] = Field(None, description="为什么需要追问")

class SuggestedExamItem(BaseModel):
    exam_name: str
    reason: Optional[str] = None

class EncounterStructuredRecord(BaseModel):
    patient_name: str
    gender: str
    age: int
    chief_complaint: Optional[str] = None
    present_illness: Optional[str] = None
    past_history: Optional[str] = None
    allergy_history: Optional[str] = None
    physical_exam: Optional[str] = None
    preliminary_diagnosis: Optional[str] = None
    suggested_exams: List[SuggestedExamItem] = []
    warning_flags: List[ClinicalHintItem] = []
    followup_questions: List[FollowupQuestionItem] = []
```

---

## 10. API 设计

所有接口统一前缀：

```text
/api/v1
```

### 10.1 会话接口

#### 1）创建问诊会话

```http
POST /api/v1/sessions/create
```

请求体：

```json
{
  "doctor_id": 1,
  "patient_id": 1
}
```

返回：

```json
{
  "success": true,
  "data": {
    "session_id": 1,
    "session_no": "WM202601010001"
  }
}
```

#### 2）结束问诊会话

```http
POST /api/v1/sessions/{session_id}/finish
```

---

### 10.2 音频转写接口

#### 1）上传音频片段并转写

```http
POST /api/v1/asr/transcribe
```

表单字段：

* `session_id`
* `speaker_role`：doctor / patient
* `audio_file`

返回：

```json
{
  "success": true,
  "data": {
    "segment_id": 1001,
    "speaker_role": "patient",
    "transcript_text": "我最近颈部疼痛，还头晕。"
  }
}
```

---

### 10.3 结构化抽取接口

#### 1）根据当前会话重新抽取

```http
POST /api/v1/extract/{session_id}
```

返回：

```json
{
  "success": true,
  "data": {
    "structured_record": {
      "chief_complaint": "颈部疼痛伴头晕3天",
      "present_illness": "..."
    }
  }
}
```

---

### 10.4 病历文档接口

#### 1）上传 PDF 病历

```http
POST /api/v1/documents/upload
```

#### 2）扫描目录病历文件

```http
POST /api/v1/documents/scan-local
```

请求体：

```json
{
  "directory": "D:\\webmedic\\medical_records"
}
```

#### 3）重建索引

```http
POST /api/v1/index/rebuild
```

#### 4）检索相似病历

```http
POST /api/v1/index/search-similar/{session_id}
```

返回：

```json
{
  "success": true,
  "data": {
    "matches": [
      {
        "document_id": 11,
        "file_name": "case_001.pdf",
        "score": 0.92,
        "reason_text": "主诉、病程和检查建议高度相似"
      }
    ]
  }
}
```

---

### 10.5 病历草稿接口

#### 1）生成病历草稿

```http
POST /api/v1/draft/generate/{session_id}
```

#### 2）使用相同检查治疗方案

```http
POST /api/v1/draft/apply-similar-plan/{session_id}
```

请求体：

```json
{
  "source_document_id": 11
}
```

---

### 10.6 临床提示接口

#### 1）生成追问与风险提示

```http
POST /api/v1/clinical-hints/generate/{session_id}
```

返回：

```json
{
  "success": true,
  "data": {
    "warnings": [
      {
        "title": "需确认肾功能",
        "content": "若考虑使用脱水类药物，应先确认肾功能情况",
        "severity": "warn"
      }
    ],
    "followup_questions": [
      {
        "question": "最近是否有肾功能异常或肾病史？",
        "reason": "用于评估药物风险"
      }
    ]
  }
}
```

---

## 11. 后端服务实现要求

## 11.1 LLM 服务统一封装

新建：

```text
backend/app/services/llm_service.py
```

功能要求：

* 统一处理 DeepSeek API URL
* 统一处理 API Key
* 统一设置超时、重试、异常捕获
* 支持非流式调用
* 支持流式调用
* 支持返回 JSON
* 支持 system prompt + user prompt 组合

禁止在业务代码中到处直接写 `requests.post` 调 DeepSeek。

---

## 11.2 Prompt 文件化

所有 prompt 必须单独放在：

```text
backend/app/prompts/
```

至少拆分以下文件：

* `extract_structured_record.txt`
* `generate_emr_draft.txt`
* `generate_clinical_hints.txt`
* `search_similar_reasoning.txt`

不要把长 prompt 散落在 Python 代码里。

---

## 11.3 错误处理

要求：

* API 返回统一结构
* 出错时返回 `success=false`
* 错误信息不要直接把内部堆栈暴露给前端
* 日志写入 `backend/logs/`

统一返回格式：

```json
{
  "success": false,
  "message": "error message",
  "data": null
}
```

---

## 12. PageIndex 集成要求

### 12.1 目标

对本地病历 PDF 建立索引，并根据当前问诊记录检索最相似的病历。

### 12.2 要求

* 支持扫描固定目录
* 记录索引状态
* 若索引失败，必须记录错误原因
* 检索结果至少返回：

  * 文件名
  * 相似度分数
  * 匹配原因说明

### 12.3 注意

* 先做小规模样本库
* 不要求一次支持海量文档
* 检索结果主要用于 demo 展示
* 结果必须标注“仅供参考”

---

## 13. Dolphin 集成要求

### 13.1 输入方式

前端使用浏览器录音，按说话人角色上传音频片段。

### 13.2 交互方式

* 用户点击“医生说话”后开始录音
* 再次点击后停止并上传
* 用户点击“患者说话”时同理

### 13.3 输出要求

* 返回文本结果
* 保存原始音频文件路径
* 保存 speaker_role
* 保存 transcript_text

### 13.4 降复杂度要求

不要在第一版实现自动说话人分离，先采用“按钮指定当前说话人”的方式。

---

## 14. Instructor + DeepSeek 抽取要求

### 14.1 抽取输入

输入为当前会话全部医患对话文本。

### 14.2 抽取输出

必须输出为结构化 JSON，并落库。

### 14.3 抽取内容

至少包含：

* 主诉
* 现病史
* 既往史
* 过敏史
* 体格检查
* 初步诊断
* 建议检查
* 风险提示
* 追问问题

### 14.4 抽取原则

* 缺失信息要明确标记为未提及
* 不允许编造患者信息
* 输出字段必须与 Schema 一致

---

## 15. 病历草稿生成要求

### 15.1 生成原则

病历草稿来自两部分：

1. 当前会话结构化数据
2. 相似病历提供的可参考内容

### 15.2 草稿内容

至少生成：

* 主诉
* 现病史
* 既往史
* 过敏史
* 体格检查
* 初步诊断
* 建议检查
* 处置意见（初始可为空）

### 15.3 风险控制

* 草稿必须标注“AI 草稿，仅供医生确认”
* 相似病历继承内容必须可追溯到来源文件
* 不允许自动把处方和治疗方案当成最终结果

---

## 16. 临床提示引擎要求

### 16.1 功能定位

这是“问诊辅助提示引擎”，不是正式审方系统。

### 16.2 输入

* 当前结构化病历
* 当前候选诊断
* 相似病历中的检查治疗建议

### 16.3 输出

输出分三类：

1. 风险提示
2. 建议追问问题
3. 建议检查项目

### 16.4 示例输出风格

* 风险提示：如“若考虑使用某类药物，建议先确认肾功能”
* 追问问题：如“近期是否存在肾病史或肾功能异常？”
* 建议检查：如“肾功能、血压、颈椎相关检查”

### 16.5 严格约束

* 不能写成确定性医疗结论
* 不能输出“必须用某药”
* 应尽量用“建议确认”“建议追问”“建议检查”措辞

---

## 17. 开发顺序（必须按阶段推进）

## 阶段 1：项目初始化

1. 创建前后端项目目录
2. 创建数据库
3. 初始化医生与患者固定数据
4. 完成前后端基本启动
5. 配置 `.env`

## 阶段 2：工作站界面

1. 完成 DoctorWorkbench 页面
2. 固定患者信息展示
3. 会话创建与结束
4. 按钮布局和交互打通

## 阶段 3：音频与转写

1. 实现浏览器录音
2. 上传音频片段
3. 调用 Dolphin
4. 显示转写结果
5. 保存转写记录

## 阶段 4：结构化抽取

1. 定义 Schema
2. 封装 llm_service
3. 接入 Instructor
4. 抽取结构化门诊要素
5. 结果落库并展示

## 阶段 5：PDF 病历索引

1. 扫描本地病历目录
2. 记录文档信息
3. 集成 PageIndex
4. 建索引
5. 实现相似病历检索

## 阶段 6：病历草稿与提示引擎

1. 生成病历草稿
2. 生成风险提示
3. 生成追问问题
4. 生成建议检查
5. 完成右侧智能辅助区展示

## 阶段 7：打磨

1. 增加日志
2. 增加错误提示
3. 增加状态显示
4. 增加会话回放
5. 增加文档说明

---

## 18. 环境变量要求

后端 `.env` 至少包括：

```env
APP_ENV=dev
APP_PORT=8000
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=webmedic_demo
DEEPSEEK_API_KEY=replace_me
DEEPSEEK_BASE_URL=https://api.deepseek.com
MEDICAL_RECORD_DIR=D:\webmedic\medical_records
UPLOAD_DIR=D:\webmedic\backend\uploads
LOG_DIR=D:\webmedic\backend\logs
```

**要求：**

* API Key 不允许硬编码到源码
* 已暴露过的 Key 必须轮换

---

## 19. Claude 编码要求

这部分是给 Claude 的直接要求。

### 19.1 输出代码风格要求

* 必须模块化
* 必须写清注释
* 不要把所有逻辑写在单文件里
* 不要生成无法运行的伪代码
* 每完成一个阶段都要保证可以启动和测试

### 19.2 编码约束

* 优先生成真实可运行代码
* 优先实现最小闭环
* 不要一开始就做过度复杂的架构
* 第一版禁止引入自动说话人分离
* 第一版禁止做复杂权限系统
* 第一版禁止做 WebSocket 重度改造，先用 REST + 轮询或简单流式

### 19.3 提交顺序要求

Claude 应按以下顺序输出代码：

1. 后端基础骨架
2. 数据库模型和初始化脚本
3. 前端工作站页面
4. 会话 API
5. 音频转写 API
6. 结构化抽取 API
7. 病历索引 API
8. 病历草稿 API
9. 临床提示 API
10. README 和启动步骤

---

## 20. 最小可演示闭环

验收标准：至少能完成以下流程：

1. 打开前端工作站页面
2. 展示 Doctor Panython 与张三基本信息
3. 点击开始问诊创建 session
4. 点击“患者说话”录音并上传
5. 后端返回转写结果并显示
6. 点击“重新抽取”得到结构化门诊记录
7. 点击“检索相似病历”返回至少 1 条结果
8. 点击“生成病历草稿”显示草稿文本
9. 点击“生成提示”显示风险提示和追问问题

只要这 9 步可以完整演示，就算第一阶段成功。

---

## 21. 后续增强方向（先不做）

以下内容不要在第一版优先实现，但要预留扩展能力：

* 自动说话人分离
* 多医生多患者管理
* 权限系统
* 正式 EMR 模板导出
* 医学知识图谱
* 药品数据库和真正审方规则引擎
* 向量检索与 PageIndex 混合召回
* 多轮会话自动摘要

---

## 22. 给 Claude 的最终执行指令

请基于本技术文档，从零开始生成可运行的项目骨架与代码。

要求：

1. 后端使用 FastAPI + SQLAlchemy + MySQL
2. 前端使用 Vue3 + Vite + Pinia + Axios
3. 目录结构严格按本文档组织
4. 所有接口按本文档 API 命名
5. 先完成最小可演示闭环
6. 代码必须可启动，不要只给示意代码
7. 每个阶段完成后都给出运行步骤
8. 对于 PageIndex、Dolphin、Instructor、DeepSeek 的接入，先写可替换式封装层，便于后续替换真实服务
9. 默认先用 mock 数据保证流程跑通，再逐步接真实模型和真实索引
10. 输出时先给完整项目骨架，再逐模块补全代码

---

## 23. 开发策略建议

最重要原则：

**先把页面、数据库、会话、转写、抽取、检索、草稿、提示这条主链路跑通。**

不要在第一轮开发就陷入以下问题：

* 医疗规则过深
* 语音分离过深
* 文档索引优化过深
* 提示工程过深
* UI 美化过深

第一阶段目标只有一个：

**让用户看到一个完整工作的 AI 门诊辅助 Demo。**
