#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Schemas
会话相关的 Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SessionCreateRequest(BaseModel):
    """创建会话请求"""
    doctor_id: int = Field(..., description="医生ID")
    patient_id: int = Field(..., description="患者ID")


class SessionCreateResponse(BaseModel):
    """创建会话响应"""
    id: int = Field(..., description="会话ID")
    session_no: str = Field(..., description="会话编号")
    doctor_id: int = Field(..., description="医生ID")
    patient_id: int = Field(..., description="患者ID")
    status: str = Field(..., description="会话状态")
    started_at: Optional[datetime] = Field(None, description="开始时间")


class SessionDetailResponse(BaseModel):
    """会话详情响应"""
    id: int = Field(..., description="会话ID")
    session_no: str = Field(..., description="会话编号")
    doctor_id: int = Field(..., description="医生ID")
    patient_id: int = Field(..., description="患者ID")
    status: str = Field(..., description="会话状态")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    ended_at: Optional[datetime] = Field(None, description="结束时间")
    created_at: datetime = Field(..., description="创建时间")


class DoctorResponse(BaseModel):
    """医生信息响应"""
    id: int = Field(..., description="医生ID")
    doctor_name: str = Field(..., description="医生姓名")
    title: Optional[str] = Field(None, description="职称")
    department: Optional[str] = Field(None, description="科室")


class PatientResponse(BaseModel):
    """患者信息响应"""
    id: int = Field(..., description="患者ID")
    patient_name: str = Field(..., description="患者姓名")
    gender: str = Field(..., description="性别")
    age: int = Field(..., description="年龄")
    phone: Optional[str] = Field(None, description="联系电话")
    birthday: Optional[str] = Field(None, description="出生日期")
