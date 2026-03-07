#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Draft Schemas
病历草稿相关的 Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApplySimilarPlanRequest(BaseModel):
    """应用相似方案请求"""
    source_document_id: int = Field(..., description="来源文档ID")


class DraftContent(BaseModel):
    """草稿内容"""
    chief_complaint: Optional[str] = Field(None, description="主诉")
    present_illness: Optional[str] = Field(None, description="现病史")
    past_history: Optional[str] = Field(None, description="既往史")
    allergy_history: Optional[str] = Field(None, description="过敏史")
    physical_exam: Optional[str] = Field(None, description="体格检查")
    preliminary_diagnosis: Optional[str] = Field(None, description="初步诊断")
    suggested_exams: Optional[str] = Field(None, description="建议检查")
    treatment_plan: Optional[str] = Field(None, description="治疗方案")


class DraftResponse(BaseModel):
    """草稿响应"""
    draft_id: int = Field(..., description="草稿ID")
    session_id: int = Field(..., description="会话ID")
    draft_type: str = Field(..., description="草稿类型")
    content: DraftContent = Field(..., description="草稿内容")
    source_case_ids: Optional[str] = Field(None, description="来源病历ID")
    created_at: datetime = Field(..., description="创建时间")
