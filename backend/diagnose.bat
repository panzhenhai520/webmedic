@echo off
chcp 65001 >nul
echo ========================================
echo    WebMedic 诊断工具
echo ========================================
echo.

echo [1/4] 检查 ffmpeg 状态...
where ffmpeg >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ ffmpeg 在 PATH 中
    ffmpeg -version 2>nul | findstr "ffmpeg version"
) else (
    echo ✗ ffmpeg 不在 PATH 中
    echo   请重启命令行窗口
)
echo.

echo [2/4] 检查前端代码...
findstr /C:"recording.wav" D:\webmedic\frontend\src\components\workbench\ControlPanel.vue >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 前端代码已更新（使用 recording.wav）
) else (
    echo ✗ 前端代码未更新（仍使用 recording.webm）
    echo   请确认文件已保存
)
echo.

echo [3/4] 检查最近上传的文件...
echo 最近 3 个上传的文件：
dir /B /O-D D:\webmedic\backend\uploads\audio\*.* 2>nul | head -n 3
echo.

echo [4/4] 检查进程状态...
echo 前端进程（npm/node）：
tasklist | findstr /I "node.exe" | find /C "node.exe"
echo.
echo Dolphin ASR 进程（python）：
tasklist | findstr /I "python.exe" | find /C "python.exe"
echo.

echo ========================================
echo 建议操作
echo ========================================
echo.
echo 1. 如果 ffmpeg 不在 PATH：
echo    - 关闭所有命令行窗口
echo    - 打开新的命令行窗口
echo    - 重新启动 Dolphin ASR
echo.
echo 2. 如果前端代码未更新：
echo    - 确认 ControlPanel.vue 已保存
echo    - 重启前端服务（Ctrl+C 然后 npm run dev）
echo.
echo 3. 如果仍有问题：
echo    - 查看浏览器控制台日志
echo    - 查看 Dolphin ASR 窗口日志
echo.
pause
