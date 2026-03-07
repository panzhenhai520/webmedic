#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Index Service
病历索引与检索服务
第一版使用 mock 数据，预留 PageIndex 接入层
"""

import random
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.models.medical_document import MedicalDocument
from app.models.similar_case_match import SimilarCaseMatch
from app.models.structured_record import StructuredRecord


class IndexService:
    """
    病历索引与检索服务
    第一版使用 mock 索引和 mock 检索
    未来可以平滑切换到 PageIndex
    """

    @staticmethod
    def rebuild_index(db: Session) -> Tuple[int, int]:
        """
        重建索引
        第一版为 mock 实现，仅更新文档状态

        Args:
            db: 数据库会话

        Returns:
            (total_documents, indexed_count)
        """
        # 获取所有待索引的文档
        documents = db.query(MedicalDocument).filter(
            MedicalDocument.index_status.in_(["pending", "failed"])
        ).all()

        total_documents = len(documents)
        indexed_count = 0

        for doc in documents:
            # Mock 索引过程
            # 未来替换为: PageIndex.index_document(doc.file_path)
            doc.parse_status = "done"
            doc.index_status = "done"
            indexed_count += 1

        db.commit()

        return total_documents, indexed_count

    @staticmethod
    def search_similar_cases(
        db: Session,
        session_id: int,
        top_k: int = 3
    ) -> List[SimilarCaseMatch]:
        """
        检索相似病历
        第一版为 mock 实现，返回随机结果

        Args:
            db: 数据库会话
            session_id: 会话ID
            top_k: 返回结果数量

        Returns:
            相似病历匹配结果列表
        """
        # 获取当前会话的结构化记录
        structured_record = db.query(StructuredRecord).filter(
            StructuredRecord.session_id == session_id
        ).order_by(StructuredRecord.created_at.desc()).first()

        if not structured_record:
            raise ValueError(f"会话 {session_id} 没有结构化记录，请先执行结构化抽取")

        # 获取所有已索引的文档
        indexed_documents = db.query(MedicalDocument).filter(
            MedicalDocument.index_status == "done"
        ).all()

        if not indexed_documents:
            raise ValueError("没有已索引的病历文档，请先扫描并索引病历文件")

        # 删除该会话的旧匹配记录
        db.query(SimilarCaseMatch).filter(
            SimilarCaseMatch.session_id == session_id
        ).delete()
        db.commit()

        # Mock 检索逻辑
        # 未来替换为: PageIndex.search(query_text, top_k)
        matches = IndexService._mock_search(
            db=db,
            session_id=session_id,
            documents=indexed_documents,
            structured_record=structured_record,
            top_k=top_k
        )

        return matches

    @staticmethod
    def _mock_search(
        db: Session,
        session_id: int,
        documents: List[MedicalDocument],
        structured_record: StructuredRecord,
        top_k: int
    ) -> List[SimilarCaseMatch]:
        """
        Mock 检索实现
        返回随机选择的文档，并生成模拟的相似度分数和原因

        Args:
            db: 数据库会话
            session_id: 会话ID
            documents: 文档列表
            structured_record: 结构化记录
            top_k: 返回结果数量

        Returns:
            相似病历匹配结果列表
        """
        # 随机选择文档
        selected_docs = random.sample(documents, min(top_k, len(documents)))

        # Mock 原因模板
        reason_templates = [
            "主诉和现病史高度相似，症状描述匹配度高",
            "初步诊断一致，病程发展相似",
            "体格检查结果相近，临床表现类似",
            "既往史和过敏史相关，可参考治疗方案",
            "症状、检查和诊断综合相似度高"
        ]

        matches = []
        for rank, doc in enumerate(selected_docs, start=1):
            # 生成随机相似度分数 (0.75 - 0.95)
            score = round(random.uniform(0.75, 0.95), 4)

            # 随机选择原因
            reason = random.choice(reason_templates)

            # 创建匹配记录
            match = SimilarCaseMatch(
                session_id=session_id,
                document_id=doc.id,
                score=score,
                reason_text=reason,
                rank_no=rank
            )
            db.add(match)
            matches.append(match)

        db.commit()

        return matches

    @staticmethod
    def get_similar_cases_by_session(db: Session, session_id: int) -> List[Tuple[SimilarCaseMatch, MedicalDocument]]:
        """
        获取会话的相似病历匹配结果

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            (匹配记录, 文档) 元组列表
        """
        matches = db.query(SimilarCaseMatch, MedicalDocument).join(
            MedicalDocument,
            SimilarCaseMatch.document_id == MedicalDocument.id
        ).filter(
            SimilarCaseMatch.session_id == session_id
        ).order_by(
            SimilarCaseMatch.rank_no
        ).all()

        return matches


    @staticmethod
    def index_single_document(db: Session, document_id: int) -> bool:
        """
        索引单个文档

        Args:
            db: 数据库会话
            document_id: 文档ID

        Returns:
            是否成功
        """
        document = db.query(MedicalDocument).filter(
            MedicalDocument.id == document_id
        ).first()

        if not document:
            raise ValueError(f"文档不存在: {document_id}")

        # Mock 索引过程
        # 未来替换为: PageIndex.index_document(document.file_path)
        document.parse_status = "done"
        document.index_status = "done"
        db.commit()

        return True


# 预留 PageIndex 接入层
class PageIndexAdapter:
    """
    PageIndex 适配器
    未来接入真实 PageIndex 时实现此类
    """

    @staticmethod
    def index_document(file_path: str) -> bool:
        """
        索引单个文档

        Args:
            file_path: 文件路径

        Returns:
            是否成功
        """
        # TODO: 接入 PageIndex
        # return PageIndex.index(file_path)
        raise NotImplementedError("PageIndex 尚未接入")

    @staticmethod
    def search(query_text: str, top_k: int = 3) -> List[dict]:
        """
        检索相似文档

        Args:
            query_text: 查询文本
            top_k: 返回结果数量

        Returns:
            检索结果列表
        """
        # TODO: 接入 PageIndex
        # return PageIndex.search(query_text, top_k)
        raise NotImplementedError("PageIndex 尚未接入")
