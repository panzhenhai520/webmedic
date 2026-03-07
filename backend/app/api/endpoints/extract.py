#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Endpoints
结构化抽取接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from app.core.response import success_response, error_response
from app.db.session import get_db
from app.services.extract_service import extract_service
from app.schemas.encounter_schema import StructuredRecordData
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class ExtractRequest(BaseModel):
    """抽取请求"""
    session_id: int = Field(..., description="会话ID")
    extractor_type: Optional[str] = Field("instructor", description="抽取器类型")


@router.post("/", response_model=dict)
async def extract_structured_record(
    request: ExtractRequest,
    db: Session = Depends(get_db)
):
    """
    根据当前会话抽取结构化病历

    Args:
        request: 抽取请求
        db: 数据库会话

    Returns:
        结构化病历数据
    """
    logger.info(f"收到抽取请求，session_id={request.session_id}, extractor_type={request.extractor_type}")
    try:
        # 调用抽取服务
        record = await extract_service.extract_from_session(
            db=db,
            session_id=request.session_id,
            extractor_type=request.extractor_type
        )
        logger.info(f"抽取成功，record.id={record.id}")

        # 构建响应数据
        response_data = {
            "record_id": record.id,
            "session_id": record.session_id,
            "extractor_type": record.extractor_type,
            "structured_record": {
                "chief_complaint": record.chief_complaint,
                "present_illness": record.present_illness,
                "past_history": record.past_history,
                "allergy_history": record.allergy_history,
                "physical_exam": record.physical_exam,
                "preliminary_diagnosis": record.preliminary_diagnosis,
                "suggested_exams": record.suggested_exams,
                "warning_flags": record.warning_flags
            },
            "created_at": record.created_at.isoformat() if record.created_at else None
        }

        return success_response(
            data=response_data,
            message="结构化抽取成功"
        )

    except ValueError as e:
        logger.warning(f"ValueError: {e}")
        return error_response(message=str(e))
    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}: {e}", exc_info=True)
        return error_response(message=f"结构化抽取失败: {str(e)}")


@router.get("/{session_id}", response_model=dict)
async def get_structured_record(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    获取会话的结构化病历

    Args:
        session_id: 会话ID
        db: 数据库会话

    Returns:
        结构化病历数据
    """
    try:
        # 获取结构化病历
        record = extract_service.get_structured_record(
            db=db,
            session_id=session_id
        )

        # 构建响应数据
        response_data = {
            "record_id": record.id,
            "session_id": record.session_id,
            "extractor_type": record.extractor_type,
            "structured_record": {
                "chief_complaint": record.chief_complaint,
                "present_illness": record.present_illness,
                "past_history": record.past_history,
                "allergy_history": record.allergy_history,
                "physical_exam": record.physical_exam,
                "preliminary_diagnosis": record.preliminary_diagnosis,
                "suggested_exams": record.suggested_exams,
                "warning_flags": record.warning_flags
            },
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None
        }

        return success_response(
            data=response_data,
            message="获取结构化病历成功"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"获取结构化病历失败: {str(e)}")
