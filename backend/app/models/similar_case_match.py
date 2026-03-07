#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Similar Case Match Model
相似病历匹配表模型
"""

from sqlalchemy import Column, BigInteger, Integer, DECIMAL, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class SimilarCaseMatch(Base):
    """相似病历匹配表"""
    __tablename__ = "similar_case_matches"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="匹配ID")
    session_id = Column(BigInteger, ForeignKey("encounter_sessions.id"), nullable=False, comment="会话ID")
    document_id = Column(BigInteger, ForeignKey("medical_documents.id"), nullable=False, comment="文档ID")
    score = Column(DECIMAL(10, 4), nullable=True, comment="相似度分数")
    reason_text = Column(Text, nullable=True, comment="匹配原因说明")
    rank_no = Column(Integer, nullable=False, comment="排名序号")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<SimilarCaseMatch(id={self.id}, session_id={self.session_id}, score={self.score})>"
