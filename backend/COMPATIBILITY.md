# 两种方案兼容性说明

## 当前状态

### 后端（dolphin_server.py）
```python
# 只对特定格式进行转换
if file_ext.lower() in ['.webm', '.ogg', '.m4a', '.mp4']:
    # 需要转换，使用 ffmpeg
    convert_audio_format(temp_path, converted_path)
else:
    # 直接使用原文件（包括 .wav）
    process_path = temp_path
```

### 前端（useRecorder.js）
- 使用 Web Audio API 生成 WAV 格式
- 文件扩展名：`.wav`
- 采样率：16kHz，单声道

## 兼容性分析

### ✅ 完全兼容！

两种方案可以同时存在，互不冲突：

1. **前端生成 WAV**：
   - 前端发送 `.wav` 文件
   - 后端检测到 `.wav` 扩展名
   - **不会触发转换逻辑**（因为 `.wav` 不在转换列表中）
   - 直接使用 FunASR 处理
   - **不需要 ffmpeg**

2. **前端生成 WebM**（如果浏览器不支持 Web Audio API）：
   - 前端发送 `.webm` 文件
   - 后端检测到 `.webm` 扩展名
   - **触发转换逻辑**
   - 使用 ffmpeg 转换为 WAV
   - **需要 ffmpeg**

## 工作流程

```
前端录音
  ↓
尝试使用 Web Audio API 生成 WAV
  ↓
成功？
  ├─ 是 → 发送 .wav → 后端直接处理 ✅
  └─ 否 → fallback 到 MediaRecorder → 发送 .webm → 后端用 ffmpeg 转换 ✅
```

## 优势

### 最佳情况（前端 WAV + 后端有 ffmpeg）
- ✅ 前端生成 WAV，后端直接处理（最快）
- ✅ 如果前端失败，后端有 ffmpeg 兜底（最稳定）
- ✅ 支持所有浏览器和场景

### 次优情况（仅前端 WAV）
- ✅ 大多数现代浏览器支持 Web Audio API
- ⚠️ 老旧浏览器可能不支持

### 次优情况（仅后端 ffmpeg）
- ✅ 支持所有浏览器
- ⚠️ 需要后端转换，稍慢

## 测试验证

### 验证前端 WAV 生成

1. 打开浏览器控制台
2. 开始录音
3. 停止录音
4. 查看控制台输出：
   ```
   开始录音（WAV 格式）
   录音完成，采样点数: xxxxx
   生成 WAV 文件，大小: xxxxx 字节
   ```

### 验证后端处理

1. 查看后端日志
2. 如果前端发送 WAV：
   ```
   接收到音频文件: blob.wav
   文件保存成功，大小: xxxxx 字节
   开始调用 FunASR 模型，处理文件: /path/to/temp_audio_xxx.wav
   识别成功，文本: xxxxx
   ```

3. 如果前端发送 WebM：
   ```
   接收到音频文件: blob.webm
   检测到 .webm 格式，需要转换为 WAV...
   音频格式转换成功: /path/to/temp_audio_xxx.webm -> /path/to/converted_xxx.wav
   开始调用 FunASR 模型，处理文件: /path/to/converted_xxx.wav
   识别成功，文本: xxxxx
   ```

## 建议配置

### 开发环境
```env
# 前端会生成 WAV，不需要 ffmpeg
# 但安装了也没关系，作为备用
```

### 生产环境
```env
# 强烈建议安装 ffmpeg
# 确保所有场景都能正常工作
```

## 故障排查

### 前端 WAV 生成失败
**症状**：浏览器控制台没有 "生成 WAV 文件" 日志

**原因**：
- 浏览器不支持 Web Audio API
- 浏览器版本过旧

**解决**：
- 使用现代浏览器（Chrome 90+, Edge 90+, Firefox 88+）
- 或者依赖后端 ffmpeg 转换

### 后端转换失败
**症状**：错误提示 "ffmpeg 未安装"

**原因**：
- ffmpeg 未安装
- ffmpeg 未添加到系统 PATH
- 需要重启命令行窗口

**解决**：
1. 验证安装：打开**新的**命令行窗口，运行 `ffmpeg -version`
2. 如果失败，重新运行 `setup_ffmpeg.bat`
3. 重启 Dolphin ASR 服务

## 总结

✅ **两种方案完全兼容，可以同时使用**

- 前端优先使用 WAV（快速、无需转换）
- 后端有 ffmpeg 兜底（稳定、支持所有格式）
- 这是最佳的容错配置！
