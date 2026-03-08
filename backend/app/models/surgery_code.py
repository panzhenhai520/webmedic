#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Surgery Code Model
手术编码表模型
"""

from sqlalchemy import Column, BigInteger, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.db.base import Base


class SurgeryCode(Base):
    """手术编码表"""
    __tablename__ = "surgery_codes"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="编码ID")
    surgery_code = Column(String(20), nullable=False, unique=True, comment="手术编码")
    surgery_name = Column(String(200), nullable=False, comment="手术名称")
    category = Column(String(100), nullable=True, comment="手术分类")
    description = Column(Text, nullable=True, comment="描述说明")
    keywords = Column(Text, nullable=True, comment="搜索关键词(JSON数组)")
    difficulty_level = Column(String(20), nullable=True, comment="难度等级: 1/2/3/4级")
    status = Column(String(20), nullable=False, default="active", comment="状态: active/inactive")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 索引
    __table_args__ = (
        Index('idx_surgery_code', 'surgery_code'),
        Index('idx_surgery_name', 'surgery_name'),
        Index('idx_category', 'category'),
        Index('idx_status', 'status'),
    )

    def __repr__(self):
        return f"<SurgeryCode(id={self.id}, code={self.surgery_code}, name={self.surgery_name})>"
