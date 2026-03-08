#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vocabulary Management Endpoints
词库管理接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.core.response import success_response, error_response
from app.db.session import get_db
from app.services.vocabulary_service import VocabularyService
from app.schemas.vocabulary import (
    MedicalVocabularyCreate,
    MedicalVocabularyUpdate,
    MedicalVocabularyListRequest,
    MedicalVocabularyListResponse,
    MedicalVocabularyResponse,
    SimilarCheckRequest,
    SimilarCheckResponse,
    SimilarItem,
)

router = APIRouter()


@router.post("/vocabulary/list", response_model=dict)
async def list_vocabulary(
    request: MedicalVocabularyListRequest,
    db: Session = Depends(get_db)
):
    """
    获取医学词汇列表

    Args:
        request: 查询请求
        db: 数据库会话

    Returns:
        词汇列表
    """
    try:
        items, total = VocabularyService.get_vocabulary_list(
            db=db,
            page=request.page,
            page_size=request.page_size,
            category=request.category,
            specialty=request.specialty,
            keyword=request.keyword,
            status=request.status
        )

        # 转换为响应格式
        response_items = []
        for item in items:
            keywords = json.loads(item.keywords) if item.keywords else []
            response_items.append(MedicalVocabularyResponse(
                id=item.id,
                category=item.category,
                standard_name=item.standard_name,
                keywords=keywords,
                description=item.description,
                specialty=item.specialty,
                status=item.status,
                created_at=item.created_at,
                updated_at=item.updated_at
            ))

        response_data = MedicalVocabularyListResponse(
            total=total,
            page=request.page,
            page_size=request.page_size,
            items=response_items
        )

        return success_response(
            data=response_data.model_dump(),
            message="获取词汇列表成功"
        )

    except Exception as e:
        return error_response(message=f"获取词汇列表失败: {str(e)}")


@router.get("/vocabulary/{vocab_id}", response_model=dict)
async def get_vocabulary(
    vocab_id: int,
    db: Session = Depends(get_db)
):
    """
    获取单个医学词汇

    Args:
        vocab_id: 词汇ID
        db: 数据库会话

    Returns:
        词汇详情
    """
    try:
        vocab = VocabularyService.get_vocabulary_by_id(db, vocab_id)

        if not vocab:
            return error_response(message="词汇不存在")

        keywords = json.loads(vocab.keywords) if vocab.keywords else []
        response_data = MedicalVocabularyResponse(
            id=vocab.id,
            category=vocab.category,
            standard_name=vocab.standard_name,
            keywords=keywords,
            description=vocab.description,
            specialty=vocab.specialty,
            status=vocab.status,
            created_at=vocab.created_at,
            updated_at=vocab.updated_at
        )

        return success_response(
            data=response_data.model_dump(),
            message="获取词汇成功"
        )

    except Exception as e:
        return error_response(message=f"获取词汇失败: {str(e)}")


@router.post("/vocabulary/check-similar", response_model=dict)
async def check_similar_vocabulary(
    request: SimilarCheckRequest,
    db: Session = Depends(get_db)
):
    """
    检查相似词汇

    Args:
        request: 检查请求
        db: 数据库会话

    Returns:
        相似词汇列表
    """
    try:
        similar_items = VocabularyService.check_vocabulary_similarity(
            db=db,
            text=request.text,
            category=request.category,
            threshold=0.8
        )

        response_items = [
            SimilarItem(**item) for item in similar_items
        ]

        response_data = SimilarCheckResponse(
            has_similar=len(similar_items) > 0,
            similar_items=response_items
        )

        return success_response(
            data=response_data.model_dump(),
            message="检查完成"
        )

    except Exception as e:
        return error_response(message=f"检查失败: {str(e)}")


@router.post("/vocabulary", response_model=dict)
async def create_vocabulary(
    vocab_data: MedicalVocabularyCreate,
    db: Session = Depends(get_db)
):
    """
    创建医学词汇

    Args:
        vocab_data: 词汇数据
        db: 数据库会话

    Returns:
        创建的词汇
    """
    try:
        # 先检查相似词
        similar_items = VocabularyService.check_vocabulary_similarity(
            db=db,
            text=vocab_data.standard_name,
            category=vocab_data.category,
            threshold=0.9
        )

        if similar_items:
            return error_response(
                message=f"存在相似词汇: {similar_items[0]['standard_name']}",
                data={"similar_items": similar_items}
            )

        # 创建词汇
        vocab = VocabularyService.create_vocabulary(db, vocab_data)

        keywords = json.loads(vocab.keywords) if vocab.keywords else []
        response_data = MedicalVocabularyResponse(
            id=vocab.id,
            category=vocab.category,
            standard_name=vocab.standard_name,
            keywords=keywords,
            description=vocab.description,
            specialty=vocab.specialty,
            status=vocab.status,
            created_at=vocab.created_at,
            updated_at=vocab.updated_at
        )

        return success_response(
            data=response_data.model_dump(),
            message="创建词汇成功"
        )

    except Exception as e:
        return error_response(message=f"创建词汇失败: {str(e)}")


@router.put("/vocabulary/{vocab_id}", response_model=dict)
async def update_vocabulary(
    vocab_id: int,
    vocab_data: MedicalVocabularyUpdate,
    db: Session = Depends(get_db)
):
    """
    更新医学词汇

    Args:
        vocab_id: 词汇ID
        vocab_data: 更新数据
        db: 数据库会话

    Returns:
        更新后的词汇
    """
    try:
        vocab = VocabularyService.update_vocabulary(db, vocab_id, vocab_data)

        if not vocab:
            return error_response(message="词汇不存在")

        keywords = json.loads(vocab.keywords) if vocab.keywords else []
        response_data = MedicalVocabularyResponse(
            id=vocab.id,
            category=vocab.category,
            standard_name=vocab.standard_name,
            keywords=keywords,
            description=vocab.description,
            specialty=vocab.specialty,
            status=vocab.status,
            created_at=vocab.created_at,
            updated_at=vocab.updated_at
        )

        return success_response(
            data=response_data.model_dump(),
            message="更新词汇成功"
        )

    except Exception as e:
        return error_response(message=f"更新词汇失败: {str(e)}")


@router.delete("/vocabulary/{vocab_id}", response_model=dict)
async def delete_vocabulary(
    vocab_id: int,
    db: Session = Depends(get_db)
):
    """
    删除医学词汇

    Args:
        vocab_id: 词汇ID
        db: 数据库会话

    Returns:
        删除结果
    """
    try:
        success = VocabularyService.delete_vocabulary(db, vocab_id)

        if not success:
            return error_response(message="词汇不存在")

        return success_response(message="删除词汇成功")

    except Exception as e:
        return error_response(message=f"删除词汇失败: {str(e)}")
