#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一日志配置模块
支持控制台和文件输出，带日志轮转
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from app.core.config import settings


def setup_logging():
    """
    配置应用日志系统

    日志级别:
    - dev 环境: DEBUG
    - prod 环境: INFO

    输出目标:
    - 控制台: 彩色格式化输出
    - 文件: logs/webmedic.log (自动轮转)
    """
    # 确定日志级别
    log_level = logging.DEBUG if settings.APP_ENV == "dev" else logging.INFO

    # 创建根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除已有的处理器
    root_logger.handlers.clear()

    # 日志格式
    console_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_format = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    # 2. 文件处理器（带轮转）
    log_file = os.path.join(settings.LOG_DIR, "webmedic.log")
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)

    # 3. 错误日志单独文件
    error_log_file = os.path.join(settings.LOG_DIR, "error.log")
    error_handler = RotatingFileHandler(
        filename=error_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    root_logger.addHandler(error_handler)

    # 降低第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    logging.info(f"日志系统初始化完成 - 级别: {logging.getLevelName(log_level)}")
    logging.info(f"日志文件: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器

    Args:
        name: 日志器名称（通常使用 __name__）

    Returns:
        配置好的日志器实例
    """
    return logging.getLogger(name)
