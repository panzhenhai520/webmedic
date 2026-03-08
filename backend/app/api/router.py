#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 路由汇总
所有 API 路由统一在此注册
"""

import logging
from fastapi import APIRouter
from app.core.response import success_response
from app.core.config import settings
from app.api.endpoints import health, system, sessions, master_data, asr, extract, documents, index, draft, clinical_hints, vocabulary

logger = logging.getLogger(__name__)

# 创建主路由
api_router = APIRouter()


@api_router.get("/ping")
async def ping():
    """
    健康检查接口
    用于测试 API 是否正常工作
    """
    return success_response(
        data={"status": "ok"},
        message="API is working"
    )


@api_router.get("/info")
async def get_info():
    """
    获取系统信息
    """
    logger.debug("/info 接口被调用")

    llm_mode = "Unknown"
    llm_model = "Unknown"

    try:
        logger.debug("尝试读取配置...")
        logger.debug(f"settings 对象: {settings}")
        logger.debug(f"hasattr LLM_USE_MOCK: {hasattr(settings, 'LLM_USE_MOCK')}")

        if hasattr(settings, 'LLM_USE_MOCK'):
            use_mock = settings.LLM_USE_MOCK
            logger.debug(f"LLM_USE_MOCK = {use_mock}")
            llm_mode = "Mock" if use_mock else "DeepSeek API"

        if hasattr(settings, 'DEEPSEEK_MODEL'):
            model = settings.DEEPSEEK_MODEL
            logger.debug(f"DEEPSEEK_MODEL = {model}")
            llm_model = model if not settings.LLM_USE_MOCK else "Mock"

        logger.debug(f"最终 llm_mode = {llm_mode}, llm_model = {llm_model}")

    except Exception as e:
        logger.error(f"配置读取异常: {type(e).__name__}: {e}", exc_info=True)

    logger.debug("准备返回响应")

    return success_response(
        data={
            "project": "WebMedic",
            "version": "0.1.0",
            "stage": "Stage 9 - 完善与打磨",
            "description": "语音驱动门诊电子病历生成 Demo 系统",
            "llm_mode": llm_mode,
            "llm_model": llm_model
        },
        message="系统信息获取成功"
    )


# 注册健康检查路由
api_router.include_router(health.router, tags=["健康检查"])

# 注册系统信息路由
api_router.include_router(system.router, tags=["系统信息"])

# 注册会话管理路由
api_router.include_router(sessions.router, prefix="/sessions", tags=["会话管理"])

# 注册基础数据路由
api_router.include_router(master_data.router, prefix="/master-data", tags=["基础数据"])

# 注册 ASR 转写路由
api_router.include_router(asr.router, prefix="/asr", tags=["语音识别"])

# 注册结构化抽取路由
api_router.include_router(extract.router, prefix="/extract", tags=["结构化抽取"])

# 注册病历文档路由
api_router.include_router(documents.router, prefix="/documents", tags=["病历文档"])

# 注册索引检索路由
api_router.include_router(index.router, prefix="/index", tags=["索引检索"])

# 注册病历草稿路由
api_router.include_router(draft.router, prefix="/draft", tags=["病历草稿"])

# 注册临床提示路由
api_router.include_router(clinical_hints.router, prefix="/clinical-hints", tags=["临床提示"])

# 注册词库管理路由
api_router.include_router(vocabulary.router, prefix="/vocabulary", tags=["词库管理"])


# 后续阶段将在此注册更多路由
