# Stage 5 完成报告 - 音频上传与 ASR 转写链路

## 实现内容

### 后端实现

#### 1. Schema 层
**文件路径:** `backend/app/schemas/asr.py`
- `TranscribeResponse`: 转写响应模型
- `TranscriptSegmentResponse`: 转写片段详情模型

#### 2. Service 层
**文件路径:** `backend/app/services/asr_service.py`
- `ASRService.transcribe_audio()`: ASR 适配层，第一版使用 mock 转写
- 预留 Dolphin ASR 切换接口
- 根据说话人角色返回不同的 mock 文本

**文件路径:** `backend/app/services/transcript_service.py`
- `TranscriptService.create_segment()`: 创建转写片段记录
- `TranscriptService.get_segments_by_session()`: 获取会话的所有转写片段
- `TranscriptService.get_segment_by_id()`: 根据ID获取转写片段

#### 3. API 层
**文件路径:** `backend/app/api/endpoints/asr.py`
- `POST /api/v1/asr/transcribe`: 接收音频文件上传并转写
  - 表单字段: session_id, speaker_role, audio_file
  - 保存音频到 uploads/audio 目录
  - 调用 ASR 服务转写
  - 创建 transcript_segments 记录
  - 返回转写结果
- `GET /api/v1/asr/segments/{session_id}`: 获取会话的所有转写片段

**文件路径:** `backend/app/api/router.py`
- 注册 ASR 路由到主路由

### 前端实现

#### 1. API 模块
**文件路径:** `frontend/src/api/asr.js`
- `transcribeAudio()`: 上传音频并转写
- `getSessionSegments()`: 获取会话转写片段

**文件路径:** `frontend/src/api/index.js`
- 导出 ASR 相关 API

#### 2. Composable
**文件路径:** `frontend/src/composables/useRecorder.js`
- 封装 MediaRecorder 录音逻辑
- `startRecording()`: 开始录音
- `stopRecording()`: 停止录音并返回音频 Blob
- `cancelRecording()`: 取消录音

#### 3. 组件更新
**文件路径:** `frontend/src/components/workbench/ControlPanel.vue`
- 集成 useRecorder 录音功能
- 点击"医生说话"/"患者说话"开始录音
- 再次点击停止录音并上传
- 显示录音状态和提示
- 转写成功后添加对话到列表

### 数据库变化
- `transcript_segments` 表将记录所有转写片段
- 每个片段包含: session_id, speaker_role, audio_file_path, transcript_text, status

### 文件系统
- 创建 `backend/uploads/audio/` 目录存储音频文件
- 音频文件使用 UUID 命名避免冲突
- 添加 .gitignore 防止上传文件进入版本控制

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

### 测试1: 页面加载和会话创建
1. 访问 http://localhost:5173
2. 验证医生和患者信息正确显示
3. 点击"开始问诊"创建会话
4. 验证会话编号显示

### 测试2: 医生录音
1. 点击"医生说话"按钮
2. 浏览器会请求麦克风权限，点击"允许"
3. 验证按钮文字变为"停止录音"
4. 验证显示"录音中... 点击按钮停止"提示
5. 对着麦克风说话（或保持静音）
6. 再次点击"医生说话"按钮停止录音
7. 验证显示"转写成功"提示
8. 验证对话区域显示转写文本（mock 数据）

### 测试3: 患者录音
1. 点击"患者说话"按钮
2. 验证按钮文字变为"停止录音"
3. 验证显示"录音中... 点击按钮停止"提示
4. 对着麦克风说话（或保持静音）
5. 再次点击"患者说话"按钮停止录音
6. 验证显示"转写成功"提示
7. 验证对话区域显示转写文本（mock 数据）

### 测试4: 多轮对话
1. 交替点击"医生说话"和"患者说话"
2. 每次录音后验证对话列表增加新记录
3. 验证医生和患者的对话显示在不同位置（左右）

### 测试5: 后端数据验证
```bash
# 查看数据库中的转写记录
mysql -u root -pwww.59697.com
use webmedic_demo;
SELECT * FROM transcript_segments ORDER BY created_at DESC LIMIT 10;
```

验证字段:
- session_id: 对应当前会话ID
- speaker_role: doctor 或 patient
- audio_file_path: uploads/audio/xxx.webm
- transcript_text: 转写文本
- status: done

### 测试6: 音频文件验证
```bash
# 查看上传的音频文件
ls -lh backend/uploads/audio/
```

验证每次录音都生成了对应的 .webm 文件

## 本阶段完成说明

### 已完成功能
✅ 前端 MediaRecorder 录音能力
✅ 医生/患者两种角色录音上传
✅ 后端接收音频并保存文件
✅ transcript_segments 数据库记录
✅ ASR 服务适配层（mock 版本）
✅ 转写结果显示到对话区域

### 技术亮点
1. **录音交互优化**: 点击开始录音，再次点击停止，按钮文字动态变化
2. **ASR 适配层设计**: 预留 Dolphin 切换接口，未来只需修改 `asr_service.py` 的 `transcribe_audio` 方法
3. **文件管理**: UUID 命名避免冲突，.gitignore 保护上传文件
4. **错误处理**: 完善的权限检查和错误提示

### Mock 数据说明
当前版本使用 mock 转写结果，根据说话人角色随机返回预设文本：
- 医生: "您好，请问哪里不舒服？" 等7条
- 患者: "医生您好，我最近颈部疼痛，还有点头晕。" 等7条

未来切换到真实 Dolphin ASR 时，只需修改 `backend/app/services/asr_service.py` 中的 `transcribe_audio` 方法实现。

## 下一阶段建议

**Stage 6: 结构化抽取**
- 实现 extract_service 服务
- 调用 DeepSeek API 进行结构化抽取
- 从对话记录中提取门诊病历字段
- 保存到 structured_records 表
- 在助手区域显示结构化信息

**关键任务:**
1. 集成 DeepSeek API
2. 设计结构化抽取 Prompt
3. 实现 Instructor 约束输出
4. 创建结构化病历展示组件
5. 实现"重新抽取"按钮功能

**预期输出字段:**
- 主诉 (chief_complaint)
- 现病史 (present_illness)
- 既往史 (past_history)
- 过敏史 (allergy_history)
- 体格检查 (physical_exam)
- 初步诊断 (preliminary_diagnosis)
- 建议检查 (suggested_exams)
- 风险标记 (warning_flags)
