#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
词库维护系统演示脚本
展示如何使用词库管理功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.medical_vocabulary import MedicalVocabulary
from app.services.vocabulary_service import VocabularyService
from app.schemas.vocabulary import MedicalVocabularyCreate
import json


def demo_list_vocabulary():
    """演示：查询词汇列表"""
    print("\n" + "="*60)
    print("演示1：查询骨科词汇")
    print("="*60)

    db = SessionLocal()
    try:
        items, total = VocabularyService.get_vocabulary_list(
            db=db,
            page=1,
            page_size=5,
            specialty="骨科"
        )

        print(f"\n找到 {total} 条骨科词汇，显示前5条：\n")
        for item in items:
            keywords = json.loads(item.keywords)
            print(f"  [{item.id}] {item.standard_name}")
            print(f"      分类: {item.category}")
            print(f"      关键词: {', '.join(keywords)}")
            print()

    finally:
        db.close()


def demo_check_similar():
    """演示：检查相似词"""
    print("\n" + "="*60)
    print("演示2：检查相似词")
    print("="*60)

    db = SessionLocal()
    try:
        # 检查"肱骨"的相似词
        print("\n检查文本: '肱骨'\n")
        similar_items = VocabularyService.check_vocabulary_similarity(
            db=db,
            text="肱骨",
            category="body_parts",
            threshold=0.8
        )

        if similar_items:
            print(f"发现 {len(similar_items)} 个相似词汇：\n")
            for item in similar_items:
                print(f"  [{item['id']}] {item['standard_name']}")
                print(f"      相似度: {item['similarity']*100:.0f}%")
                print(f"      关键词: {', '.join(item['keywords'])}")
                print()
        else:
            print("未发现相似词汇")

    finally:
        db.close()


def demo_create_vocabulary():
    """演示：创建新词汇"""
    print("\n" + "="*60)
    print("演示3：创建新词汇")
    print("="*60)

    db = SessionLocal()
    try:
        # 创建测试词汇
        vocab_data = MedicalVocabularyCreate(
            category="body_parts",
            standard_name="演示测试词汇",
            keywords=["演示", "测试"],
            description="这是一个演示用的测试词汇",
            specialty="骨科"
        )

        print("\n创建词汇:")
        print(f"  标准名称: {vocab_data.standard_name}")
        print(f"  分类: {vocab_data.category}")
        print(f"  专科: {vocab_data.specialty}")
        print(f"  关键词: {', '.join(vocab_data.keywords)}")

        # 先检查是否存在相似词
        similar_items = VocabularyService.check_vocabulary_similarity(
            db=db,
            text=vocab_data.standard_name,
            category=vocab_data.category,
            threshold=0.9
        )

        if similar_items:
            print(f"\n警告: 发现 {len(similar_items)} 个相似词汇")
            for item in similar_items:
                print(f"  - {item['standard_name']} (相似度: {item['similarity']*100:.0f}%)")
            print("\n跳过创建")
        else:
            vocab = VocabularyService.create_vocabulary(db, vocab_data)
            print(f"\n创建成功! ID: {vocab.id}")

            # 清理：删除测试数据
            VocabularyService.delete_vocabulary(db, vocab.id)
            print("已清理测试数据")

    finally:
        db.close()


def demo_statistics():
    """演示：统计信息"""
    print("\n" + "="*60)
    print("演示4：词库统计信息")
    print("="*60)

    db = SessionLocal()
    try:
        # 统计各分类数量
        categories = ["body_parts", "symptoms", "diseases", "directions"]
        category_names = {
            "body_parts": "身体部位",
            "symptoms": "症状",
            "diseases": "疾病",
            "directions": "方位词"
        }

        print("\n词汇分类统计：\n")
        total = 0
        for category in categories:
            count = db.query(MedicalVocabulary).filter(
                MedicalVocabulary.category == category,
                MedicalVocabulary.status == "active"
            ).count()
            print(f"  {category_names[category]}: {count} 条")
            total += count

        print(f"\n  总计: {total} 条")

        # 统计专科分布
        print("\n\n专科分布统计：\n")
        from sqlalchemy import func
        specialties = db.query(
            MedicalVocabulary.specialty,
            func.count(MedicalVocabulary.id)
        ).filter(
            MedicalVocabulary.specialty.isnot(None),
            MedicalVocabulary.status == "active"
        ).group_by(
            MedicalVocabulary.specialty
        ).all()

        for specialty, count in specialties:
            print(f"  {specialty}: {count} 条")

    finally:
        db.close()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("词库维护系统演示")
    print("="*60)

    try:
        # 运行演示
        demo_statistics()
        demo_list_vocabulary()
        demo_check_similar()
        demo_create_vocabulary()

        print("\n" + "="*60)
        print("演示完成！")
        print("="*60)
        print("\n现在可以访问前端页面进行测试：")
        print("  http://localhost:5173/vocabulary")
        print()

    except Exception as e:
        print(f"\n演示过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
