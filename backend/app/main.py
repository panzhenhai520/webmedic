#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebMedic FastAPI Main Application
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.api.router import api_router
from app.core.logging_config import setup_logging
from app.core.exception_handlers import (
    global_exception_handler,
    database_exception_handler,
    value_error_handler
)

# 初始化日志系统
setup_logging()
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="WebMedic - 语音驱动门诊电子病历生成 Demo 系统",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(api_router, prefix="/api/v1")

# 注册异常处理器
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)


@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "success": True,
        "message": "WebMedic Backend API is running",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "success": True,
        "status": "healthy",
        "service": "webmedic-backend"
    }


# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.APP_NAME} Backend Starting...")
    logger.info(f"📝 Environment: {settings.APP_ENV}")
    logger.info(f"🌐 Host: {settings.APP_HOST}:{settings.APP_PORT}")
    logger.info(f"📚 API Docs: http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
    logger.info("=" * 60)


# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("=" * 60)
    logger.info(f"🛑 {settings.APP_NAME} Backend Shutting Down...")
    logger.info("=" * 60)
