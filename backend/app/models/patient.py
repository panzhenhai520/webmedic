#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patient Model
患者表模型
"""

from sqlalchemy import Column, BigInteger, String, Integer, Date, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Patient(Base):
    """患者表"""
    __tablename__ = "patients"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="患者ID")
    patient_name = Column(String(100), nullable=False, comment="患者姓名")
    gender = Column(String(20), nullable=False, comment="性别")
    age = Column(Integer, nullable=False, comment="年龄")
    birthday = Column(Date, nullable=True, comment="出生日期")
    phone = Column(String(50), nullable=True, comment="联系电话")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.patient_name}, gender={self.gender}, age={self.age})>"
