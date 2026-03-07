#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局异常处理器
统一处理未捕获的异常
"""

import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器
    捕获所有未处理的异常，返回统一格式
    """
    logger.error(
        f"未处理的异常: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else "unknown"
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": f"服务器内部错误: {type(exc).__name__}",
            "data": None
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    数据库异常处理器
    """
    logger.error(
        f"数据库错误: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "数据库操作失败",
            "data": None
        }
    )


async def value_error_handler(request: Request, exc: ValueError):
    """
    参数错误处理器
    """
    logger.warning(
        f"参数错误: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": str(exc),
            "data": None
        }
    )
