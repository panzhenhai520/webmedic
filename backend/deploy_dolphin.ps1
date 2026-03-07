# Dolphin ASR 快速部署脚本（Windows）

Write-Host "=== Dolphin ASR 部署脚本 ===" -ForegroundColor Green
Write-Host ""

# 检查 Python 环境
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "错误: 未找到 Python，请先安装 Python 3.8+" -ForegroundColor Red
    exit 1
}

Write-Host "1. 创建虚拟环境..." -ForegroundColor Yellow
python -m venv dolphin_env
.\dolphin_env\Scripts\Activate.ps1

Write-Host "2. 安装 FunASR..." -ForegroundColor Yellow
pip install funasr -i https://pypi.tuna.tsinghua.edu.cn/simple

Write-Host "3. 安装依赖..." -ForegroundColor Yellow
pip install modelscope torch torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple

Write-Host "4. 下载模型（首次运行会自动下载）..." -ForegroundColor Yellow
Write-Host "   模型: damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"

Write-Host ""
Write-Host "=== 部署完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "启动服务：" -ForegroundColor Cyan
Write-Host "  .\dolphin_env\Scripts\Activate.ps1"
Write-Host "  funasr-server --model damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch --port 8000"
Write-Host ""
Write-Host "测试服务：" -ForegroundColor Cyan
Write-Host "  curl -X POST http://localhost:8000/asr -F 'file=@test.wav'"
