@echo off
chcp 65001 >nul
echo ========================================
echo    FFmpeg 自动安装
echo ========================================
echo.
echo 此脚本将自动下载并安装 FFmpeg
echo 需要管理员权限
echo.
echo 按任意键继续...
pause >nul

echo.
echo 正在启动安装程序...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0setup_ffmpeg.ps1"

echo.
echo 安装完成！
echo.
pause
