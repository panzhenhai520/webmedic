#!/bin/bash
# Dolphin ASR 快速部署脚本（使用 FunASR）

echo "=== Dolphin ASR 部署脚本 ==="
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

echo "1. 创建虚拟环境..."
python3 -m venv dolphin_env
source dolphin_env/bin/activate

echo "2. 安装 FunASR..."
pip install funasr -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "3. 安装依赖..."
pip install modelscope torch torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "4. 下载模型（首次运行会自动下载）..."
echo "   模型: damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"

echo ""
echo "=== 部署完成 ==="
echo ""
echo "启动服务："
echo "  source dolphin_env/bin/activate"
echo "  funasr-server --model damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch --port 8000"
echo ""
echo "测试服务："
echo "  curl -X POST http://localhost:8000/asr -F 'file=@test.wav'"
