#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structured Record Model
结构化病历表模型
"""

from sqlalchemy import Column, BigInteger, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class StructuredRecord(Base):
    """结构化病历表"""
    __tablename__ = "structured_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")
    session_id = Column(BigInteger, ForeignKey("encounter_sessions.id"), nullable=False, comment="会话ID")
    schema_version = Column(String(50), nullable=False, comment="Schema版本")
    raw_json = Column(JSON, nullable=False, comment="原始JSON数据")
    chief_complaint = Column(Text, nullable=True, comment="主诉")
    present_illness = Column(Text, nullable=True, comment="现病史")
    past_history = Column(Text, nullable=True, comment="既往史")
    allergy_history = Column(Text, nullable=True, comment="过敏史")
    physical_exam = Column(Text, nullable=True, comment="体格检查")
    preliminary_diagnosis = Column(Text, nullable=True, comment="初步诊断")
    suggested_exams = Column(Text, nullable=True, comment="建议检查")
    warning_flags = Column(Text, nullable=True, comment="风险提示")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<StructuredRecord(id={self.id}, session_id={self.session_id})>"
