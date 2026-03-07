#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Draft API Endpoints
病历草稿接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.response import success_response, error_response
from app.db.session import get_db
from app.schemas.draft_schema import ApplySimilarPlanRequest, DraftResponse, DraftContent
from app.services.draft_service import DraftService

router = APIRouter()


@router.post("/generate/{session_id}", response_model=dict)
async def generate_draft(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    生成病历草稿
    """
    try:
        draft = DraftService.generate_draft(db, session_id)

        # 转换为响应格式
        response_data = DraftResponse(
            draft_id=draft.id,
            session_id=draft.session_id,
            draft_type=draft.draft_type,
            content=DraftContent(**draft.content_json),
            source_case_ids=draft.source_case_ids,
            created_at=draft.created_at
        )

        return success_response(
            data=response_data.model_dump(),
            message="病历草稿生成成功"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"生成病历草稿失败: {str(e)}")


@router.post("/apply-similar-plan/{session_id}", response_model=dict)
async def apply_similar_plan(
    session_id: int,
    request: ApplySimilarPlanRequest,
    db: Session = Depends(get_db)
):
    """
    使用相同检查治疗方案
    """
    try:
        draft = DraftService.apply_similar_plan(
            db=db,
            session_id=session_id,
            source_document_id=request.source_document_id
        )

        # 转换为响应格式
        response_data = DraftResponse(
            draft_id=draft.id,
            session_id=draft.session_id,
            draft_type=draft.draft_type,
            content=DraftContent(**draft.content_json),
            source_case_ids=draft.source_case_ids,
            created_at=draft.created_at
        )

        return success_response(
            data=response_data.model_dump(),
            message="已应用相似病历的检查治疗方案"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"应用方案失败: {str(e)}")
