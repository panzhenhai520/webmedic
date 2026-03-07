#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transcript Service
转写片段管理服务
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app.models import TranscriptSegment, EncounterSession


class TranscriptService:
    """转写片段服务类"""

    @staticmethod
    def create_segment(
        db: Session,
        session_id: int,
        speaker_role: str,
        audio_file_path: str,
        transcript_text: str,
        start_time_ms: int = None,
        end_time_ms: int = None
    ) -> TranscriptSegment:
        """
        创建转写片段

        Args:
            db: 数据库会话
            session_id: 会话ID
            speaker_role: 说话人角色 (doctor/patient)
            audio_file_path: 音频文件路径
            transcript_text: 转写文本
            start_time_ms: 开始时间(毫秒)
            end_time_ms: 结束时间(毫秒)

        Returns:
            创建的转写片段对象

        Raises:
            ValueError: 如果会话不存在或参数无效
        """
        # 验证会话是否存在
        session = db.query(EncounterSession).filter(
            EncounterSession.id == session_id
        ).first()
        if not session:
            raise ValueError(f"会话ID {session_id} 不存在")

        # 验证说话人角色
        if speaker_role not in ["doctor", "patient"]:
            raise ValueError(f"无效的说话人角色: {speaker_role}")

        # 创建转写片段
        segment = TranscriptSegment(
            session_id=session_id,
            speaker_role=speaker_role,
            audio_file_path=audio_file_path,
            transcript_text=transcript_text,
            start_time_ms=start_time_ms,
            end_time_ms=end_time_ms,
            status="done"
        )

        db.add(segment)
        db.commit()
        db.refresh(segment)

        return segment

    @staticmethod
    def get_segments_by_session(
        db: Session,
        session_id: int
    ) -> list[TranscriptSegment]:
        """
        获取会话的所有转写片段

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            转写片段列表
        """
        segments = db.query(TranscriptSegment).filter(
            TranscriptSegment.session_id == session_id
        ).order_by(TranscriptSegment.created_at).all()

        return segments

    @staticmethod
    def get_segment_by_id(
        db: Session,
        segment_id: int
    ) -> TranscriptSegment:
        """
        根据ID获取转写片段

        Args:
            db: 数据库会话
            segment_id: 片段ID

        Returns:
            转写片段对象

        Raises:
            ValueError: 如果片段不存在
        """
        segment = db.query(TranscriptSegment).filter(
            TranscriptSegment.id == segment_id
        ).first()

        if not segment:
            raise ValueError(f"转写片段ID {segment_id} 不存在")

        return segment
