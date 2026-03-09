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
        from app.services.index_service import get_index_service
        from app.models.medical_document import MedicalDocument

        # 获取索引服务
        index_service = await get_index_service()

        # 查询所有文档（不限制状态，因为索引过程会自动解析PDF）
        documents = db.query(MedicalDocument).all()

        total_documents = len(documents)
        indexed_count = 0

        # 索引每个文档
        for doc in documents:
            try:
                await index_service.index_document(db, doc.id)
                indexed_count += 1
            except Exception as e:
                print(f"Failed to index document {doc.id}: {e}")

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
        from app.services.index_service import get_index_service
        from app.models.structured_record import StructuredRecord
        from pypdf import PdfReader
        import os
        import re

        # 获取索引服务实例
        index_service = await get_index_service()

        matches = await index_service.search_similar_cases(
            db=db,
            session_id=session_id,
            top_k=top_k
        )

        # 获取当前会话的结构化记录
        current_record = db.query(StructuredRecord).filter(
            StructuredRecord.session_id == session_id
        ).order_by(StructuredRecord.created_at.desc()).first()

        current_chief_complaint = ""
        current_present_illness = ""
        if current_record:
            current_chief_complaint = current_record.chief_complaint or ""
            current_present_illness = current_record.present_illness or ""

        # 获取匹配结果和文档信息
        match_results = index_service.get_similar_cases_by_session(db, session_id)

        # 转换为响应格式，添加结构化对比数据
        match_list = []
        for match, doc in match_results:
            # 读取 PDF 内容
            content_preview = ""
            similar_chief_complaint = ""
            similar_present_illness = ""

            try:
                file_path = os.path.join("medical_records", doc.file_name)
                if os.path.exists(file_path):
                    # 使用 PyMuPDF 提取 PDF 内容（对中文支持更好）
                    try:
                        import fitz
                        pdf_doc = fitz.open(file_path)
                        full_content = ""
                        for page in pdf_doc:
                            full_content += page.get_text()
                        pdf_doc.close()
                    except ImportError:
                        # 如果 PyMuPDF 未安装，回退到 pypdf
                        reader = PdfReader(file_path)
                        full_content = "\n".join([page.extract_text() for page in reader.pages])

                    content_preview = full_content[:800] + ("..." if len(full_content) > 800 else "")

                    # 按行分割
                    lines = [line.strip() for line in full_content.split('\n') if line.strip()]

                    # 查找主诉和现病史
                    # 策略：在这个 PDF 中，内容在标签之前
                    chief_idx = -1
                    illness_idx = -1

                    for i, line in enumerate(lines):
                        if '主诉:' in line or '主诉：' in line:
                            chief_idx = i
                        if '现病史:' in line or '现病史：' in line:
                            illness_idx = i

                    # 提取主诉：查找"主诉:"标签之前的内容，找包含"天"或"日"的行
                    if chief_idx > 0:
                        for i in range(chief_idx - 1, max(0, chief_idx - 10), -1):
                            if '天' in lines[i] or '日' in lines[i] or '疼痛' in lines[i] or '不适' in lines[i]:
                                similar_chief_complaint = lines[i][:200]
                                break

                    # 提取现病史：查找"现病史:"标签之前的内容
                    if illness_idx > 0:
                        for i in range(illness_idx - 1, max(0, illness_idx - 10), -1):
                            if '患者' in lines[i] and len(lines[i]) > 20:
                                similar_present_illness = lines[i][:300]
                                break

            except Exception as e:
                content_preview = f"无法读取文档内容: {str(e)}"
                similar_chief_complaint = f"解析错误: {str(e)}"
                similar_present_illness = f"解析错误: {str(e)}"

            match_list.append(
                SimilarCaseMatchSchema(
                    document_id=match.document_id,
                    file_name=doc.file_name,
                    score=match.score,
                    reason_text=match.reason_text,
                    rank_no=match.rank_no,
                    content_preview=content_preview,
                    query_text=f"{current_chief_complaint}\n{current_present_illness}",
                    current_chief_complaint=current_chief_complaint,
                    current_present_illness=current_present_illness,
                    similar_chief_complaint=similar_chief_complaint or "未能从PDF中提取",
                    similar_present_illness=similar_present_illness or "未能从PDF中提取"
                )
            )

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
        from app.services.index_service import get_index_service

        # 获取索引服务实例
        index_service = await get_index_service()

        match_results = index_service.get_similar_cases_by_session(db, session_id)

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
