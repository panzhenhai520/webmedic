# Stage 6 完成报告 - 结构化抽取链路

## 实现内容

### 后端实现

#### 1. 配置层
**文件路径:** `backend/app/core/config.py`
- 新增 `DEEPSEEK_MODEL`: DeepSeek 模型名称
- 新增 `LLM_USE_MOCK`: Mock/Real 模式切换开关
- 新增 `LLM_TIMEOUT`: API 超时时间
- 新增 `LLM_MAX_RETRIES`: 最大重试次数

#### 2. Schema 层
**文件路径:** `backend/app/schemas/encounter_schema.py`
- `StructuredRecordData`: 结构化病历数据模型
- `ExtractRequest`: 抽取请求模型
- `ExtractResponse`: 抽取响应模型
- `StructuredRecordResponse`: 结构化病历详情模型

#### 3. Prompt 层
**文件路径:** `backend/app/prompts/extract_structured_record.txt`
- 结构化抽取 Prompt 模板
- 包含任务说明、输出格式、注意事项
- 支持变量替换：dialogue_text, patient_name, gender, age

#### 4. Service 层

**文件路径:** `backend/app/services/llm_service.py`
- `LLMService`: 统一封装 DeepSeek API 调用
- 支持 Mock/Real 双模式切换
- `generate_json()`: 生成 JSON 格式响应
- `generate_text()`: 生成文本响应
- Mock 模式返回预设数据
- Real 模式使用 OpenAI SDK 连接 DeepSeek
- 使用 `response_format={"type": "json_object"}` 确保 JSON 输出

**文件路径:** `backend/app/services/extract_service.py`
- `ExtractService`: 结构化抽取服务
- `load_prompt_template()`: 加载 Prompt 模板
- `build_dialogue_text()`: 构建对话文本
- `extract_structured_record()`: 执行结构化抽取
  - 获取会话对话记录
  - 构建 Prompt
  - 调用 LLM 服务
  - 验证 JSON 结构
  - 保存到数据库
- `get_structured_record()`: 获取结构化病历

#### 5. API 层
**文件路径:** `backend/app/api/endpoints/extract.py`
- `POST /api/v1/extract/{session_id}`: 抽取结构化病历
- `GET /api/v1/extract/{session_id}`: 获取结构化病历

**文件路径:** `backend/app/api/router.py`
- 注册 extract 路由到主路由

### 前端实现

#### 1. API 模块
**文件路径:** `frontend/src/api/extract.js`
- `extractStructuredRecord()`: 调用抽取接口
- `getStructuredRecord()`: 获取结构化病历

**文件路径:** `frontend/src/api/index.js`
- 导出 extract 相关 API

#### 2. 组件更新
**文件路径:** `frontend/src/components/workbench/ControlPanel.vue`
- 更新 `handleExtract()` 函数
- 点击"重新抽取"调用真实 API
- 抽取成功后更新 store

**文件路径:** `frontend/src/components/workbench/AssistantTabs.vue`
- 更新结构化病历展示
- 显示所有8个字段：
  - 主诉
  - 现病史
  - 既往史
  - 过敏史
  - 体格检查
  - 初步诊断
  - 建议检查
  - 风险标记

### 配置文件

**文件路径:** `backend/.env`
- 新增 LLM 相关配置
- `LLM_USE_MOCK=true` 默认使用 Mock 模式

**文件路径:** `backend/.env.example`
- 更新示例配置文件
- 添加详细注释说明

### 数据库变化
- `structured_records` 表将记录所有结构化病历
- 每个会话只保存一条记录，重新抽取会更新现有记录

## 启动步骤

### 1. 启动后端
```bash
cd backend
python main.py
```
后端将在 http://localhost:8001 启动

### 2. 启动前端
```bash
cd frontend
npm run dev
```
前端将在 http://localhost:5173 启动

## 测试步骤

### 测试1: Mock 模式测试（默认）
1. 访问 http://localhost:5173
2. 点击"开始问诊"创建会话
3. 点击"医生说话"录音，再次点击停止
4. 点击"患者说话"录音，再次点击停止
5. 重复几次，创建多轮对话
6. 点击"重新抽取"按钮
7. 验证右侧"结构化病历"标签页显示抽取结果
8. 验证显示以下字段：
   - 主诉：颈部疼痛伴头晕3天
   - 现病史：患者3天前无明显诱因出现颈部疼痛...
   - 既往史：既往体健，否认高血压、糖尿病等慢性病史...
   - 过敏史：对青霉素过敏
   - 体格检查：颈部活动受限，左侧颈部肌肉紧张...
   - 初步诊断：颈椎病（神经根型）
   - 建议检查：颈椎X光片、血常规、血沉
   - 风险标记：青霉素过敏，避免使用青霉素类抗生素

### 测试2: 数据库验证
```bash
# 查看数据库中的结构化记录
mysql -u root -pwww.59697.com
use webmedic_demo;
SELECT * FROM structured_records ORDER BY created_at DESC LIMIT 5;
```

验证字段:
- session_id: 对应当前会话ID
- schema_version: v1.0
- raw_json: 完整的 JSON 数据
- chief_complaint, present_illness 等字段有值

### 测试3: 真实 DeepSeek API 测试

#### 步骤1: 切换到真实模式
编辑 `backend/.env` 文件：
```bash
# 将 LLM_USE_MOCK 改为 false
LLM_USE_MOCK=false
```

#### 步骤2: 重启后端
```bash
# 停止后端（Ctrl+C）
# 重新启动
cd backend
python main.py
```

#### 步骤3: 验证真实 API
1. 查看后端启动日志，应显示：
   ```
   LLM Service 初始化成功 - 真实模式
   ```

2. 重复测试1的步骤
3. 点击"重新抽取"后，后端会调用真实 DeepSeek API
4. 验证返回的结构化数据是根据实际对话内容生成的

#### 步骤4: 查看日志
```bash
# 查看后端日志
tail -f backend/logs/app.log
```

应该能看到：
- "使用真实 DeepSeek API 生成 JSON"
- "DeepSeek API 返回内容: ..."
- "创建会话 X 的结构化病历成功"

## 本阶段完成说明

### 已完成功能
✅ 定义结构化病历 Pydantic Schema
✅ 封装 LLM Service（支持 Mock/Real 双模式）
✅ 封装 Extract Service
✅ 提供 `/api/v1/extract/{session_id}` 接口
✅ Prompt 独立文件化
✅ 抽取结果落库到 structured_records
✅ 前端点击"重新抽取"展示结果
✅ 支持 Mock/Real 模式平滑切换

### 技术亮点

1. **双模式设计**: 通过 `LLM_USE_MOCK` 配置项轻松切换 Mock/Real 模式
2. **统一封装**: LLM Service 统一封装 DeepSeek API，其他服务不直接调用 HTTP
3. **Prompt 管理**: Prompt 独立文件化，便于维护和优化
4. **JSON 约束**: 使用 `response_format={"type": "json_object"}` 确保 API 返回 JSON
5. **Pydantic 验证**: 使用 Pydantic Schema 验证返回的 JSON 结构
6. **错误处理**: 完善的日志记录和错误提示
7. **数据更新**: 同一会话重新抽取会更新现有记录，不会重复创建

### Mock 模式 vs 真实模式

| 特性 | Mock 模式 | 真实模式 |
|------|----------|---------|
| 配置 | `LLM_USE_MOCK=true` | `LLM_USE_MOCK=false` |
| API Key | 不需要 | 需要有效的 DeepSeek API Key |
| 返回数据 | 预设的固定数据 | 根据实际对话生成 |
| 响应速度 | 极快（毫秒级） | 较慢（秒级） |
| 成本 | 免费 | 消耗 API 额度 |
| 适用场景 | 开发调试、演示 | 生产环境、真实使用 |

### 如何从 Mock 切换到 Real

**方法1: 修改 .env 文件（推荐）**
```bash
# 编辑 backend/.env
LLM_USE_MOCK=false

# 重启后端
cd backend
python main.py
```

**方法2: 环境变量**
```bash
# Linux/Mac
export LLM_USE_MOCK=false
python main.py

# Windows
set LLM_USE_MOCK=false
python main.py
```

**验证方式:**
- 查看后端启动日志
- Mock 模式: "LLM Service 初始化成功 - Mock 模式"
- 真实模式: "LLM Service 初始化成功 - 真实模式"

## 下一阶段建议

**Stage 7: 相似病历检索**
- 实现 index_service 服务
- 解析 PDF 病历文件
- 建立向量索引
- 实现相似度检索
- 在助手区域显示相似病历

**关键任务:**
1. 集成 PageIndex 或其他向量检索工具
2. 解析 PDF 病历样本
3. 建立病历索引
4. 实现相似度计算
5. 创建相似病历展示组件
6. 实现"检索相似病历"按钮功能

**预期输出:**
- 相似病历列表
- 相似度评分
- 相似原因说明
- 支持查看病历详情
