#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医疗词库管理工具
用于查看、添加、删除词库中的词汇
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.medical_vocabulary import BODY_PARTS, SYMPTOMS, DISEASES, DIRECTIONS


def list_vocabulary(category: str = "all"):
    """
    列出词库内容

    Args:
        category: 类别 (body_parts, symptoms, diseases, directions, all)
    """
    categories = {
        "body_parts": ("身体部位", BODY_PARTS),
        "symptoms": ("症状", SYMPTOMS),
        "diseases": ("疾病", DISEASES),
        "directions": ("方位", DIRECTIONS),
    }

    if category == "all":
        for cat_key, (cat_name, cat_dict) in categories.items():
            print(f"\n{'='*60}")
            print(f"{cat_name} ({cat_key}): {len(cat_dict)} 条")
            print('='*60)
            for key, values in list(cat_dict.items())[:5]:  # 只显示前5条
                print(f"  {key}: {values}")
            if len(cat_dict) > 5:
                print(f"  ... 还有 {len(cat_dict) - 5} 条")
    elif category in categories:
        cat_name, cat_dict = categories[category]
        print(f"\n{cat_name} ({category}): {len(cat_dict)} 条")
        print('='*60)
        for key, values in cat_dict.items():
            print(f"  {key}: {values}")
    else:
        print(f"错误：未知类别 '{category}'")
        print(f"可用类别: {', '.join(categories.keys())}, all")


def search_vocabulary(keyword: str):
    """
    搜索词库

    Args:
        keyword: 搜索关键词
    """
    print(f"\n搜索关键词: '{keyword}'")
    print('='*60)

    found = False

    # 搜索身体部位
    for key, values in BODY_PARTS.items():
        if keyword in key or any(keyword in v for v in values):
            print(f"[身体部位] {key}: {values}")
            found = True

    # 搜索症状
    for key, values in SYMPTOMS.items():
        if keyword in key or any(keyword in v for v in values):
            print(f"[症状] {key}: {values}")
            found = True

    # 搜索疾病
    for key, values in DISEASES.items():
        if keyword in key or any(keyword in v for v in values):
            print(f"[疾病] {key}: {values}")
            found = True

    if not found:
        print(f"未找到包含 '{keyword}' 的词条")


def count_vocabulary():
    """统计词库数量"""
    print("\n词库统计")
    print('='*60)
    print(f"身体部位: {len(BODY_PARTS)} 条")
    print(f"症状: {len(SYMPTOMS)} 条")
    print(f"疾病: {len(DISEASES)} 条")
    print(f"方位: {len(DIRECTIONS)} 条")
    print(f"总计: {len(BODY_PARTS) + len(SYMPTOMS) + len(DISEASES) + len(DIRECTIONS)} 条")


def show_help():
    """显示帮助信息"""
    print("""
医疗词库管理工具

用法:
    python vocabulary_manager.py <命令> [参数]

命令:
    list [category]     列出词库内容
                        category: body_parts, symptoms, diseases, directions, all (默认)

    search <keyword>    搜索词库
                        keyword: 搜索关键词

    count               统计词库数量

    help                显示此帮助信息

示例:
    # 列出所有词库（概览）
    python vocabulary_manager.py list

    # 列出身体部位词库
    python vocabulary_manager.py list body_parts

    # 搜索包含"肱骨"的词条
    python vocabulary_manager.py search 肱骨

    # 统计词库数量
    python vocabulary_manager.py count

添加新词汇:
    直接编辑 app/utils/medical_vocabulary.py 文件
    参考 app/utils/VOCABULARY_MAINTENANCE.md 维护指南
    """)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else "all"
        list_vocabulary(category)
    elif command == "search":
        if len(sys.argv) < 3:
            print("错误：search 命令需要提供关键词")
            print("用法: python vocabulary_manager.py search <keyword>")
            return
        keyword = sys.argv[2]
        search_vocabulary(keyword)
    elif command == "count":
        count_vocabulary()
    elif command == "help":
        show_help()
    else:
        print(f"错误：未知命令 '{command}'")
        show_help()


if __name__ == "__main__":
    main()
