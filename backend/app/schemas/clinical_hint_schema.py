#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clinical Hint Schemas
临床提示相关的 Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class WarningItem(BaseModel):
    """风险提示项"""
    hint_title: str = Field(..., description="提示标题")
    hint_content: str = Field(..., description="提示内容")
    severity: str = Field(..., description="严重程度: info/warn/high")


class FollowupQuestionItem(BaseModel):
    """追问建议项"""
    question: str = Field(..., description="建议追问问题")
    reason: Optional[str] = Field(None, description="为什么需要追问")


class SuggestedExamItem(BaseModel):
    """建议检查项"""
    exam_name: str = Field(..., description="检查项目名称")
    reason: Optional[str] = Field(None, description="建议原因")


class ClinicalHintsResponse(BaseModel):
    """临床提示响应"""
    session_id: int = Field(..., description="会话ID")
    warnings: List[WarningItem] = Field(default_factory=list, description="风险提示列表")
    followup_questions: List[FollowupQuestionItem] = Field(default_factory=list, description="追问建议列表")
    suggested_exams: List[SuggestedExamItem] = Field(default_factory=list, description="建议检查列表")
