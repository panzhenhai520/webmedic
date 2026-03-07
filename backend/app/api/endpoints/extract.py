#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Endpoints
结构化抽取接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.response import success_response, error_response
from app.db.session import get_db
from app.services.extract_service import ExtractService
from app.schemas.encounter_schema import ExtractResponse, StructuredRecordData
from app.services.llm_service import llm_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/test-llm", response_model=dict)
async def test_llm():
    """测试 LLM Service"""
    try:
        result = llm_service.generate_json("测试结构化病历抽取")
        return success_response(
            data={
                "type": str(type(result)),
                "content": result
            },
            message="测试成功"
        )
    except Exception as e:
        import traceback
        return error_response(message=f"测试失败: {str(e)}\n{traceback.format_exc()}")


@router.post("/{session_id}", response_model=dict)
async def extract_structured_record(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    根据当前会话重新抽取结构化病历

    Args:
        session_id: 会话ID
        db: 数据库会话

    Returns:
        结构化病历数据
    """
    logger.debug(f"收到抽取请求，session_id={session_id}")
    try:
        logger.debug("准备调用 ExtractService...")
        # 调用抽取服务
        record = ExtractService.extract_structured_record(
            db=db,
            session_id=session_id
        )
        logger.debug(f"ExtractService 返回成功，record.id={record.id}")

        # 构建响应数据
        structured_data = StructuredRecordData(
            chief_complaint=record.chief_complaint,
            present_illness=record.present_illness,
            past_history=record.past_history,
            allergy_history=record.allergy_history,
            physical_exam=record.physical_exam,
            preliminary_diagnosis=record.preliminary_diagnosis,
            suggested_exams=record.suggested_exams,
            warning_flags=record.warning_flags
        )

        response_data = {
            "record_id": record.id,
            "session_id": record.session_id,
            "structured_record": structured_data.model_dump(),
            "created_at": record.created_at.isoformat() if record.created_at else None
        }

        logger.debug("准备返回成功响应")
        return success_response(
            data=response_data,
            message="结构化抽取成功"
        )

    except ValueError as e:
        logger.warning(f"捕获 ValueError: {e}")
        return error_response(message=str(e))
    except Exception as e:
        logger.error(f"捕获 Exception: {type(e).__name__}: {e}", exc_info=True)
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
        record = ExtractService.get_structured_record(
            db=db,
            session_id=session_id
        )

        # 构建响应数据
        structured_data = StructuredRecordData(
            chief_complaint=record.chief_complaint,
            present_illness=record.present_illness,
            past_history=record.past_history,
            allergy_history=record.allergy_history,
            physical_exam=record.physical_exam,
            preliminary_diagnosis=record.preliminary_diagnosis,
            suggested_exams=record.suggested_exams,
            warning_flags=record.warning_flags
        )

        response_data = {
            "record_id": record.id,
            "session_id": record.session_id,
            "structured_record": structured_data.model_dump(),
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
