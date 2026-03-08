#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vocabulary Schemas
词库相关的数据模型
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# ============ 医学词汇 ============

class MedicalVocabularyBase(BaseModel):
    """医学词汇基础模型"""
    category: str = Field(..., description="分类: body_parts/symptoms/diseases/directions")
    standard_name: str = Field(..., description="标准名称")
    keywords: List[str] = Field(..., description="关键词列表")
    description: Optional[str] = Field(None, description="描述说明")
    specialty: Optional[str] = Field(None, description="专科分类")


class MedicalVocabularyCreate(MedicalVocabularyBase):
    """创建医学词汇"""
    pass


class MedicalVocabularyUpdate(BaseModel):
    """更新医学词汇"""
    standard_name: Optional[str] = None
    keywords: Optional[List[str]] = None
    description: Optional[str] = None
    specialty: Optional[str] = None
    status: Optional[str] = None


class MedicalVocabularyResponse(MedicalVocabularyBase):
    """医学词汇响应"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MedicalVocabularyListRequest(BaseModel):
    """医学词汇列表查询请求"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    category: Optional[str] = Field(None, description="分类筛选")
    specialty: Optional[str] = Field(None, description="专科筛选")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    status: Optional[str] = Field("active", description="状态筛选")


class MedicalVocabularyListResponse(BaseModel):
    """医学词汇列表响应"""
    total: int
    page: int
    page_size: int
    items: List[MedicalVocabularyResponse]


# ============ ICD编码 ============

class ICDCodeBase(BaseModel):
    """ICD编码基础模型"""
    icd_code: str = Field(..., description="ICD编码")
    icd_name_cn: str = Field(..., description="中文名称")
    icd_name_en: Optional[str] = Field(None, description="英文名称")
    category: Optional[str] = Field(None, description="章节分类")
    description: Optional[str] = Field(None, description="描述说明")
    keywords: Optional[List[str]] = Field(None, description="搜索关键词")


class ICDCodeCreate(ICDCodeBase):
    """创建ICD编码"""
    pass


class ICDCodeUpdate(BaseModel):
    """更新ICD编码"""
    icd_name_cn: Optional[str] = None
    icd_name_en: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    status: Optional[str] = None


class ICDCodeResponse(ICDCodeBase):
    """ICD编码响应"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ICDCodeListRequest(BaseModel):
    """ICD编码列表查询请求"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    category: Optional[str] = Field(None, description="分类筛选")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    status: Optional[str] = Field("active", description="状态筛选")


class ICDCodeListResponse(BaseModel):
    """ICD编码列表响应"""
    total: int
    page: int
    page_size: int
    items: List[ICDCodeResponse]


# ============ 手术编码 ============

class SurgeryCodeBase(BaseModel):
    """手术编码基础模型"""
    surgery_code: str = Field(..., description="手术编码")
    surgery_name: str = Field(..., description="手术名称")
    category: Optional[str] = Field(None, description="手术分类")
    description: Optional[str] = Field(None, description="描述说明")
    keywords: Optional[List[str]] = Field(None, description="搜索关键词")
    difficulty_level: Optional[str] = Field(None, description="难度等级")


class SurgeryCodeCreate(SurgeryCodeBase):
    """创建手术编码"""
    pass


class SurgeryCodeUpdate(BaseModel):
    """更新手术编码"""
    surgery_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    difficulty_level: Optional[str] = None
    status: Optional[str] = None


class SurgeryCodeResponse(SurgeryCodeBase):
    """手术编码响应"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SurgeryCodeListRequest(BaseModel):
    """手术编码列表查询请求"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    category: Optional[str] = Field(None, description="分类筛选")
    keyword: Optional[str] = Field(None, description="关键词搜索")
    status: Optional[str] = Field("active", description="状态筛选")


class SurgeryCodeListResponse(BaseModel):
    """手术编码列表响应"""
    total: int
    page: int
    page_size: int
    items: List[SurgeryCodeResponse]


# ============ 相似词检查 ============

class SimilarCheckRequest(BaseModel):
    """相似词检查请求"""
    text: str = Field(..., description="待检查的文本")
    category: Optional[str] = Field(None, description="限定分类")


class SimilarItem(BaseModel):
    """相似项"""
    id: int
    standard_name: str
    keywords: List[str]
    similarity: float = Field(..., description="相似度 0-1")


class SimilarCheckResponse(BaseModel):
    """相似词检查响应"""
    has_similar: bool = Field(..., description="是否存在相似词")
    similar_items: List[SimilarItem] = Field(..., description="相似词列表")
