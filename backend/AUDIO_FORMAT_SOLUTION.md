# Dolphin ASR 音频格式问题解决方案

## 问题描述

浏览器录音生成 WebM 格式，但 Dolphin ASR 的 soundfile 库不支持 WebM 格式，导致识别失败：
```
[WinError 2] 系统找不到指定的文件
模型识别失败: 可能是音频格式不支持或文件损坏
```

## 根本原因

1. 浏览器的 MediaRecorder API 通常只支持 WebM 或 MP4 格式
2. soundfile 库不支持 WebM 格式
3. 需要 ffmpeg 进行格式转换

## 解决方案对比

### 方案 1：安装 ffmpeg（推荐）✅

**优点**：
- 一劳永逸，支持所有音频格式
- 转换质量高，速度快
- 后端处理，前端无需修改

**缺点**：
- 需要安装额外软件
- 需要配置系统 PATH

**安装步骤**：
```bash
# 方式 1：自动安装（推荐）
cd D:\webmedic\backend
setup_ffmpeg.bat  # 以管理员权限运行

# 方式 2：手动安装
# 1. 访问 https://www.gyan.dev/ffmpeg/builds/
# 2. 下载 ffmpeg-release-essentials.zip
# 3. 解压到 C:\ffmpeg
# 4. 添加到系统 PATH: C:\ffmpeg\bin
# 5. 验证: ffmpeg -version
```

**使用**：
- 安装后重启 Dolphin ASR 服务即可
- 后端会自动使用 ffmpeg 转换音频

### 方案 2：前端生成 WAV 格式（已实现）✅

**优点**：
- 不需要安装 ffmpeg
- 前端直接生成 WAV，后端无需转换
- 纯 JavaScript 实现，跨平台

**缺点**：
- 前端代码更复杂
- 占用浏览器内存和 CPU
- 可能影响录音性能

**实现**：
- 已创建 `wavEncoder.js` 工具
- 已修改 `useRecorder.js` 使用 Web Audio API
- 直接生成 16kHz 单声道 WAV 格式

**使用**：
- 前端代码已更新，无需额外配置
- 重启前端服务即可使用

## 当前状态

### 后端（dolphin_server.py）
- ✅ 强制要求 ffmpeg
- ✅ 检测到 WebM/MP4/OGG/M4A 格式时自动转换
- ✅ 如果 ffmpeg 未安装，返回明确的错误信息和安装提示

### 前端（useRecorder.js）
- ✅ 使用 Web Audio API 直接生成 WAV
- ✅ 16kHz 采样率，单声道
- ✅ 无需后端转换

## 推荐使用方式

### 开发环境
**推荐方案 2（前端 WAV）**：
- 无需安装 ffmpeg
- 开发更便捷

### 生产环境
**推荐方案 1（ffmpeg）**：
- 性能更好
- 支持更多格式
- 更稳定可靠

## 测试步骤

### 测试方案 1（ffmpeg）

1. 安装 ffmpeg：
   ```bash
   cd D:\webmedic\backend
   setup_ffmpeg.bat
   ```

2. 重启 Dolphin ASR：
   ```bash
   # 停止当前服务（Ctrl+C）
   start_dolphin.bat
   ```

3. 测试录音：
   - 访问 http://localhost:5173
   - 开始问诊 → 录音 → 查看识别结果

### 测试方案 2（前端 WAV）

1. 重启前端服务：
   ```bash
   cd D:\webmedic\frontend
   npm run dev
   ```

2. 测试录音：
   - 访问 http://localhost:5173
   - 开始问诊 → 录音 → 查看识别结果
   - 浏览器控制台应显示 "生成 WAV 文件"

## 故障排查

### ffmpeg 安装失败
- 检查网络连接
- 手动下载并安装
- 确保添加到系统 PATH

### 前端 WAV 生成失败
- 检查浏览器控制台错误
- 确保浏览器支持 Web Audio API
- 尝试使用 Chrome/Edge 浏览器

### 识别仍然失败
- 检查 Dolphin ASR 服务是否正常运行
- 查看后端日志：`D:\webmedic\backend\logs\`
- 尝试使用 Mock 模式测试：`.env` 中设置 `ASR_USE_MOCK=true`

## 文件清单

### 新增文件
- `backend/setup_ffmpeg.bat` - ffmpeg 自动安装脚本（批处理）
- `backend/setup_ffmpeg.ps1` - ffmpeg 自动安装脚本（PowerShell）
- `backend/install_ffmpeg.bat` - ffmpeg 安装指南
- `frontend/src/utils/wavEncoder.js` - WAV 编码器
- `backend/AUDIO_FORMAT_SOLUTION.md` - 本文档

### 修改文件
- `backend/dolphin_server.py` - 强制要求 ffmpeg，改进错误提示
- `frontend/src/composables/useRecorder.js` - 使用 Web Audio API 生成 WAV

## 总结

两种方案都已实现并可用：
- **方案 1（ffmpeg）**：适合生产环境，性能更好
- **方案 2（前端 WAV）**：适合开发环境，无需安装额外软件

建议：**先使用方案 2 快速测试，生产环境使用方案 1**。
