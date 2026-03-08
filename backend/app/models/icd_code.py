#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ICD Code Model
ICD疾病编码表模型
"""

from sqlalchemy import Column, BigInteger, String, Text, DateTime, Index
from sqlalchemy.sql import func
from app.db.base import Base


class ICDCode(Base):
    """ICD疾病编码表"""
    __tablename__ = "icd_codes"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="编码ID")
    icd_code = Column(String(20), nullable=False, unique=True, comment="ICD编码")
    icd_name_cn = Column(String(200), nullable=False, comment="中文名称")
    icd_name_en = Column(String(200), nullable=True, comment="英文名称")
    category = Column(String(100), nullable=True, comment="章节分类")
    description = Column(Text, nullable=True, comment="描述说明")
    keywords = Column(Text, nullable=True, comment="搜索关键词(JSON数组)")
    status = Column(String(20), nullable=False, default="active", comment="状态: active/inactive")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 索引
    __table_args__ = (
        Index('idx_icd_code', 'icd_code'),
        Index('idx_icd_name_cn', 'icd_name_cn'),
        Index('idx_category', 'category'),
        Index('idx_status', 'status'),
    )

    def __repr__(self):
        return f"<ICDCode(id={self.id}, code={self.icd_code}, name={self.icd_name_cn})>"
