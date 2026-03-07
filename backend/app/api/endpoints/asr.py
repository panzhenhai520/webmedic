#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR Endpoints
ASR 转写接口
"""

import os
import uuid
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from app.core.response import success_response, error_response
from app.db.session import get_db
from app.services.asr_service import ASRService
from app.services.transcript_service import TranscriptService
from app.schemas.asr import TranscribeResponse

router = APIRouter()

# 音频文件上传目录
UPLOAD_DIR = "uploads/audio"


@router.post("/transcribe", response_model=dict)
async def transcribe_audio(
    session_id: int = Form(...),
    speaker_role: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    转写音频文件

    Args:
        session_id: 会话ID
        speaker_role: 说话人角色 (doctor/patient)
        audio_file: 音频文件
        db: 数据库会话

    Returns:
        转写结果
    """
    try:
        # 验证说话人角色
        if speaker_role not in ["doctor", "patient"]:
            return error_response(message=f"无效的说话人角色: {speaker_role}")

        # 确保上传目录存在
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # 生成唯一文件名
        file_extension = os.path.splitext(audio_file.filename)[1] or ".webm"
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # 保存音频文件
        with open(file_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)

        # 调用 ASR 服务进行转写
        transcript_text = ASRService.transcribe_audio(
            audio_file_path=file_path,
            speaker_role=speaker_role,
            session_id=session_id,
            db=db
        )

        # 创建转写片段记录
        segment = TranscriptService.create_segment(
            db=db,
            session_id=session_id,
            speaker_role=speaker_role,
            audio_file_path=file_path,
            transcript_text=transcript_text
        )

        # 构建响应
        response_data = TranscribeResponse(
            segment_id=segment.id,
            speaker_role=segment.speaker_role,
            transcript_text=segment.transcript_text
        )

        return success_response(
            data=response_data.model_dump(),
            message="转写成功"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"转写失败: {str(e)}")


@router.get("/segments/{session_id}", response_model=dict)
async def get_session_segments(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    获取会话的所有转写片段

    Args:
        session_id: 会话ID
        db: 数据库会话

    Returns:
        转写片段列表
    """
    try:
        segments = TranscriptService.get_segments_by_session(
            db=db,
            session_id=session_id
        )

        segments_data = [
            {
                "id": seg.id,
                "session_id": seg.session_id,
                "speaker_role": seg.speaker_role,
                "transcript_text": seg.transcript_text,
                "created_at": seg.created_at.isoformat() if seg.created_at else None
            }
            for seg in segments
        ]

        return success_response(
            data=segments_data,
            message="获取转写片段成功"
        )

    except Exception as e:
        return error_response(message=f"获取转写片段失败: {str(e)}")
