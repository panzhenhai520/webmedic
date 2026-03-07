#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Data Endpoints
基础数据接口（医生、患者等）
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.response import success_response, error_response
from app.db.session import get_db
from app.services.session_service import SessionService
from app.schemas.session import DoctorResponse, PatientResponse

router = APIRouter()


@router.get("/doctor/default", response_model=dict)
async def get_default_doctor(db: Session = Depends(get_db)):
    """
    获取默认医生（Doctor Panython）

    Args:
        db: 数据库会话

    Returns:
        默认医生信息
    """
    try:
        # 获取默认医生
        doctor = SessionService.get_default_doctor(db=db)

        # 构建响应
        response_data = DoctorResponse(
            id=doctor.id,
            doctor_name=doctor.doctor_name,
            title=doctor.title,
            department=doctor.department
        )

        return success_response(
            data=response_data.model_dump(),
            message="获取默认医生成功"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"获取默认医生失败: {str(e)}")


@router.get("/patient/default", response_model=dict)
async def get_default_patient(db: Session = Depends(get_db)):
    """
    获取默认患者（张三）

    Args:
        db: 数据库会话

    Returns:
        默认患者信息
    """
    try:
        # 获取默认患者
        patient = SessionService.get_default_patient(db=db)

        # 构建响应
        response_data = PatientResponse(
            id=patient.id,
            patient_name=patient.patient_name,
            gender=patient.gender,
            age=patient.age,
            phone=patient.phone,
            birthday=str(patient.birthday) if patient.birthday else None
        )

        return success_response(
            data=response_data.model_dump(),
            message="获取默认患者成功"
        )

    except ValueError as e:
        return error_response(message=str(e))
    except Exception as e:
        return error_response(message=f"获取默认患者失败: {str(e)}")
