#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session Endpoints
会话管理接口
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.response import success_response, error_response
from app.db.session import get_db
from app.services.session_service import SessionService
from app.schemas.session import (
    SessionCreateRequest,
    SessionCreateResponse,
    SessionDetailResponse
)
from app.schemas.session_history import (
    SessionListItem,
    SessionListResponse,
    TranscriptItem,
    SessionDetailWithTranscripts
)
from app.models import TranscriptSegment

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create", response_model=dict)
async def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db)
):
    """
    创建问诊会话

    Args:
        request: 创建会话请求
        db: 数据库会话

    Returns:
        创建的会话信息
    """
    try:
        # 创建会话
        session = SessionService.create_session(
            db=db,
            doctor_id=request.doctor_id,
            patient_id=request.patient_id
        )

        # 构建响应
        response_data = SessionCreateResponse(
            id=session.id,
            session_no=session.session_no,
            doctor_id=session.doctor_id,
            patient_id=session.patient_id,
            status=session.status,
            started_at=session.started_at
        )

        return success_response(
            data=response_data.model_dump(),
            message="会话创建成功"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"创建会话失败: {str(e)}")


@router.get("/list", response_model=dict)
async def list_sessions(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取会话列表（分页）

    Args:
        page: 页码
        page_size: 每页数量
        status: 状态过滤
        db: 数据库会话

    Returns:
        会话列表
    """
    try:
        skip = (page - 1) * page_size
        sessions, total = SessionService.get_all_sessions(
            db=db,
            skip=skip,
            limit=page_size,
            status=status
        )

        # 构建响应（sessions 已经是 dict 列表，包含医生和患者信息）
        session_items = [SessionListItem(**session) for session in sessions]

        response_data = SessionListResponse(
            total=total,
            page=page,
            page_size=page_size,
            sessions=session_items
        )

        return success_response(
            data=response_data.model_dump(),
            message="获取会话列表成功"
        )

    except Exception as e:
        logger.error(f"获取会话列表失败: {e}", exc_info=True)
        return error_response(message=f"获取会话列表失败: {str(e)}")


@router.post("/{session_id}/finish", response_model=dict)
async def finish_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    结束问诊会话

    Args:
        session_id: 会话ID
        db: 数据库会话

    Returns:
        更新后的会话信息
    """
    try:
        # 结束会话
        session = SessionService.end_session(db=db, session_id=session_id)

        # 构建响应
        response_data = SessionDetailResponse(
            id=session.id,
            session_no=session.session_no,
            doctor_id=session.doctor_id,
            patient_id=session.patient_id,
            status=session.status,
            started_at=session.started_at,
            ended_at=session.ended_at,
            created_at=session.created_at
        )

        return success_response(
            data=response_data.model_dump(),
            message="会话已结束"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"结束会话失败: {str(e)}")


@router.get("/{session_id}/transcripts", response_model=dict)
async def get_session_with_transcripts(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    获取会话详情（包含转写记录）

    Args:
        session_id: 会话ID
        db: 数据库会话

    Returns:
        会话详情和转写记录
    """
    try:
        result = SessionService.get_session_with_transcripts(db, session_id)
        session = result["session"]
        transcripts = result["transcripts"]

        # 构建响应
        transcript_items = [
            TranscriptItem(
                id=t.id,
                speaker_role=t.speaker_role,
                transcript_text=t.transcript_text,
                audio_file_path=t.audio_file_path,
                start_time_ms=t.start_time_ms,
                end_time_ms=t.end_time_ms,
                status=t.status,
                created_at=t.created_at
            )
            for t in transcripts
        ]

        response_data = SessionDetailWithTranscripts(
            id=session.id,
            session_no=session.session_no,
            doctor_id=session.doctor_id,
            patient_id=session.patient_id,
            status=session.status,
            started_at=session.started_at,
            ended_at=session.ended_at,
            created_at=session.created_at,
            transcripts=transcript_items,
            transcript_count=len(transcript_items)
        )

        return success_response(
            data=response_data.model_dump(),
            message="获取会话详情成功"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        logger.error(f"获取会话详情失败: {e}", exc_info=True)
        return error_response(message=f"获取会话详情失败: {str(e)}")


@router.get("/{session_id}", response_model=dict)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    获取会话详情

    Args:
        session_id: 会话ID
        db: 数据库会话

    Returns:
        会话详情
    """
    try:
        # 获取会话
        session = SessionService.get_session(db=db, session_id=session_id)

        # 构建响应
        response_data = SessionDetailResponse(
            id=session.id,
            session_no=session.session_no,
            doctor_id=session.doctor_id,
            patient_id=session.patient_id,
            status=session.status,
            started_at=session.started_at,
            ended_at=session.ended_at,
            created_at=session.created_at
        )

        return success_response(
            data=response_data.model_dump(),
            message="获取会话详情成功"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"获取会话详情失败: {str(e)}")
