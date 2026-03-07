#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transcript Segment Model
转写片段表模型
"""

from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class TranscriptSegment(Base):
    """转写片段表"""
    __tablename__ = "transcript_segments"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="片段ID")
    session_id = Column(BigInteger, ForeignKey("encounter_sessions.id"), nullable=False, comment="会话ID")
    speaker_role = Column(String(20), nullable=False, comment="说话人角色: doctor/patient")
    audio_file_path = Column(String(500), nullable=True, comment="音频文件路径")
    transcript_text = Column(Text, nullable=True, comment="转写文本")
    start_time_ms = Column(BigInteger, nullable=True, comment="开始时间(毫秒)")
    end_time_ms = Column(BigInteger, nullable=True, comment="结束时间(毫秒)")
    status = Column(String(20), nullable=False, default="done", comment="状态: pending/processing/done/failed")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<TranscriptSegment(id={self.id}, session_id={self.session_id}, speaker={self.speaker_role})>"
