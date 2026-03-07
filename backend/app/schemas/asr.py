#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASR Schemas
ASR 转写相关的 Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional


class TranscribeResponse(BaseModel):
    """转写响应"""
    segment_id: int = Field(..., description="转写片段ID")
    speaker_role: str = Field(..., description="说话人角色")
    transcript_text: str = Field(..., description="转写文本")


class TranscriptSegmentResponse(BaseModel):
    """转写片段详情响应"""
    id: int = Field(..., description="片段ID")
    session_id: int = Field(..., description="会话ID")
    speaker_role: str = Field(..., description="说话人角色")
    audio_file_path: Optional[str] = Field(None, description="音频文件路径")
    transcript_text: Optional[str] = Field(None, description="转写文本")
    start_time_ms: Optional[int] = Field(None, description="开始时间(毫秒)")
    end_time_ms: Optional[int] = Field(None, description="结束时间(毫秒)")
    status: str = Field(..., description="状态")
