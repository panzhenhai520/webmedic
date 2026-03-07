#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Service
结构化抽取服务 - 支持多种抽取器
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.encounter_session import EncounterSession
from app.models.transcript_segment import TranscriptSegment
from app.models.structured_record import StructuredRecord
from app.services.extractors.factory import ExtractorFactory
from app.core.config import settings

logger = logging.getLogger(__name__)


class ExtractService:
    """抽取服务"""

    def __init__(self, extractor_type: Optional[str] = None):
        """
        初始化抽取服务

        Args:
            extractor_type: 抽取器类型，默认从配置读取
        """
        self.extractor = ExtractorFactory.create(extractor_type)
        self.use_mock = settings.LLM_USE_MOCK

    async def extract_from_session(
        self,
        db: Session,
        session_id: int,
        extractor_type: Optional[str] = None
    ) -> StructuredRecord:
        """
        从会话中抽取结构化信息

        Args:
            db: 数据库会话
            session_id: 会话ID
            extractor_type: 抽取器类型（可选，用于临时切换抽取器）

        Returns:
            结构化记录
        """
        try:
            # 查询会话
            session = db.query(EncounterSession).filter(
                EncounterSession.id == session_id
            ).first()

            if not session:
                raise ValueError(f"Session not found: {session_id}")

            # 查询所有转写片段
            segments = db.query(TranscriptSegment).filter(
                TranscriptSegment.session_id == session_id
            ).order_by(TranscriptSegment.sequence_number).all()

            if not segments:
                raise ValueError(f"No transcript segments found for session: {session_id}")

            # 拼接对话文本
            dialogue_text = "\n".join([
                f"{seg.speaker}: {seg.text_content}"
                for seg in segments
            ])

            # 如果指定了临时抽取器类型，创建新的抽取器
            extractor = self.extractor
            if extractor_type:
                extractor = ExtractorFactory.create(extractor_type)

            # 执行抽取
            extracted_data = await extractor.extract(
                dialogue_text=dialogue_text,
                use_mock=self.use_mock
            )

            # 检查是否已存在该会话的结构化记录
            existing_record = db.query(StructuredRecord).filter(
                StructuredRecord.session_id == session_id
            ).first()

            if existing_record:
                # 更新现有记录
                existing_record.chief_complaint = extracted_data.get("chief_complaint", "")
                existing_record.present_illness = extracted_data.get("present_illness_history", "")
                existing_record.past_history = extracted_data.get("past_medical_history", "")
                existing_record.allergy_history = extracted_data.get("allergy_history", "")
                existing_record.physical_exam = extracted_data.get("physical_examination", "")
                existing_record.preliminary_diagnosis = extracted_data.get("preliminary_diagnosis", "")
                existing_record.suggested_exams = extracted_data.get("treatment_plan", "")
                existing_record.extractor_type = extractor.get_extractor_name()
                existing_record.raw_json = extracted_data

                db.commit()
                db.refresh(existing_record)

                logger.info(f"Updated extraction for session {session_id} using {extractor.get_extractor_name()}")
                return existing_record
            else:
                # 创建新记录
                structured_record = StructuredRecord(
                    session_id=session_id,
                    schema_version="v1.0",
                    raw_json=extracted_data,
                    chief_complaint=extracted_data.get("chief_complaint", ""),
                    present_illness=extracted_data.get("present_illness_history", ""),
                    past_history=extracted_data.get("past_medical_history", ""),
                    allergy_history=extracted_data.get("allergy_history", ""),
                    physical_exam=extracted_data.get("physical_examination", ""),
                    preliminary_diagnosis=extracted_data.get("preliminary_diagnosis", ""),
                    suggested_exams=extracted_data.get("treatment_plan", ""),
                    extractor_type=extractor.get_extractor_name()
                )

                db.add(structured_record)
                db.commit()
                db.refresh(structured_record)

                logger.info(f"Extraction completed for session {session_id} using {extractor.get_extractor_name()}")
                return structured_record

        except Exception as e:
            logger.error(f"Failed to extract from session {session_id}: {e}")
            db.rollback()
            raise

    async def compare_extractors(
        self,
        db: Session,
        session_id: int
    ) -> dict:
        """
        对比不同抽取器的结果

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            对比结果
        """
        try:
            # 使用Instructor抽取
            instructor_result = await self.extract_from_session(
                db=db,
                session_id=session_id,
                extractor_type="instructor"
            )

            # 使用LangExtract抽取
            langextract_result = await self.extract_from_session(
                db=db,
                session_id=session_id,
                extractor_type="langextract"
            )

            return {
                "instructor": {
                    "chief_complaint": instructor_result.chief_complaint,
                    "present_illness": instructor_result.present_illness,
                    "preliminary_diagnosis": instructor_result.preliminary_diagnosis,
                },
                "langextract": {
                    "chief_complaint": langextract_result.chief_complaint,
                    "present_illness": langextract_result.present_illness,
                    "preliminary_diagnosis": langextract_result.preliminary_diagnosis,
                }
            }

        except Exception as e:
            logger.error(f"Failed to compare extractors for session {session_id}: {e}")
            raise

    @staticmethod
    def get_structured_record(
        db: Session,
        session_id: int
    ) -> StructuredRecord:
        """
        获取会话的结构化病历

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            结构化病历对象

        Raises:
            ValueError: 如果记录不存在
        """
        record = db.query(StructuredRecord).filter(
            StructuredRecord.session_id == session_id
        ).first()

        if not record:
            raise ValueError(f"会话 {session_id} 的结构化病历不存在")

        return record


# 创建全局实例
extract_service = ExtractService()
