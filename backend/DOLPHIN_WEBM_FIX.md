# Dolphin ASR WebM 格式支持问题解决方案

## 问题说明

浏览器录音默认生成 WebM 格式，但 FunASR 模型需要 ffmpeg 来处理 WebM 格式。

## 解决方案

### 方案 1：安装 ffmpeg（推荐）

1. **下载 ffmpeg**：
   - 访问：https://www.gyan.dev/ffmpeg/builds/
   - 下载：ffmpeg-release-essentials.zip

2. **解压并配置**：
   ```bash
   # 解压到 C:\ffmpeg
   # 添加到系统 PATH：C:\ffmpeg\bin
   ```

3. **验证安装**：
   ```bash
   ffmpeg -version
   ```

4. **重启 Dolphin 服务**

### 方案 2：使用 Mock 模式测试（临时）

如果暂时无法安装 ffmpeg，可以先使用 Mock 模式测试其他功能：

1. 在前端切换引擎为 "Mock 模式"
2. 或者在 `.env` 中设置：
   ```env
   ASR_USE_MOCK=true
   ```

### 方案 3：前端转换为 WAV（实验性）

前端已修改为尝试使用浏览器支持的最佳格式，但大多数浏览器仍然只支持 WebM。

## 推荐操作流程

1. **立即测试**：先使用 Mock 模式验证其他功能
2. **安装 ffmpeg**：按照方案 1 安装 ffmpeg
3. **切换回 Dolphin**：安装完成后切换回 Dolphin 引擎

## ffmpeg 快速安装（Windows）

```powershell
# 使用 Chocolatey（如果已安装）
choco install ffmpeg

# 或使用 Scoop
scoop install ffmpeg
```

安装后重启终端和 Dolphin 服务即可。
