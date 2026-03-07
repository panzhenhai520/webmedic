#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EMR Draft Model
病历草稿表模型
"""

from sqlalchemy import Column, BigInteger, String, JSON, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class EmrDraft(Base):
    """病历草稿表"""
    __tablename__ = "emr_drafts"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="草稿ID")
    session_id = Column(BigInteger, ForeignKey("encounter_sessions.id"), nullable=False, comment="会话ID")
    draft_type = Column(String(50), nullable=False, comment="草稿类型")
    content_json = Column(JSON, nullable=True, comment="内容JSON")
    content_text = Column(Text, nullable=True, comment="内容文本")
    source_case_ids = Column(String(500), nullable=True, comment="来源病历ID列表")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<EmrDraft(id={self.id}, session_id={self.session_id}, type={self.draft_type})>"
