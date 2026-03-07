#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doctor Model
医生表模型
"""

from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Doctor(Base):
    """医生表"""
    __tablename__ = "doctors"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="医生ID")
    doctor_name = Column(String(100), nullable=False, comment="医生姓名")
    title = Column(String(100), nullable=True, comment="职称")
    department = Column(String(100), nullable=True, comment="科室")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<Doctor(id={self.id}, name={self.doctor_name})>"
