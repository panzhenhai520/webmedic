#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clinical Hints API Endpoints
临床提示接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.response import success_response, error_response
from app.db.session import get_db
from app.schemas.clinical_hint_schema import (
    ClinicalHintsResponse,
    WarningItem,
    FollowupQuestionItem,
    SuggestedExamItem
)
from app.services.clinical_hint_service import ClinicalHintService

router = APIRouter()


@router.post("/generate/{session_id}", response_model=dict)
async def generate_clinical_hints(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    生成临床提示（风险提示、追问建议、建议检查）
    """
    try:
        hints = ClinicalHintService.generate_hints(db, session_id)

        # 转换为响应格式
        warnings = [WarningItem(**w) for w in hints.get("warnings", [])]
        followup_questions = [FollowupQuestionItem(**q) for q in hints.get("followup_questions", [])]
        suggested_exams = [SuggestedExamItem(**e) for e in hints.get("suggested_exams", [])]

        response_data = ClinicalHintsResponse(
            session_id=session_id,
            warnings=warnings,
            followup_questions=followup_questions,
            suggested_exams=suggested_exams
        )

        return success_response(
            data=response_data.model_dump(),
            message="临床提示生成成功"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"生成临床提示失败: {str(e)}")
