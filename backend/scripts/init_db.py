#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Initialization Script
数据库初始化脚本

功能：
1. 创建数据库（如果不存在）
2. 创建所有数据表
3. 初始化固定医生：Doctor Panython
4. 初始化固定患者：张三（男，29岁）
"""

import sys
import os
from datetime import date
from sqlalchemy import create_engine, text

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.db.base import Base, import_all_models
from app.db.session import engine, SessionLocal
from app.models import Doctor, Patient


def create_database():
    """创建数据库（如果不存在）"""
    print("=" * 60)
    print("检查并创建数据库...")
    print("=" * 60)

    try:
        # 构建不包含数据库名的连接URL（连接到MySQL服务器）
        db_url_without_db = (
            f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@{settings.DB_HOST}:{settings.DB_PORT}/"
            f"?charset=utf8mb4"
        )

        # 创建临时引擎连接到MySQL服务器
        temp_engine = create_engine(db_url_without_db, echo=False)

        # 创建数据库
        with temp_engine.connect() as conn:
            # 检查数据库是否存在
            result = conn.execute(
                text(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{settings.DB_NAME}'")
            )
            exists = result.fetchone()

            if exists:
                print(f"✅ 数据库 '{settings.DB_NAME}' 已存在")
            else:
                # 创建数据库
                conn.execute(text(f"CREATE DATABASE {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
                print(f"✅ 数据库 '{settings.DB_NAME}' 创建成功")

        temp_engine.dispose()
        return True

    except Exception as e:
        print(f"❌ 数据库创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_tables():
    """创建所有数据表"""
    print("=" * 60)
    print("开始创建数据表...")
    print("=" * 60)

    try:
        # 导入所有模型
        import_all_models()

        # 创建所有表
        Base.metadata.create_all(bind=engine)

        print("✅ 数据表创建成功！")
        print("\n已创建的表：")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")

        return True
    except Exception as e:
        print(f"❌ 数据表创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def init_default_data():
    """初始化默认数据"""
    print("\n" + "=" * 60)
    print("开始初始化默认数据...")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 检查是否已经初始化过
        existing_doctor = db.query(Doctor).filter_by(doctor_name="Doctor Panython").first()
        if existing_doctor:
            print("⚠️  默认数据已存在，跳过初始化")
            return True

        # 1. 创建固定医生：Doctor Panython
        doctor = Doctor(
            doctor_name="Doctor Panython",
            title="主治医师",
            department="全科"
        )
        db.add(doctor)
        db.flush()  # 获取 ID
        print(f"✅ 创建医生: {doctor.doctor_name} (ID: {doctor.id})")

        # 2. 创建固定患者：张三
        patient = Patient(
            patient_name="张三",
            gender="男",
            age=29,
            birthday=date(1995, 1, 1),  # 假设生日
            phone="13800138000"
        )
        db.add(patient)
        db.flush()  # 获取 ID
        print(f"✅ 创建患者: {patient.patient_name} (ID: {patient.id}, 性别: {patient.gender}, 年龄: {patient.age}岁)")

        # 提交事务
        db.commit()

        print("\n" + "=" * 60)
        print("✅ 默认数据初始化成功！")
        print("=" * 60)

        return True

    except Exception as e:
        db.rollback()
        print(f"❌ 默认数据初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


def verify_initialization():
    """验证初始化结果"""
    print("\n" + "=" * 60)
    print("验证初始化结果...")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 查询医生
        doctors = db.query(Doctor).all()
        print(f"\n医生数量: {len(doctors)}")
        for doctor in doctors:
            print(f"  - {doctor.doctor_name} ({doctor.title}, {doctor.department})")

        # 查询患者
        patients = db.query(Patient).all()
        print(f"\n患者数量: {len(patients)}")
        for patient in patients:
            print(f"  - {patient.patient_name} ({patient.gender}, {patient.age}岁)")

        print("\n" + "=" * 60)
        print("✅ 验证完成！")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 验证失败: {e}")

    finally:
        db.close()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("WebMedic 数据库初始化脚本")
    print("=" * 60)

    # 1. 创建数据库
    if not create_database():
        print("\n❌ 初始化失败：数据库创建失败")
        sys.exit(1)

    # 2. 创建数据表
    if not create_tables():
        print("\n❌ 初始化失败：数据表创建失败")
        sys.exit(1)

    # 3. 初始化默认数据
    if not init_default_data():
        print("\n❌ 初始化失败：默认数据创建失败")
        sys.exit(1)

    # 4. 验证初始化结果
    verify_initialization()

    print("\n" + "=" * 60)
    print("🎉 数据库初始化完成！")
    print("=" * 60)
    print("\n提示：")
    print("  - 固定医生：Doctor Panython")
    print("  - 固定患者：张三（男，29岁）")
    print("  - 现在可以启动后端服务了：python run.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
