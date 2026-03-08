#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建词库相关数据库表
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.base import Base
from app.db.session import engine
from app.models.medical_vocabulary import MedicalVocabulary
from app.models.icd_code import ICDCode
from app.models.surgery_code import SurgeryCode


def create_tables():
    """创建所有表"""
    print("开始创建词库相关数据库表...")

    try:
        # 创建表
        Base.metadata.create_all(bind=engine)

        print("[成功] 数据库表创建成功！")
        print("\n已创建的表：")
        print("  - medical_vocabulary (医学词汇表)")
        print("  - icd_codes (ICD疾病编码表)")
        print("  - surgery_codes (手术编码表)")

    except Exception as e:
        print(f"[失败] 创建表失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_tables()
