#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Service
结构化抽取服务
"""

import os
import json
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import StructuredRecord, EncounterSession, TranscriptSegment, Patient
from app.services.llm_service import llm_service
from app.schemas.encounter_schema import StructuredRecordData

logger = logging.getLogger(__name__)


class ExtractService:
    """结构化抽取服务类"""

    @staticmethod
    def load_prompt_template() -> str:
        """
        加载 prompt 模板

        Returns:
            prompt 模板内容
        """
        prompt_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "prompts",
            "extract_structured_record.txt"
        )

        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"加载 prompt 模板失败: {e}")
            raise Exception(f"无法加载 prompt 模板: {str(e)}")

    @staticmethod
    def build_dialogue_text(segments: list) -> str:
        """
        构建对话文本

        Args:
            segments: 转写片段列表

        Returns:
            格式化的对话文本
        """
        dialogue_lines = []
        for seg in segments:
            speaker = "医生" if seg.speaker_role == "doctor" else "患者"
            dialogue_lines.append(f"{speaker}：{seg.transcript_text}")

        return "\n".join(dialogue_lines)

    @staticmethod
    def extract_structured_record(
        db: Session,
        session_id: int
    ) -> StructuredRecord:
        """
        从会话对话中抽取结构化病历

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            结构化病历对象

        Raises:
            ValueError: 如果会话不存在或没有对话记录
            Exception: 抽取失败
        """
        # 验证会话是否存在
        session = db.query(EncounterSession).filter(
            EncounterSession.id == session_id
        ).first()
        if not session:
            raise ValueError(f"会话ID {session_id} 不存在")

        # 获取患者信息
        patient = db.query(Patient).filter(
            Patient.id == session.patient_id
        ).first()
        if not patient:
            raise ValueError(f"患者ID {session.patient_id} 不存在")

        # 获取对话记录
        segments = db.query(TranscriptSegment).filter(
            TranscriptSegment.session_id == session_id
        ).order_by(TranscriptSegment.created_at).all()

        if not segments:
            raise ValueError(f"会话 {session_id} 没有对话记录")

        # 构建对话文本
        dialogue_text = ExtractService.build_dialogue_text(segments)

        # 加载 prompt 模板
        prompt_template = ExtractService.load_prompt_template()

        # 填充 prompt
        prompt = prompt_template.format(
            dialogue_text=dialogue_text,
            patient_name=patient.patient_name,
            gender=patient.gender,
            age=patient.age
        )

        logger.info(f"开始抽取会话 {session_id} 的结构化病历")

        try:
            # 调用 LLM 服务生成结构化数据
            logger.debug("准备调用 LLM 服务...")
            result_json = llm_service.generate_json(prompt=prompt)

            logger.debug(f"LLM 返回结果类型: {type(result_json)}")
            logger.debug(f"LLM 返回结果: {result_json}")

            # 验证返回的 JSON 结构
            logger.debug("准备验证 JSON 结构...")
            structured_data = StructuredRecordData(**result_json)
            logger.debug("JSON 结构验证成功")

            # 检查是否已存在该会话的结构化记录
            existing_record = db.query(StructuredRecord).filter(
                StructuredRecord.session_id == session_id
            ).first()

            if existing_record:
                # 更新现有记录
                existing_record.raw_json = result_json
                existing_record.chief_complaint = structured_data.chief_complaint
                existing_record.present_illness = structured_data.present_illness
                existing_record.past_history = structured_data.past_history
                existing_record.allergy_history = structured_data.allergy_history
                existing_record.physical_exam = structured_data.physical_exam
                existing_record.preliminary_diagnosis = structured_data.preliminary_diagnosis
                existing_record.suggested_exams = structured_data.suggested_exams
                existing_record.warning_flags = structured_data.warning_flags

                db.commit()
                db.refresh(existing_record)

                logger.info(f"更新会话 {session_id} 的结构化病历成功")
                return existing_record
            else:
                # 创建新记录
                record = StructuredRecord(
                    session_id=session_id,
                    schema_version="v1.0",
                    raw_json=result_json,
                    chief_complaint=structured_data.chief_complaint,
                    present_illness=structured_data.present_illness,
                    past_history=structured_data.past_history,
                    allergy_history=structured_data.allergy_history,
                    physical_exam=structured_data.physical_exam,
                    preliminary_diagnosis=structured_data.preliminary_diagnosis,
                    suggested_exams=structured_data.suggested_exams,
                    warning_flags=structured_data.warning_flags
                )

                db.add(record)
                db.commit()
                db.refresh(record)

                logger.info(f"创建会话 {session_id} 的结构化病历成功")
                return record

        except Exception as e:
            logger.error(f"捕获到异常: {type(e).__name__}: {str(e)}", exc_info=True)
            raise Exception(f"结构化抽取失败: {str(e)}")

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
