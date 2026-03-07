# WebMedic 当前音频格式配置

## ✅ 确认：默认使用 WAV 格式

### 证据 1：前端代码
**文件**：`frontend/src/composables/useRecorder.js`
```javascript
/**
 * 录音功能 Composable
 * 使用 Web Audio API 直接生成 WAV 格式，无需后端转换
 */
```

**实现**：
- 使用 Web Audio API（不是 MediaRecorder）
- 直接生成 16kHz 单声道 WAV 格式
- 使用自定义 WAV 编码器（`wavEncoder.js`）

### 证据 2：上传文件名
**文件**：`frontend/src/components/workbench/ControlPanel.vue` 第 353 行
```javascript
formData.append('audio_file', audioBlob, 'recording.wav')
```

### 证据 3：实际上传的文件
**最近上传的文件**（全部是 WAV）：
```
-rw-r--r-- 1 Administrator 197121  41K Mar  7 18:24 ca971537-3691-41cd-b50c-388ec1577319.wav
-rw-r--r-- 1 Administrator 197121 281K Mar  7 18:24 bc55ba82-5ee5-430a-af13-f01b69c838fe.wav
-rw-r--r-- 1 Administrator 197121 225K Mar  7 18:22 2df2f14a-df0f-4b44-9fdf-1bb1f175cf50.wav
-rw-r--r-- 1 Administrator 197121 281K Mar  7 18:16 ad178539-9abb-489a-ae1a-4661ad025030.wav
```

### 证据 4：后端处理逻辑
**文件**：`backend/dolphin_server.py` 第 153 行
```python
if file_ext.lower() in ['.webm', '.ogg', '.m4a', '.mp4']:
    # 需要转换
else:
    # 直接处理（包括 .wav）
```

**结论**：`.wav` 文件**不会触发转换**，直接由 FunASR 处理。

## 工作流程

```
用户点击录音
    ↓
前端：Web Audio API 捕获音频
    ↓
前端：wavEncoder.js 编码为 WAV
    ↓
前端：生成 Blob（audio/wav）
    ↓
前端：FormData 上传（文件名：recording.wav）
    ↓
后端：接收文件，检测扩展名 = .wav
    ↓
后端：跳过格式转换
    ↓
后端：直接调用 FunASR 识别
    ↓
返回识别结果
```

## 优势

### 1. 性能优势
- ✅ 无需后端转换（节省时间）
- ✅ 无需 ffmpeg（降低依赖）
- ✅ 直接处理（减少 I/O）

### 2. 兼容性优势
- ✅ WAV 是标准格式（FunASR 原生支持）
- ✅ 16kHz 采样率（语音识别最佳）
- ✅ 单声道（减少文件大小）

### 3. 稳定性优势
- ✅ 纯前端实现（减少后端依赖）
- ✅ 有 ffmpeg 兜底（支持老旧浏览器）
- ✅ 格式标准（避免编码问题）

## 浏览器兼容性

### 支持 Web Audio API 的浏览器（生成 WAV）
- ✅ Chrome 90+
- ✅ Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14.1+

### 不支持的浏览器（fallback 到 MediaRecorder）
- ⚠️ 老旧浏览器会生成 WebM
- ✅ 后端有 ffmpeg 可以转换

## 验证方法

### 方法 1：浏览器控制台
打开开发者工具，录音时查看日志：
```
开始录音（WAV 格式）
录音完成，采样点数: xxxxx
生成 WAV 文件，大小: xxxxx 字节
```

### 方法 2：网络请求
查看 Network 标签，上传请求的 Content-Type：
```
Content-Type: multipart/form-data
文件名：recording.wav
```

### 方法 3：后端日志
Dolphin ASR 服务日志：
```
接收到音频文件: recording.wav
保存到临时路径: ...temp_audio_xxxxx.wav
开始调用 FunASR 模型，处理文件: ...temp_audio_xxxxx.wav
识别成功，文本: xxxxx
```

**关键**：不应该出现 "检测到 .webm 格式，需要转换为 WAV" 这行日志。

## 总结

✅ **是的，默认使用 WAV 格式**

- 前端使用 Web Audio API 生成 WAV
- 文件名：`recording.wav`
- 后端直接处理，无需转换
- 性能最优，兼容性最好

---

**最后更新**：2026-03-07
**状态**：已验证，正常工作
