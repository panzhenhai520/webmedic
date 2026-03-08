#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vocabulary Service
词库管理服务
"""

import json
import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from difflib import SequenceMatcher

from app.models.medical_vocabulary import MedicalVocabulary
from app.models.icd_code import ICDCode
from app.models.surgery_code import SurgeryCode
from app.schemas.vocabulary import (
    MedicalVocabularyCreate,
    MedicalVocabularyUpdate,
    ICDCodeCreate,
    ICDCodeUpdate,
    SurgeryCodeCreate,
    SurgeryCodeUpdate,
)

logger = logging.getLogger(__name__)


class VocabularyService:
    """词库管理服务"""

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        计算两个文本的相似度

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            相似度 (0-1)
        """
        return SequenceMatcher(None, text1, text2).ratio()

    # ============ 医学词汇 ============

    @staticmethod
    def get_vocabulary_list(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        specialty: Optional[str] = None,
        keyword: Optional[str] = None,
        status: str = "active"
    ) -> Tuple[List[MedicalVocabulary], int]:
        """
        获取医学词汇列表

        Args:
            db: 数据库会话
            page: 页码
            page_size: 每页数量
            category: 分类筛选
            specialty: 专科筛选
            keyword: 关键词搜索
            status: 状态筛选

        Returns:
            (词汇列表, 总数)
        """
        query = db.query(MedicalVocabulary)

        # 状态筛选
        if status:
            query = query.filter(MedicalVocabulary.status == status)

        # 分类筛选
        if category:
            query = query.filter(MedicalVocabulary.category == category)

        # 专科筛选
        if specialty:
            query = query.filter(MedicalVocabulary.specialty == specialty)

        # 关键词搜索
        if keyword:
            query = query.filter(
                or_(
                    MedicalVocabulary.standard_name.like(f"%{keyword}%"),
                    MedicalVocabulary.keywords.like(f"%{keyword}%"),
                    MedicalVocabulary.description.like(f"%{keyword}%")
                )
            )

        # 总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        items = query.order_by(MedicalVocabulary.id.desc()).offset(offset).limit(page_size).all()

        return items, total

    @staticmethod
    def get_vocabulary_by_id(db: Session, vocab_id: int) -> Optional[MedicalVocabulary]:
        """获取单个医学词汇"""
        return db.query(MedicalVocabulary).filter(MedicalVocabulary.id == vocab_id).first()

    @staticmethod
    def check_vocabulary_similarity(
        db: Session,
        text: str,
        category: Optional[str] = None,
        threshold: float = 0.8
    ) -> List[dict]:
        """
        检查相似词汇

        Args:
            db: 数据库会话
            text: 待检查文本
            category: 限定分类
            threshold: 相似度阈值

        Returns:
            相似词汇列表
        """
        query = db.query(MedicalVocabulary).filter(MedicalVocabulary.status == "active")

        if category:
            query = query.filter(MedicalVocabulary.category == category)

        all_vocabs = query.all()
        similar_items = []

        for vocab in all_vocabs:
            # 检查标准名称相似度
            similarity = VocabularyService.calculate_similarity(text, vocab.standard_name)

            if similarity >= threshold:
                keywords = json.loads(vocab.keywords) if vocab.keywords else []
                similar_items.append({
                    "id": vocab.id,
                    "standard_name": vocab.standard_name,
                    "keywords": keywords,
                    "similarity": round(similarity, 2)
                })
                continue

            # 检查关键词相似度
            keywords = json.loads(vocab.keywords) if vocab.keywords else []
            for kw in keywords:
                similarity = VocabularyService.calculate_similarity(text, kw)
                if similarity >= threshold:
                    similar_items.append({
                        "id": vocab.id,
                        "standard_name": vocab.standard_name,
                        "keywords": keywords,
                        "similarity": round(similarity, 2)
                    })
                    break

        # 按相似度排序
        similar_items.sort(key=lambda x: x["similarity"], reverse=True)

        return similar_items

    @staticmethod
    def create_vocabulary(
        db: Session,
        vocab_data: MedicalVocabularyCreate
    ) -> MedicalVocabulary:
        """
        创建医学词汇

        Args:
            db: 数据库会话
            vocab_data: 词汇数据

        Returns:
            创建的词汇对象
        """
        vocab = MedicalVocabulary(
            category=vocab_data.category,
            standard_name=vocab_data.standard_name,
            keywords=json.dumps(vocab_data.keywords, ensure_ascii=False),
            description=vocab_data.description,
            specialty=vocab_data.specialty,
            status="active"
        )

        db.add(vocab)
        db.commit()
        db.refresh(vocab)

        logger.info(f"Created vocabulary: {vocab.standard_name}")
        return vocab

    @staticmethod
    def update_vocabulary(
        db: Session,
        vocab_id: int,
        vocab_data: MedicalVocabularyUpdate
    ) -> Optional[MedicalVocabulary]:
        """
        更新医学词汇

        Args:
            db: 数据库会话
            vocab_id: 词汇ID
            vocab_data: 更新数据

        Returns:
            更新后的词汇对象
        """
        vocab = db.query(MedicalVocabulary).filter(MedicalVocabulary.id == vocab_id).first()

        if not vocab:
            return None

        # 更新字段
        if vocab_data.standard_name is not None:
            vocab.standard_name = vocab_data.standard_name
        if vocab_data.keywords is not None:
            vocab.keywords = json.dumps(vocab_data.keywords, ensure_ascii=False)
        if vocab_data.description is not None:
            vocab.description = vocab_data.description
        if vocab_data.specialty is not None:
            vocab.specialty = vocab_data.specialty
        if vocab_data.status is not None:
            vocab.status = vocab_data.status

        db.commit()
        db.refresh(vocab)

        logger.info(f"Updated vocabulary: {vocab.standard_name}")
        return vocab

    @staticmethod
    def delete_vocabulary(db: Session, vocab_id: int) -> bool:
        """
        删除医学词汇（软删除）

        Args:
            db: 数据库会话
            vocab_id: 词汇ID

        Returns:
            是否成功
        """
        vocab = db.query(MedicalVocabulary).filter(MedicalVocabulary.id == vocab_id).first()

        if not vocab:
            return False

        vocab.status = "inactive"
        db.commit()

        logger.info(f"Deleted vocabulary: {vocab.standard_name}")
        return True

    # ============ ICD编码 ============
    # (类似的CRUD方法，这里省略，实际实现时需要完整编写)

    # ============ 手术编码 ============
    # (类似的CRUD方法，这里省略，实际实现时需要完整编写)
