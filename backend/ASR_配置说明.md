# ASR 语音识别配置说明

## 支持的 ASR 引擎

WebMedic 支持两种语音识别引擎：

1. **OpenAI Whisper** - 商业 API，识别准确度高
2. **清华 Dolphin** - 开源模型，可本地部署

## 配置方式

在 `.env` 文件中配置：

```env
# ASR 引擎配置
ASR_ENGINE=whisper  # 可选: whisper, dolphin
ASR_USE_MOCK=false  # 是否使用 Mock 模式

# OpenAI Whisper 配置
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Dolphin ASR 配置
DOLPHIN_API_URL=http://localhost:8000/asr
DOLPHIN_API_KEY=  # 如果需要认证
```

## 使用 Whisper

### 1. 获取 API Key

访问 https://platform.openai.com/api-keys 创建 API Key

### 2. 配置

```env
ASR_ENGINE=whisper
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. 重启服务

```bash
# 重启后端
python main.py
```

## 使用 Dolphin

### 1. 部署 Dolphin 服务

Dolphin 可以通过以下方式部署：

#### 方式一：使用 FunASR（推荐）

```bash
# 安装 FunASR
pip install funasr

# 启动服务
funasr-server --model damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
```

#### 方式二：Docker 部署

```bash
docker run -d -p 8000:8000 \
  --name dolphin-asr \
  registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-cpu-0.4.0
```

### 2. 配置

```env
ASR_ENGINE=dolphin
DOLPHIN_API_URL=http://localhost:8000/asr
```

### 3. API 格式说明

Dolphin 服务需要提供以下 API 接口：

**请求：**
```
POST /asr
Content-Type: multipart/form-data

file: <audio_file>
```

**响应：**
```json
{
  "text": "识别的文本内容"
}
```

或

```json
{
  "result": "识别的文本内容"
}
```

### 4. 自定义 API 格式

如果你的 Dolphin 服务使用不同的 API 格式，请修改 `app/services/asr_service.py` 中的 `_dolphin_transcribe` 方法。

## Mock 模式

用于快速测试，不调用真实 ASR 服务：

```env
ASR_USE_MOCK=true
```

## 前端使用

1. 打开"真实录音"开关
2. 点击"医生说话"或"患者说话"开始录音
3. 再次点击停止录音
4. 系统会根据配置的 ASR 引擎进行识别

## 故障排查

### Whisper 相关

- **错误：未配置 Whisper API Key**
  - 检查 `.env` 中的 `OPENAI_API_KEY` 是否正确配置

- **错误：Whisper 识别失败**
  - 检查 API Key 是否有效
  - 检查网络连接
  - 查看后端日志获取详细错误信息

### Dolphin 相关

- **错误：无法连接到 Dolphin 服务**
  - 检查 Dolphin 服务是否启动
  - 检查 `DOLPHIN_API_URL` 配置是否正确

- **错误：Dolphin 识别失败**
  - 检查 API 响应格式是否匹配
  - 查看后端日志获取详细错误信息

## 性能对比

| 引擎 | 准确度 | 速度 | 成本 | 部署难度 |
|------|--------|------|------|----------|
| Whisper | 高 | 中 | 按量付费 | 简单 |
| Dolphin | 中-高 | 快 | 免费 | 中等 |

## 推荐配置

- **开发测试**：使用 Mock 模式
- **演示展示**：使用 Whisper（准确度高）
- **生产环境**：使用 Dolphin（成本低，可控）
