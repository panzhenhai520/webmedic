#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Encounter Structured Record Schemas
结构化病历相关的 Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StructuredRecordData(BaseModel):
    """结构化病历数据模型"""
    chief_complaint: Optional[str] = Field(None, description="主诉")
    present_illness: Optional[str] = Field(None, description="现病史")
    past_history: Optional[str] = Field(None, description="既往史")
    allergy_history: Optional[str] = Field(None, description="过敏史")
    physical_exam: Optional[str] = Field(None, description="体格检查")
    preliminary_diagnosis: Optional[str] = Field(None, description="初步诊断")
    suggested_exams: Optional[str] = Field(None, description="建议检查")
    warning_flags: Optional[str] = Field(None, description="风险标记")


class ExtractRequest(BaseModel):
    """抽取请求（可选，用于未来扩展）"""
    force_refresh: bool = Field(False, description="是否强制重新抽取")


class ExtractResponse(BaseModel):
    """抽取响应"""
    record_id: int = Field(..., description="结构化病历ID")
    session_id: int = Field(..., description="会话ID")
    structured_record: StructuredRecordData = Field(..., description="结构化病历数据")
    created_at: datetime = Field(..., description="创建时间")


class StructuredRecordResponse(BaseModel):
    """结构化病历详情响应"""
    id: int = Field(..., description="记录ID")
    session_id: int = Field(..., description="会话ID")
    schema_version: str = Field(..., description="Schema版本")
    chief_complaint: Optional[str] = Field(None, description="主诉")
    present_illness: Optional[str] = Field(None, description="现病史")
    past_history: Optional[str] = Field(None, description="既往史")
    allergy_history: Optional[str] = Field(None, description="过敏史")
    physical_exam: Optional[str] = Field(None, description="体格检查")
    preliminary_diagnosis: Optional[str] = Field(None, description="初步诊断")
    suggested_exams: Optional[str] = Field(None, description="建议检查")
    warning_flags: Optional[str] = Field(None, description="风险标记")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
