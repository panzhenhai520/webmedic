# Dolphin ASR 本地部署完整指南

## 部署状态

✅ 虚拟环境已创建：`dolphin_env`
✅ FunASR 已安装
⏳ PyTorch 正在安装中...

## 部署步骤

### 1. 安装依赖（已完成）

```bash
cd D:\webmedic\backend
python -m venv dolphin_env
dolphin_env\Scripts\activate
pip install funasr -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 2. 启动 Dolphin 服务

**方式一：使用启动脚本（推荐）**
```bash
cd D:\webmedic\backend
start_dolphin.bat
```

**方式二：手动启动**
```bash
cd D:\webmedic\backend
dolphin_env\Scripts\activate
funasr-server --model damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch --port 8000 --host 0.0.0.0
```

**首次启动说明：**
- 首次启动会自动下载模型（约 1-2GB）
- 下载时间取决于网络速度（5-15分钟）
- 模型会缓存到本地，后续启动无需下载

### 3. 配置 WebMedic

编辑 `D:\webmedic\backend\.env`：

```env
# 切换到 Dolphin 引擎
ASR_ENGINE=dolphin

# Dolphin 服务地址
DOLPHIN_API_URL=http://localhost:8000/asr
```

### 4. 启动 WebMedic

```bash
# 启动后端
cd D:\webmedic\backend
python main.py

# 启动前端（另一个终端）
cd D:\webmedic\frontend
npm run dev
```

### 5. 测试录音

1. 打开浏览器访问前端
2. 开始问诊
3. 打开"真实录音"开关
4. 点击"医生说话"或"患者说话"
5. 对着麦克风说话
6. 再次点击停止录音
7. 系统会使用 Dolphin 识别语音

## 验证安装

### 验证 FunASR
```bash
cd D:\webmedic\backend
dolphin_env\Scripts\python -c "import funasr; print('FunASR 版本:', funasr.__version__)"
```

### 验证 PyTorch
```bash
cd D:\webmedic\backend
dolphin_env\Scripts\python -c "import torch; print('PyTorch 版本:', torch.__version__)"
```

### 测试 Dolphin 服务
```bash
cd D:\webmedic\backend
test_dolphin.bat
```

## 切换 ASR 引擎

### 切换到 Whisper
```env
ASR_ENGINE=whisper
```

### 切换到 Dolphin
```env
ASR_ENGINE=dolphin
```

### 使用 Mock 模式
```env
ASR_USE_MOCK=true
```

## 故障排查

### 问题1：模型下载失败
**解决方案：**
- 检查网络连接
- 使用国内镜像：设置环境变量 `MODELSCOPE_CACHE=D:\models`
- 手动下载模型后放到缓存目录

### 问题2：服务启动失败
**解决方案：**
- 检查端口 8000 是否被占用
- 查看错误日志
- 确认 PyTorch 已正确安装

### 问题3：识别失败
**解决方案：**
- 检查 Dolphin 服务是否运行：访问 http://localhost:8000
- 查看后端日志
- 确认音频格式正确（webm）

### 问题4：识别速度慢
**解决方案：**
- CPU 版本较慢，考虑使用 GPU 版本
- 减小音频文件大小
- 升级服务器配置

## 性能优化

### 使用 GPU 加速（可选）

如果有 NVIDIA 显卡：

```bash
# 卸载 CPU 版本
pip uninstall torch torchaudio

# 安装 GPU 版本
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 调整并发数

修改启动命令：
```bash
funasr-server --model damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch --port 8000 --workers 4
```

## 系统要求

### 最低配置
- CPU: 2核
- 内存: 4GB
- 磁盘: 5GB（包含模型）
- 操作系统: Windows 10/11, Linux, macOS

### 推荐配置
- CPU: 4核+
- 内存: 8GB+
- 磁盘: 10GB+
- GPU: NVIDIA GPU（可选，用于加速）

## 常用命令

### 启动服务
```bash
cd D:\webmedic\backend
start_dolphin.bat
```

### 停止服务
按 `Ctrl+C`

### 查看日志
服务运行时会在终端显示日志

### 测试服务
```bash
cd D:\webmedic\backend
test_dolphin.bat
```

## 模型信息

**使用的模型：**
- 名称: Paraformer Large
- 来源: 阿里达摩院
- 语言: 中文
- 大小: ~1.5GB
- 准确率: 高

**模型缓存位置：**
- Windows: `C:\Users\<用户名>\.cache\modelscope`
- Linux: `~/.cache/modelscope`

## 下一步

1. 等待 PyTorch 安装完成
2. 运行 `start_dolphin.bat` 启动服务
3. 修改 `.env` 切换到 Dolphin
4. 重启 WebMedic 后端
5. 测试真实录音功能

## 技术支持

如遇问题，请查看：
- FunASR 文档: https://github.com/alibaba-damo-academy/FunASR
- ModelScope: https://modelscope.cn
- 后端日志: `D:\webmedic\backend\logs`
