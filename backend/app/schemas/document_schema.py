#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Schemas
病历文档相关的 Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ScanLocalRequest(BaseModel):
    """扫描本地目录请求"""
    directory: str = Field(..., description="要扫描的目录路径")


class DocumentInfo(BaseModel):
    """文档信息"""
    id: int = Field(..., description="文档ID")
    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    file_hash: Optional[str] = Field(None, description="文件哈希值")
    parse_status: str = Field(..., description="解析状态")
    index_status: str = Field(..., description="索引状态")
    source_type: str = Field(..., description="来源类型")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ScanLocalResponse(BaseModel):
    """扫描本地目录响应"""
    total_found: int = Field(..., description="发现的文件总数")
    new_added: int = Field(..., description="新增的文件数")
    already_exists: int = Field(..., description="已存在的文件数")
    documents: List[DocumentInfo] = Field(default_factory=list, description="文档列表")
