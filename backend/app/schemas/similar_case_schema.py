#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Similar Case Schemas
相似病历相关的 Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StructuredComparison(BaseModel):
    """结构化对比数据"""
    field_name: str = Field(..., description="字段名称")
    current_value: str = Field(..., description="当前患者的值")
    similar_value: str = Field(..., description="相似病历的值")
    similarity_score: Optional[float] = Field(None, description="该字段的相似度")


class SimilarCaseMatch(BaseModel):
    """相似病历匹配结果"""
    document_id: int = Field(..., description="文档ID")
    file_name: str = Field(..., description="文件名")
    score: Optional[float] = Field(None, description="相似度分数")
    reason_text: Optional[str] = Field(None, description="匹配原因说明")
    rank_no: int = Field(..., description="排名序号")
    content_preview: Optional[str] = Field(None, description="文档内容预览（前500字）")
    query_text: Optional[str] = Field(None, description="查询文本（主诉+现病史）")
    # 结构化对比数据
    current_chief_complaint: Optional[str] = Field(None, description="当前患者主诉")
    current_present_illness: Optional[str] = Field(None, description="当前患者现病史")
    similar_chief_complaint: Optional[str] = Field(None, description="相似病历主诉")
    similar_present_illness: Optional[str] = Field(None, description="相似病历现病史")


class SearchSimilarResponse(BaseModel):
    """检索相似病历响应"""
    session_id: int = Field(..., description="会话ID")
    matches: List[SimilarCaseMatch] = Field(default_factory=list, description="匹配结果列表")
    total_count: int = Field(..., description="匹配结果总数")
