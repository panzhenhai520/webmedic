#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medical Vocabulary Model
医学词汇表模型
"""

from sqlalchemy import Column, BigInteger, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.db.base import Base


class MedicalVocabulary(Base):
    """医学词汇表"""
    __tablename__ = "medical_vocabulary"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="词汇ID")
    category = Column(String(50), nullable=False, comment="分类: body_parts/symptoms/diseases/directions")
    standard_name = Column(String(100), nullable=False, comment="标准名称")
    keywords = Column(Text, nullable=False, comment="关键词列表(JSON数组)")
    description = Column(Text, nullable=True, comment="描述说明")
    specialty = Column(String(50), nullable=True, comment="专科分类: 骨科/心内科/消化科等")
    status = Column(String(20), nullable=False, default="active", comment="状态: active/inactive")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 索引
    __table_args__ = (
        Index('idx_category', 'category'),
        Index('idx_standard_name', 'standard_name'),
        Index('idx_specialty', 'specialty'),
        Index('idx_status', 'status'),
    )

    def __repr__(self):
        return f"<MedicalVocabulary(id={self.id}, category={self.category}, name={self.standard_name})>"
