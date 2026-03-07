# FFmpeg 自动安装脚本
# 需要管理员权限运行

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   FFmpeg 自动安装脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ffmpegDir = "C:\ffmpeg"
$ffmpegBin = "$ffmpegDir\bin"
$downloadUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zipFile = "$env:TEMP\ffmpeg.zip"

# 检查是否已安装
try {
    $version = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✓ FFmpeg 已安装: $version" -ForegroundColor Green
    Write-Host ""
    Write-Host "如需重新安装，请先删除 C:\ffmpeg 目录" -ForegroundColor Yellow
    pause
    exit 0
} catch {
    Write-Host "FFmpeg 未安装，开始安装..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[1/4] 下载 FFmpeg..." -ForegroundColor Yellow
Write-Host "      下载地址: $downloadUrl" -ForegroundColor Gray
Write-Host "      文件大小: 约 80MB，请耐心等待..." -ForegroundColor Gray
Write-Host ""

try {
    # 下载 ffmpeg
    Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
    Write-Host "✓ 下载完成" -ForegroundColor Green
} catch {
    Write-Host "✗ 下载失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动下载并安装:" -ForegroundColor Yellow
    Write-Host "1. 访问: https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor Yellow
    Write-Host "2. 下载: ffmpeg-release-essentials.zip" -ForegroundColor Yellow
    Write-Host "3. 解压到: C:\ffmpeg" -ForegroundColor Yellow
    Write-Host "4. 添加到 PATH: C:\ffmpeg\bin" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "[2/4] 解压文件..." -ForegroundColor Yellow

try {
    # 创建目标目录
    if (Test-Path $ffmpegDir) {
        Remove-Item $ffmpegDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $ffmpegDir -Force | Out-Null

    # 解压
    Expand-Archive -Path $zipFile -DestinationPath $env:TEMP -Force

    # 查找解压后的目录
    $extractedDir = Get-ChildItem "$env:TEMP\ffmpeg-*" -Directory | Select-Object -First 1

    # 移动文件
    Copy-Item "$($extractedDir.FullName)\*" -Destination $ffmpegDir -Recurse -Force

    Write-Host "✓ 解压完成" -ForegroundColor Green
} catch {
    Write-Host "✗ 解压失败: $_" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "[3/4] 添加到系统 PATH..." -ForegroundColor Yellow

try {
    # 获取当前系统 PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

    # 检查是否已存在
    if ($currentPath -notlike "*$ffmpegBin*") {
        # 添加到 PATH
        $newPath = "$currentPath;$ffmpegBin"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")

        # 更新当前会话的 PATH
        $env:Path = "$env:Path;$ffmpegBin"

        Write-Host "✓ 已添加到系统 PATH" -ForegroundColor Green
    } else {
        Write-Host "✓ PATH 已存在，跳过" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ 添加 PATH 失败: $_" -ForegroundColor Red
    Write-Host "   请手动添加: $ffmpegBin" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/4] 验证安装..." -ForegroundColor Yellow

# 刷新环境变量
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

try {
    $version = & "$ffmpegBin\ffmpeg.exe" -version 2>&1 | Select-Object -First 1
    Write-Host "✓ FFmpeg 安装成功!" -ForegroundColor Green
    Write-Host "  版本: $version" -ForegroundColor Gray
} catch {
    Write-Host "✗ 验证失败: $_" -ForegroundColor Red
    Write-Host "   请重启命令行窗口后再试" -ForegroundColor Yellow
}

# 清理临时文件
Write-Host ""
Write-Host "清理临时文件..." -ForegroundColor Yellow
Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
Remove-Item "$env:TEMP\ffmpeg-*" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "1. 重启 Dolphin ASR 服务" -ForegroundColor White
Write-Host "2. 重新测试语音识别功能" -ForegroundColor White
Write-Host ""
pause
