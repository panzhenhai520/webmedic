#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session History Schemas
会话历史相关的请求/响应模型
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class SessionListItem(BaseModel):
    """会话列表项"""
    id: int
    session_no: str
    status: str
    doctor_name: str
    doctor_title: str
    patient_name: str
    patient_gender: str
    patient_age: int
    transcript_count: int = 0  # 转写片段数量
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime


class SessionListRequest(BaseModel):
    """会话列表查询请求"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    status: Optional[str] = Field(default=None, description="状态过滤")


class SessionListResponse(BaseModel):
    """会话列表响应"""
    total: int
    page: int
    page_size: int
    sessions: List[SessionListItem]


class TranscriptItem(BaseModel):
    """转写片段项"""
    id: int
    speaker_role: str
    transcript_text: Optional[str]
    audio_file_path: Optional[str]
    start_time_ms: Optional[int]
    end_time_ms: Optional[int]
    status: str
    created_at: datetime


class SessionDetailWithTranscripts(BaseModel):
    """会话详情（含转写记录）"""
    id: int
    session_no: str
    doctor_id: int
    patient_id: int
    status: str
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    created_at: datetime
    transcripts: List[TranscriptItem]
    transcript_count: int
