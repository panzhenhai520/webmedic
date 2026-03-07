#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加extractor_type字段
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings

def add_extractor_type_field():
    """添加extractor_type字段到structured_records表"""
    engine = create_engine(settings.database_url)

    try:
        with engine.begin() as conn:  # 使用begin()自动提交
            # 检查字段是否已存在
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :db_name
                AND TABLE_NAME = 'structured_records'
                AND COLUMN_NAME = 'extractor_type'
            """), {"db_name": settings.DB_NAME})

            count = result.fetchone()[0]

            if count > 0:
                print("extractor_type field already exists")
                return

            # 添加字段
            conn.execute(text("""
                ALTER TABLE structured_records
                ADD COLUMN extractor_type VARCHAR(50) NULL COMMENT 'extractor type'
                AFTER warning_flags
            """))

            print("Successfully added extractor_type field")

    except Exception as e:
        print(f"Failed to add field: {e}")
        raise

if __name__ == "__main__":
    print("Starting database migration...")
    add_extractor_type_field()
    print("Database migration completed!")
