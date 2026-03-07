#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Medical Document Model
病历文档表模型
"""

from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class MedicalDocument(Base):
    """病历文档表"""
    __tablename__ = "medical_documents"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="文档ID")
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_path = Column(String(500), nullable=False, comment="文件路径")
    file_hash = Column(String(128), nullable=True, comment="文件哈希值")
    parse_status = Column(String(20), nullable=False, default="pending", comment="解析状态: pending/parsing/done/failed")
    index_status = Column(String(20), nullable=False, default="pending", comment="索引状态: pending/indexing/done/failed")
    source_type = Column(String(50), nullable=True, default="pdf", comment="来源类型")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<MedicalDocument(id={self.id}, file_name={self.file_name})>"
