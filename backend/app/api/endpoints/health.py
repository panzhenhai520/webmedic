#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Check Endpoints
健康检查接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.response import success_response, error_response
from app.db.session import get_db, test_db_connection

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    系统健康检查
    检查服务是否正常运行
    """
    return success_response(
        data={
            "status": "healthy",
            "service": "webmedic-backend"
        },
        message="服务运行正常"
    )


@router.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)):
    """
    数据库健康检查
    检查数据库连接是否正常
    """
    try:
        # 执行简单查询测试数据库连接
        db.execute(text("SELECT 1"))

        return success_response(
            data={
                "status": "healthy",
                "database": "connected"
            },
            message="数据库连接正常"
        )
    except Exception as e:
        return error_response(
            message=f"数据库连接失败: {str(e)}",
            data={
                "status": "unhealthy",
                "database": "disconnected"
            }
        )
