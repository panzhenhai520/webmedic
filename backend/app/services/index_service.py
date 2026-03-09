#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Index Service
病历索引与检索服务 - 使用向量数据库
"""

import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.medical_document import MedicalDocument
from app.models.similar_case_match import SimilarCaseMatch
from app.models.structured_record import StructuredRecord
from app.services.vector.factory import VectorDBFactory
from app.services.embedding_service import get_embedding_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class IndexService:
    """病历索引与检索服务"""

    def __init__(self):
        self.vector_db = VectorDBFactory.create()
        self.embedding_service = get_embedding_service()
        self.collection_name = settings.QDRANT_COLLECTION

    async def initialize(self) -> None:
        """初始化索引服务"""
        try:
            # 初始化向量数据库
            await self.vector_db.initialize()

            # 检查集合是否存在，不存在则创建
            if not await self.vector_db.collection_exists(self.collection_name):
                vector_size = self.embedding_service.get_vector_size()
                await self.vector_db.create_collection(
                    collection_name=self.collection_name,
                    vector_size=vector_size,
                    distance="cosine"
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize index service: {e}")
            raise

    async def index_document(
        self,
        db: Session,
        document_id: int
    ) -> None:
        """
        索引单个文档

        Args:
            db: 数据库会话
            document_id: 文档ID
        """
        try:
            # 查询文档
            document = db.query(MedicalDocument).filter(
                MedicalDocument.id == document_id
            ).first()

            if not document:
                raise ValueError(f"Document not found: {document_id}")

            # 从 PDF 文件中提取文本
            import os
            if not os.path.exists(document.file_path):
                raise ValueError(f"Document file not found: {document.file_path}")

            # 解析 PDF 内容
            try:
                from pypdf import PdfReader
                with open(document.file_path, 'rb') as file:
                    pdf_reader = PdfReader(file)
                    text_content = ""
                    for page in pdf_reader.pages:
                        text_content += page.extract_text()

                if not text_content or len(text_content.strip()) < 10:
                    raise ValueError(f"Document has no valid content: {document_id}")

            except Exception as e:
                logger.error(f"Failed to parse PDF {document.file_path}: {e}")
                document.parse_status = "failed"
                document.index_status = "failed"
                db.commit()
                raise ValueError(f"Failed to parse PDF: {e}")

            # 生成向量
            vector = self.embedding_service.encode_single(text_content)

            # 构建元数据
            payload = {
                "document_id": document.id,
                "file_name": document.file_name,
                "file_path": document.file_path,
                "parsed_content": text_content[:500],  # 只存储前500字符
                "created_at": document.created_at.isoformat() if document.created_at else None,
            }

            # 插入向量数据库
            # 使用 UUID 格式的 ID（Qdrant 要求）
            import uuid
            point_id = str(uuid.UUID(int=document.id, version=4))

            await self.vector_db.upsert_vectors(
                collection_name=self.collection_name,
                ids=[point_id],
                vectors=[vector],
                payloads=[payload]
            )

            # 更新文档状态
            document.parse_status = "done"
            document.index_status = "done"
            db.commit()

            logger.info(f"Document indexed successfully: {document_id}")

        except Exception as e:
            logger.error(f"Failed to index document {document_id}: {e}")
            # 更新文档索引状态为失败
            document = db.query(MedicalDocument).filter(
                MedicalDocument.id == document_id
            ).first()
            if document:
                document.index_status = "failed"
                db.commit()
            raise

    async def search_similar_documents(
        self,
        query_text: str,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[dict]:
        """
        搜索相似文档

        Args:
            query_text: 查询文本
            limit: 返回结果数量
            score_threshold: 相似度阈值

        Returns:
            相似文档列表
        """
        try:
            # 生成查询向量
            query_vector = self.embedding_service.encode_single(query_text)

            # 搜索向量数据库
            results = await self.vector_db.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )

            # 转换结果格式
            similar_docs = []
            for result in results:
                similar_docs.append({
                    "document_id": result.payload.get("document_id"),
                    "file_name": result.payload.get("file_name"),
                    "similarity_score": result.score,
                    "content_preview": result.payload.get("parsed_content", "")
                })

            logger.info(f"Found {len(similar_docs)} similar documents")
            return similar_docs

        except Exception as e:
            logger.error(f"Failed to search similar documents: {e}")
            raise

    async def search_similar_cases(
        self,
        db: Session,
        session_id: int,
        top_k: int = 3
    ) -> List[SimilarCaseMatch]:
        """
        检索相似病历

        Args:
            db: 数据库会话
            session_id: 会话ID
            top_k: 返回结果数量

        Returns:
            相似病历匹配结果列表
        """
        try:
            # 获取当前会话的结构化记录
            structured_record = db.query(StructuredRecord).filter(
                StructuredRecord.session_id == session_id
            ).order_by(StructuredRecord.created_at.desc()).first()

            if not structured_record:
                raise ValueError(f"会话 {session_id} 没有结构化记录，请先执行结构化抽取")

            # 构建查询文本
            query_text = f"{structured_record.chief_complaint} {structured_record.present_illness}"

            # 搜索相似文档（降低阈值以适应 Mock 数据）
            similar_docs = await self.search_similar_documents(
                query_text=query_text,
                limit=top_k,
                score_threshold=0.5
            )

            # 删除该会话的旧匹配记录
            db.query(SimilarCaseMatch).filter(
                SimilarCaseMatch.session_id == session_id
            ).delete()
            db.commit()

            # 创建新的匹配记录
            matches = []
            for rank, doc_info in enumerate(similar_docs, start=1):
                match = SimilarCaseMatch(
                    session_id=session_id,
                    document_id=doc_info["document_id"],
                    score=doc_info["similarity_score"],
                    reason_text=f"向量相似度: {doc_info['similarity_score']:.4f}",
                    rank_no=rank
                )
                db.add(match)
                matches.append(match)

            db.commit()

            logger.info(f"Found {len(matches)} similar cases for session {session_id}")
            return matches

        except Exception as e:
            logger.error(f"Failed to search similar cases for session {session_id}: {e}")
            raise

    async def delete_document_index(
        self,
        db: Session,
        document_id: int
    ) -> None:
        """
        删除文档索引

        Args:
            db: 数据库会话
            document_id: 文档ID
        """
        try:
            # 从向量数据库删除（使用 UUID 格式）
            import uuid
            point_id = str(uuid.UUID(int=document_id, version=4))

            await self.vector_db.delete_vectors(
                collection_name=self.collection_name,
                ids=[point_id]
            )

            # 更新文档索引状态
            document = db.query(MedicalDocument).filter(
                MedicalDocument.id == document_id
            ).first()
            if document:
                document.index_status = "pending"
                db.commit()

            logger.info(f"Document index deleted: {document_id}")

        except Exception as e:
            logger.error(f"Failed to delete document index {document_id}: {e}")
            raise

    async def get_index_stats(self) -> dict:
        """获取索引统计信息"""
        try:
            collection_info = await self.vector_db.get_collection_info(
                self.collection_name
            )
            return {
                "collection_name": collection_info["name"],
                "total_vectors": collection_info["vectors_count"],
                "total_points": collection_info["points_count"],
                "status": collection_info["status"],
                "vector_size": collection_info["config"]["vector_size"],
                "distance_metric": collection_info["config"]["distance"],
            }
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            raise

    async def close(self) -> None:
        """关闭服务"""
        await self.vector_db.close()

    @staticmethod
    def get_similar_cases_by_session(
        db: Session,
        session_id: int
    ) -> List[Tuple[SimilarCaseMatch, MedicalDocument]]:
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


# 全局单例
_index_service: Optional[IndexService] = None


async def get_index_service() -> IndexService:
    """获取索引服务单例"""
    global _index_service
    if _index_service is None:
        _index_service = IndexService()
        await _index_service.initialize()
    return _index_service


# 同步包装方法（用于非异步上下文）
class IndexServiceSync:
    """索引服务的同步包装器"""

    @staticmethod
    def index_single_document(db: Session, document_id: int) -> None:
        """
        同步索引单个文档

        Args:
            db: 数据库会话
            document_id: 文档ID
        """
        import asyncio

        async def _index():
            service = await get_index_service()
            await service.index_document(db, document_id)

        try:
            # 在新的事件循环中运行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_index())
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Failed to index document {document_id}: {e}")
            raise

    @staticmethod
    def rebuild_index(db: Session) -> tuple[int, int]:
        """
        同步重建索引

        Args:
            db: 数据库会话

        Returns:
            (总文档数, 成功索引数)
        """
        import asyncio
        from app.models.medical_document import MedicalDocument

        async def _rebuild():
            service = await get_index_service()

            # 查询所有已解析的文档
            documents = db.query(MedicalDocument).filter(
                MedicalDocument.parse_status == "done"
            ).all()

            total = len(documents)
            indexed = 0

            for doc in documents:
                try:
                    await service.index_document(db, doc.id)
                    indexed += 1
                except Exception as e:
                    logger.error(f"Failed to index document {doc.id}: {e}")

            return total, indexed

        try:
            # 在新的事件循环中运行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(_rebuild())
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            raise


# 为了向后兼容，创建一个别名
IndexService.index_single_document = IndexServiceSync.index_single_document
IndexService.rebuild_index = IndexServiceSync.rebuild_index
