#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一 API 响应格式
"""

from typing import Any, Optional
from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一 API 响应模型"""
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


def success_response(data: Any = None, message: str = "操作成功") -> dict:
    """
    成功响应

    Args:
        data: 响应数据
        message: 响应消息

    Returns:
        统一格式的成功响应
    """
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(message: str = "操作失败", data: Any = None) -> dict:
    """
    错误响应

    Args:
        message: 错误消息
        data: 额外的错误数据

    Returns:
        统一格式的错误响应
    """
    return {
        "success": False,
        "message": message,
        "data": data
    }
