#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dolphin ASR Server
基于 FunASR 的语音识别服务
"""

import os
import logging
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from funasr import AutoModel

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
CORS(app)

# 全局模型变量
asr_model = None


def convert_audio_format(input_path, output_path):
    """
    转换音频格式为 WAV
    使用 ffmpeg 进行转换（必需）
    """
    try:
        import subprocess

        # 检查 ffmpeg 是否可用
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise FileNotFoundError(
                "ffmpeg 未安装或不在系统 PATH 中。\n"
                "请运行 setup_ffmpeg.bat 安装 ffmpeg，\n"
                "或访问 https://www.gyan.dev/ffmpeg/builds/ 手动安装。"
            )

        # 使用 ffmpeg 转换音频
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-ar', '16000',  # 采样率 16kHz
            '-ac', '1',      # 单声道
            '-y',            # 覆盖输出文件
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            logger.info(f"音频格式转换成功: {input_path} -> {output_path}")
            return True
        else:
            logger.error(f"ffmpeg 转换失败: {result.stderr}")
            raise RuntimeError(f"音频转换失败: {result.stderr}")

    except FileNotFoundError as e:
        logger.error(f"ffmpeg 未安装: {e}")
        raise
    except Exception as e:
        logger.error(f"音频格式转换失败: {e}")
        raise


def init_model():
    """初始化 ASR 模型"""
    global asr_model
    try:
        print("\n[1/2] 正在加载 FunASR 模型...")
        print("     模型: speech_paraformer-large")
        print("     设备: CPU")
        print("     首次运行会下载模型文件（约 200MB），请耐心等待...\n")

        # 使用 Paraformer 中文语音识别模型
        asr_model = AutoModel(
            model="damo/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
            device="cpu",
            disable_update=True  # 禁用自动更新检查
        )

        print("\n[2/2] ✓ FunASR 模型加载成功\n")
        logger.info("FunASR 模型加载成功")

    except Exception as e:
        print(f"\n✗ 模型加载失败: {e}\n")
        logger.error(f"模型加载失败: {e}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({"status": "OK", "model_loaded": asr_model is not None})


@app.route('/asr', methods=['POST'])
def transcribe():
    """语音识别接口"""
    try:
        # 检查模型是否已加载
        if asr_model is None:
            return jsonify({"error": "模型未加载"}), 500

        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({"error": "未找到音频文件"}), 400

        audio_file = request.files['file']

        # 检查文件名
        if audio_file.filename == '':
            return jsonify({"error": "文件名为空"}), 400

        # 保存临时文件（使用绝对路径）
        script_dir = os.path.dirname(os.path.abspath(__file__))
        uploads_dir = os.path.join(script_dir, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)

        # 保留原始文件扩展名
        import uuid
        file_ext = os.path.splitext(audio_file.filename)[1] or '.webm'
        temp_filename = f"temp_audio_{uuid.uuid4().hex[:8]}{file_ext}"
        temp_path = os.path.join(uploads_dir, temp_filename)

        logger.info(f"接收到音频文件: {audio_file.filename}")
        logger.info(f"保存到临时路径: {temp_path}")

        # 保存文件
        audio_file.save(temp_path)

        # 验证文件是否保存成功
        if not os.path.exists(temp_path):
            logger.error(f"文件保存失败: {temp_path}")
            return jsonify({"error": "文件保存失败"}), 500

        file_size = os.path.getsize(temp_path)
        logger.info(f"文件保存成功，大小: {file_size} 字节")

        # 检查文件格式，如果是 webm 或其他不支持的格式，尝试转换
        process_path = temp_path
        converted_path = None

        if file_ext.lower() in ['.webm', '.ogg', '.m4a', '.mp4']:
            logger.info(f"检测到 {file_ext} 格式，需要转换为 WAV...")
            converted_path = os.path.join(uploads_dir, f"converted_{uuid.uuid4().hex[:8]}.wav")

            try:
                if convert_audio_format(temp_path, converted_path):
                    process_path = converted_path
                    logger.info("格式转换成功，使用转换后的文件")
            except FileNotFoundError as e:
                # ffmpeg 未安装
                logger.error(f"格式转换失败: {e}")
                # 清理临时文件
                for path in [temp_path, converted_path]:
                    try:
                        if path and os.path.exists(path):
                            os.remove(path)
                    except:
                        pass
                return jsonify({
                    "error": "ffmpeg 未安装",
                    "detail": str(e),
                    "hint": "请运行 setup_ffmpeg.bat 安装 ffmpeg"
                }), 500
            except Exception as e:
                logger.error(f"格式转换失败: {e}")
                # 清理临时文件
                for path in [temp_path, converted_path]:
                    try:
                        if path and os.path.exists(path):
                            os.remove(path)
                    except:
                        pass
                return jsonify({
                    "error": "音频格式转换失败",
                    "detail": str(e),
                    "hint": "请确保 ffmpeg 已正确安装"
                }), 500

        # 调用模型进行识别
        logger.info(f"开始调用 FunASR 模型，处理文件: {process_path}")
        try:
            result = asr_model.generate(input=process_path)
            logger.info(f"模型返回结果类型: {type(result)}")
            logger.info(f"模型返回结果: {result}")
        except Exception as model_error:
            logger.error(f"FunASR 模型调用失败: {model_error}", exc_info=True)
            # 清理临时文件
            for path in [temp_path, converted_path]:
                try:
                    if path and os.path.exists(path):
                        os.remove(path)
                except:
                    pass
            return jsonify({
                "error": f"模型识别失败: {str(model_error)}",
                "hint": "可能是音频格式不支持或文件损坏"
            }), 500

        # 清理临时文件
        try:
            for path in [temp_path, converted_path]:
                if path and os.path.exists(path):
                    os.remove(path)
                    logger.info(f"已清理临时文件: {path}")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {e}")

        # 提取识别文本
        if result and len(result) > 0:
            text = result[0].get("text", "")
            logger.info(f"识别成功，文本: {text}")
            return jsonify({"text": text, "result": text})
        else:
            logger.error("模型返回空结果")
            return jsonify({"error": "识别失败，模型返回空结果"}), 500

    except Exception as e:
        logger.error(f"识别过程出错: {e}", exc_info=True)
        # 尝试清理临时文件
        try:
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    try:
        print("=" * 50)
        print("正在初始化 Dolphin ASR 服务...")
        print("=" * 50)

        # 初始化模型
        init_model()

        print("=" * 50)
        print("模型加载完成！")
        print("=" * 50)

        # 启动服务
        logger.info("启动 Dolphin ASR 服务...")
        logger.info("服务地址: http://0.0.0.0:8888")
        print("\n✓ 服务启动成功！")
        print("✓ 访问地址: http://localhost:8888")
        print("✓ 健康检查: http://localhost:8888/health")
        print("✓ 按 Ctrl+C 停止服务\n")

        app.run(host='0.0.0.0', port=8888, debug=False)

    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"\n✗ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按任意键退出...")
