@echo off
chcp 65001 >nul
echo ========================================
echo    FFmpeg 安装验证
echo ========================================
echo.

echo [1/3] 检查 ffmpeg 是否在 PATH 中...
where ffmpeg >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ ffmpeg 已在 PATH 中
    echo.
    echo 版本信息：
    ffmpeg -version | findstr "ffmpeg version"
    echo.
) else (
    echo ✗ ffmpeg 不在 PATH 中
    echo.
    echo 可能的原因：
    echo 1. ffmpeg 未安装
    echo 2. 未添加到系统 PATH
    echo 3. 需要重启命令行窗口
    echo.
)

echo [2/3] 检查 C:\ffmpeg\bin 目录...
if exist "C:\ffmpeg\bin\ffmpeg.exe" (
    echo ✓ ffmpeg.exe 存在于 C:\ffmpeg\bin
    echo.
) else (
    echo ✗ C:\ffmpeg\bin\ffmpeg.exe 不存在
    echo.
)

echo [3/3] 检查系统 PATH 配置...
echo %PATH% | findstr /i "ffmpeg" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ PATH 中包含 ffmpeg 路径
    echo.
) else (
    echo ✗ PATH 中不包含 ffmpeg 路径
    echo.
    echo 请手动添加 C:\ffmpeg\bin 到系统 PATH：
    echo 1. 右键"此电脑" - 属性 - 高级系统设置
    echo 2. 环境变量 - 系统变量 - Path - 编辑
    echo 3. 新建 - 输入: C:\ffmpeg\bin
    echo 4. 确定保存
    echo 5. 重启所有命令行窗口
    echo.
)

echo ========================================
echo 测试完成
echo ========================================
echo.
pause
