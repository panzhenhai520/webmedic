#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Session Management
数据库会话管理
"""

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from app.core.config import settings

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # 连接前先 ping，确保连接有效
    pool_recycle=3600,   # 1小时后回收连接
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 最大溢出连接数
    echo=False,          # 不打印 SQL 语句（生产环境）
)

# 创建 SessionLocal 类
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    用于 FastAPI 依赖注入

    ��用示例:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_db_connection() -> bool:
    """
    测试数据库连接

    Returns:
        bool: 连接成功返回 True，否则返回 False
    """
    try:
        db = SessionLocal()
        # 执行简单查询测试连接
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        return False
