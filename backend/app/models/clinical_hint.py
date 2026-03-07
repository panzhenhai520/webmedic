#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clinical Hint Model
临床提示表模型
"""

from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class ClinicalHint(Base):
    """临床提示表"""
    __tablename__ = "clinical_hints"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="提示ID")
    session_id = Column(BigInteger, ForeignKey("encounter_sessions.id"), nullable=False, comment="会话ID")
    hint_type = Column(String(50), nullable=False, comment="提示类型: warning/question/exam")
    hint_title = Column(String(255), nullable=True, comment="提示标题")
    hint_content = Column(Text, nullable=False, comment="提示内容")
    severity = Column(String(20), nullable=True, default="info", comment="严重程度: info/warn/high")
    source_model = Column(String(100), nullable=True, comment="来源模型")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<ClinicalHint(id={self.id}, session_id={self.session_id}, type={self.hint_type})>"
