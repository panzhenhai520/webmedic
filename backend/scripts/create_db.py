#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Database Script
创建数据库脚本（独立运行，不依赖app模块）
"""

import pymysql

# 数据库配置
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "www.59697.com"
DB_NAME = "webmedic_demo"

def create_database():
    """创建数据库"""
    print("=" * 60)
    print("WebMedic 数据库创建脚本")
    print("=" * 60)

    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4'
        )

        cursor = connection.cursor()

        # 检查数据库是否存在
        cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{DB_NAME}'")
        exists = cursor.fetchone()

        if exists:
            print(f"✅ 数据库 '{DB_NAME}' 已存在")
        else:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ 数据库 '{DB_NAME}' 创建成功")

        # 验证数据库
        cursor.execute("SHOW DATABASES LIKE 'webmedic%'")
        databases = cursor.fetchall()
        print(f"\n当前 webmedic 相关数据库：")
        for db in databases:
            print(f"  - {db[0]}")

        cursor.close()
        connection.close()

        print("\n" + "=" * 60)
        print("✅ 数据库创建完成！")
        print("=" * 60)
        print("\n下一步：运行初始化脚本创建表和数据")
        print("  python scripts/init_db.py")
        print("=" * 60 + "\n")

        return True

    except Exception as e:
        print(f"❌ 数据库创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_database()
