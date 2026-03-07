#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Encounter Session Model
问诊会话表模型
"""

from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class EncounterSession(Base):
    """问诊会话表"""
    __tablename__ = "encounter_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="会话ID")
    session_no = Column(String(64), nullable=False, unique=True, comment="会话编号")
    doctor_id = Column(BigInteger, ForeignKey("doctors.id"), nullable=False, comment="医生ID")
    patient_id = Column(BigInteger, ForeignKey("patients.id"), nullable=False, comment="患者ID")
    status = Column(String(20), nullable=False, default="created", comment="会话状态: created/started/ended")
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    ended_at = Column(DateTime, nullable=True, comment="结束时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self):
        return f"<EncounterSession(id={self.id}, session_no={self.session_no}, status={self.status})>"
