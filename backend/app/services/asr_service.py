#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR Service
语音识别服务适配层
支持多种 ASR 引擎：Whisper、Dolphin
"""

import os
import logging
import requests
from typing import Optional
from sqlalchemy.orm import Session
from openai import OpenAI

logger = logging.getLogger(__name__)


class ASRService:
    """
    ASR 服务适配层
    第一版使用 mock 转写结果
    未来可以平滑切换到 Dolphin ASR
    """

    # Mock 对话流程：医生问题和患者回答成对出现
    MOCK_DIALOGUE = [
        # 第0轮：开场问诊
        {
            "doctor": "您好，请问哪里不舒服？",
            "patient": "医生您好，我最近颈部疼痛，还有点头晕。"
        },
        # 第1轮：询问病程
        {
            "doctor": "这种情况持续多久了？",
            "patient": "大概有三四天了。"
        },
        # 第2轮：询问伴随症状
        {
            "doctor": "有没有其他症状？",
            "patient": "还有点恶心，睡眠也不太好。"
        },
        # 第3轮：询问既往史
        {
            "doctor": "之前有没有类似的情况？",
            "patient": "之前没有过这种情况。"
        },
        # 第4轮：询问检查史
        {
            "doctor": "有没有做过相关检查？",
            "patient": "还没有做过检查。"
        },
        # 第5轮：询问慢性病史
        {
            "doctor": "平时有什么慢性病吗？",
            "patient": "没有慢性病，身体一直挺好的。"
        },
        # 第6轮：询问过敏史
        {
            "doctor": "对什么药物过敏吗？",
            "patient": "对青霉素过敏。"
        },
        # 第7轮：体格检查
        {
            "doctor": "我给您做个体格检查。颈部活动受限，颈椎棘突压痛明显，双侧肩部肌肉紧张。",
            "patient": "好的医生，我配合检查。"
        },
        # 第8轮：生命体征
        {
            "doctor": "血压130/85mmHg，心率78次/分，心肺听诊未见异常。",
            "patient": "嗯，颈部确实很疼，转头都困难。"
        },
        # 第9轮：初步诊断
        {
            "doctor": "根据您的症状和体格检查，初步诊断为颈椎病，可能伴有颈性眩晕。",
            "patient": "明白了，我会注意休息的。"
        },
        # 第10轮：检查建议
        {
            "doctor": "建议您做个颈椎X光片或者CT检查，看看颈椎的具体情况。",
            "patient": "好的，我这就去做检查。"
        },
        # 第11轮：辅助检查
        {
            "doctor": "另外建议查一下血常规和血脂，排除其他问题。",
            "patient": "好的医生，我都听您的。"
        },
        # 第12轮：医嘱
        {
            "doctor": "您这个情况需要注意休息，避免长时间低头。如果头晕加重或者出现肢体麻木，要及时复诊。",
            "patient": "好的，谢谢医生，我会注意的。"
        }
    ]

    @staticmethod
    def transcribe_audio(
        audio_file_path: str,
        speaker_role: str,
        session_id: int,
        db: Session
    ) -> str:
        """
        转写音频文件

        Args:
            audio_file_path: 音频文件路径
            speaker_role: 说话人角色 (doctor/patient)
            session_id: 会话ID
            db: 数据库会话

        Returns:
            转写文本

        Note:
            根据配置选择 ASR 引擎：
            - ASR_USE_MOCK=true: 使用 Mock 模式
            - ASR_ENGINE=whisper: 使用 OpenAI Whisper
            - ASR_ENGINE=dolphin: 使用清华 Dolphin
        """
        from app.core.config import settings

        # 检查音频文件大小
        file_size = os.path.getsize(audio_file_path) if os.path.exists(audio_file_path) else 0

        # 如果文件大小小于 1KB，认为是模拟数据
        if file_size < 1024 or settings.ASR_USE_MOCK:
            logger.info(f"音频文件大小 {file_size} 字节，使用 Mock 模式")
            return ASRService._mock_transcribe(session_id, speaker_role, db)

        # 根据配置选择 ASR 引擎
        logger.info(f"音频文件大小 {file_size} 字节，使用 {settings.ASR_ENGINE.upper()} 引擎")

        if settings.ASR_ENGINE.lower() == "dolphin":
            return ASRService._dolphin_transcribe(audio_file_path)
        else:  # 默认使用 whisper
            return ASRService._whisper_transcribe(audio_file_path)

    @staticmethod
    def _mock_transcribe(session_id: int, speaker_role: str, db: Session) -> str:
        """
        Mock 转写：按对话轮次返回预设文本

        Args:
            session_id: 会话ID
            speaker_role: 说话人角色
            db: 数据库会话

        Returns:
            转写文本
        """
        # 查询当前会话已有的转写片段数量，确定对话进度
        from app.models.transcript_segment import TranscriptSegment
        segment_count = db.query(TranscriptSegment).filter(
            TranscriptSegment.session_id == session_id
        ).count()

        # 计算当前对话轮次（每轮包含医生和患者各一次发言）
        dialogue_round = segment_count // 2

        # 确保不超出预设对话范围
        if dialogue_round >= len(ASRService.MOCK_DIALOGUE):
            dialogue_round = len(ASRService.MOCK_DIALOGUE) - 1

        # 根据说话人角色和对话轮次返回对应文本
        current_dialogue = ASRService.MOCK_DIALOGUE[dialogue_round]

        if speaker_role == "doctor":
            return current_dialogue["doctor"]
        else:  # patient
            return current_dialogue["patient"]

    @staticmethod
    def _whisper_transcribe(audio_file_path: str) -> str:
        """
        Whisper 转写：调用 OpenAI Whisper API

        Args:
            audio_file_path: 音频文件路径

        Returns:
            转写文本
        """
        try:
            from app.core.config import settings

            # 检查是否配置了 OpenAI API Key
            if not settings.OPENAI_API_KEY:
                logger.warning("未配置 OPENAI_API_KEY")
                return "[未配置 Whisper API Key]"

            # 初始化 OpenAI 客户端
            client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )

            # 调用 Whisper API
            with open(audio_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="zh"  # 指定中文
                )

            logger.info(f"Whisper 转写成功: {transcript.text}")
            return transcript.text

        except Exception as e:
            logger.error(f"Whisper API 调用失败: {e}")
            return f"[Whisper 识别失败: {str(e)}]"

    @staticmethod
    def _dolphin_transcribe(audio_file_path: str) -> str:
        """
        Dolphin 转写：调用清华 Dolphin ASR 服务

        Args:
            audio_file_path: 音频文件路径

        Returns:
            转写文本

        Note:
            Dolphin 可以是本地部署的服务或远程 API
            需要根据实际部署情况调整请求格式
        """
        try:
            from app.core.config import settings

            # 检查是否配置了 Dolphin 服务地址
            if not settings.DOLPHIN_API_URL:
                logger.warning("未配置 DOLPHIN_API_URL")
                return "[���配置 Dolphin 服务地址]"

            logger.info(f"准备调用 Dolphin API: {settings.DOLPHIN_API_URL}")
            logger.info(f"音频文件路径: {audio_file_path}")
            logger.info(f"文件大小: {os.path.getsize(audio_file_path)} 字节")

            # 准备请求头（避免中文字符）
            headers = {}
            # 只有在 API Key 存在且不包含注释符号时才添加
            if settings.DOLPHIN_API_KEY and not settings.DOLPHIN_API_KEY.startswith("#"):
                api_key = settings.DOLPHIN_API_KEY.strip()
                if api_key:  # 确保不是空字符串
                    headers["Authorization"] = f"Bearer {api_key}"
                    logger.info("已添加 Authorization 头")
            else:
                logger.info("未配置 DOLPHIN_API_KEY，跳过认证")

            # 读取音频文件并上传
            with open(audio_file_path, "rb") as audio_file:
                # 使用简单的 ASCII 文件名和明确的 MIME 类型
                files = {
                    "file": ("audio.webm", audio_file, "audio/webm")
                }

                logger.info("开始发送请求到 Dolphin 服务...")

                # 调用 Dolphin API
                response = requests.post(
                    settings.DOLPHIN_API_URL,
                    files=files,
                    headers=headers,
                    timeout=30
                )

            logger.info(f"Dolphin API 响应状态码: {response.status_code}")

            # 检查响应
            if response.status_code == 200:
                result = response.json()
                # 根据实际 API 响应格式提取文本
                text = result.get("text", "") or result.get("result", "")
                logger.info(f"Dolphin 转写成功: {text}")
                return text
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text[:200]}"
                logger.error(f"Dolphin API 返回错误: {error_msg}")
                return f"[Dolphin 识别失败: {error_msg}]"

        except requests.exceptions.Timeout:
            logger.error("Dolphin API 请求超时")
            return "[Dolphin 识别超时]"
        except requests.exceptions.ConnectionError as e:
            logger.error(f"无法连接到 Dolphin 服务: {e}")
            return "[无法连接到 Dolphin 服务]"
        except Exception as e:
            logger.error(f"Dolphin API 调用失败: {e}", exc_info=True)
            return f"[Dolphin 识别失败: {str(e)}]"

    @staticmethod
    def is_available() -> bool:
        """
        检查 ASR 服务是否可用

        Returns:
            是否可用
        """
        # Mock 版本始终返回 True
        # 未来可以检查 Dolphin 服务状态
        return True
