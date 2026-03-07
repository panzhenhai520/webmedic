#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Information Endpoints
系统信息接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.response import success_response
from app.db.session import get_db
from app.models import Doctor, Patient

router = APIRouter()


@router.get("/system/info")
async def get_system_info():
    """
    获取系统信息
    """
    from app.core.config import settings

    return success_response(
        data={
            "project": "WebMedic",
            "version": "0.1.0",
            "stage": "Stage 8 - Draft Generation & Clinical Hints",
            "description": "语音驱动门诊电子病历生成 Demo 系统",
            "database": "MySQL",
            "framework": "FastAPI",
            "llm_mode": "Mock" if settings.LLM_USE_MOCK else "Real",
            "llm_model": settings.DEEPSEEK_MODEL if not settings.LLM_USE_MOCK else "Mock",
            "asr_engine": settings.ASR_ENGINE.upper(),
            "asr_mode": "Mock" if settings.ASR_USE_MOCK else "Real"
        },
        message="系统信息获取成功"
    )


@router.get("/system/database/tables")
async def get_database_tables(db: Session = Depends(get_db)):
    """
    获取数据库表列表
    """
    try:
        # 查询所有表
        result = db.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]

        return success_response(
            data={
                "tables": tables,
                "count": len(tables)
            },
            message="数据库表列表获取成功"
        )
    except Exception as e:
        return success_response(
            data={
                "tables": [],
                "count": 0,
                "error": str(e)
            },
            message="数据库表列表获取失败"
        )


@router.get("/system/database/stats")
async def get_database_stats(db: Session = Depends(get_db)):
    """
    获取数据库统计信息
    """
    try:
        # 统计各表记录数
        doctor_count = db.query(Doctor).count()
        patient_count = db.query(Patient).count()

        return success_response(
            data={
                "doctors": doctor_count,
                "patients": patient_count
            },
            message="数据库统计信息获取成功"
        )
    except Exception as e:
        return success_response(
            data={
                "error": str(e)
            },
            message="数据库统计信息获取失败"
        )


@router.post("/system/asr/switch")
async def switch_asr_engine(engine: str):
    """
    切换 ASR 引擎
    支持: whisper, dolphin, mock
    """
    from app.core.config import settings
    import os

    # 验证引擎类型
    valid_engines = ["whisper", "dolphin", "mock"]
    engine_lower = engine.lower()

    if engine_lower not in valid_engines:
        return success_response(
            data={"current_engine": settings.ASR_ENGINE},
            message=f"无效的引擎类型，支持: {', '.join(valid_engines)}"
        )

    # 更新环境变量（仅在当前进程中生效）
    if engine_lower == "mock":
        os.environ["ASR_USE_MOCK"] = "true"
        os.environ["ASR_ENGINE"] = "whisper"  # mock 模式下默认使用 whisper
        settings.ASR_USE_MOCK = True
    else:
        os.environ["ASR_USE_MOCK"] = "false"
        os.environ["ASR_ENGINE"] = engine_lower
        settings.ASR_ENGINE = engine_lower
        settings.ASR_USE_MOCK = False

    return success_response(
        data={
            "current_engine": engine_lower if engine_lower != "mock" else "mock",
            "asr_mode": "Mock" if settings.ASR_USE_MOCK else "Real",
            "note": "引擎已切换（当前进程有效，重启后恢复配置文件设置）"
        },
        message=f"ASR 引擎已切换到: {engine_lower}"
    )


@router.post("/system/llm/switch")
async def switch_llm_model(model: str):
    """
    切换 LLM 模型
    支持: deepseek-chat, deepseek-reasoner
    """
    from app.core.config import settings
    import os

    # 验证模型类型
    valid_models = ["deepseek-chat", "deepseek-reasoner"]
    model_lower = model.lower()

    if model_lower not in valid_models:
        return success_response(
            data={"current_model": settings.DEEPSEEK_MODEL},
            message=f"无效的模型类型，支持: {', '.join(valid_models)}"
        )

    # 更新环境变量（仅在当前进程中生效）
    os.environ["DEEPSEEK_MODEL"] = model_lower
    settings.DEEPSEEK_MODEL = model_lower

    return success_response(
        data={
            "current_model": model_lower,
            "note": "模型已切换（当前进程有效，重启后恢复配置文件设置）"
        },
        message=f"LLM 模型已切换到: {model_lower}"
    )
