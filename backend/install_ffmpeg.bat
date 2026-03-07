@echo off
chcp 65001 >nul
echo ========================================
echo    FFmpeg 安装指南
echo ========================================
echo.
echo FFmpeg 是处理音频/视频的必备工具
echo Dolphin ASR 需要 ffmpeg 来处理 WebM 格式
echo.
echo 安装步骤：
echo.
echo 1. 下载 ffmpeg
echo    访问: https://www.gyan.dev/ffmpeg/builds/
echo    下载: ffmpeg-release-essentials.zip
echo.
echo 2. 解压到 C:\ffmpeg
echo    确保目录结构为: C:\ffmpeg\bin\ffmpeg.exe
echo.
echo 3. 添加到系统 PATH
echo    - 右键"此电脑" - 属性 - 高级系统设置
echo    - 环境变量 - 系统变量 - Path - 编辑
echo    - 新建 - 输入: C:\ffmpeg\bin
echo    - 确定保存
echo.
echo 4. 验证安装
echo    打开新的命令行窗口，运行:
echo    ffmpeg -version
echo.
echo ========================================
echo 按任意键打开下载页面...
pause >nul
start https://www.gyan.dev/ffmpeg/builds/
