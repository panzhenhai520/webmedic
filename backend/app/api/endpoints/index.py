#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Index API Endpoints
病历索引与检索接口
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.response import success_response, error_response
from app.db.session import get_db
from app.schemas.similar_case_schema import SearchSimilarResponse, SimilarCaseMatch as SimilarCaseMatchSchema
from app.services.index_service import IndexService

router = APIRouter()


@router.post("/rebuild", response_model=dict)
async def rebuild_index(db: Session = Depends(get_db)):
    """
    重建索引
    对所有待索引的文档执行索引操作
    """
    try:
        total_documents, indexed_count = IndexService.rebuild_index(db)

        return success_response(
            data={
                "total_documents": total_documents,
                "indexed_count": indexed_count
            },
            message=f"索引重建完成，共处理 {total_documents} 个文档，成功索引 {indexed_count} 个"
        )

    except Exception as e:
        return error_response(message=f"重建索引失败: {str(e)}")


@router.post("/search-similar/{session_id}", response_model=dict)
async def search_similar_cases(
    session_id: int,
    top_k: int = 3,
    db: Session = Depends(get_db)
):
    """
    检索相似病历
    根据当前会话的结构化记录检索最相似的病历文档
    """
    try:
        matches = IndexService.search_similar_cases(
            db=db,
            session_id=session_id,
            top_k=top_k
        )

        # 获取匹配结果和文档信息
        match_results = IndexService.get_similar_cases_by_session(db, session_id)

        # 转换为响应格式
        match_list = [
            SimilarCaseMatchSchema(
                document_id=match.document_id,
                file_name=doc.file_name,
                score=match.score,
                reason_text=match.reason_text,
                rank_no=match.rank_no
            )
            for match, doc in match_results
        ]

        response_data = SearchSimilarResponse(
            session_id=session_id,
            matches=match_list,
            total_count=len(match_list)
        )

        return success_response(
            data=response_data.model_dump(),
            message=f"检索完成，找到 {len(match_list)} 条相似病历"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"检索相似病历失败: {str(e)}")


@router.get("/similar-cases/{session_id}", response_model=dict)
async def get_similar_cases(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    获取会话的相似病历匹配结果
    """
    try:
        match_results = IndexService.get_similar_cases_by_session(db, session_id)

        # 转换为响应格式
        match_list = [
            SimilarCaseMatchSchema(
                document_id=match.document_id,
                file_name=doc.file_name,
                score=match.score,
                reason_text=match.reason_text,
                rank_no=match.rank_no
            )
            for match, doc in match_results
        ]

        response_data = SearchSimilarResponse(
            session_id=session_id,
            matches=match_list,
            total_count=len(match_list)
        )

        return success_response(
            data=response_data.model_dump(),
            message="获取相似病历成功"
        )

    except Exception as e:
        return error_response(message=f"获取相似病历失败: {str(e)}")
