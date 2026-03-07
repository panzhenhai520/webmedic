#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Draft Service
病历草稿生成服务
"""

import os
import json
from typing import Optional
from sqlalchemy.orm import Session
from app.models.emr_draft import EmrDraft
from app.models.structured_record import StructuredRecord
from app.models.medical_document import MedicalDocument
from app.models.similar_case_match import SimilarCaseMatch
from app.core.config import settings
from app.services.llm_service import get_llm_service


class DraftService:
    """病历草稿生成服务"""

    @staticmethod
    def generate_draft(db: Session, session_id: int) -> EmrDraft:
        """
        生成病历草稿

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            病历草稿对象
        """
        # 获取结构化记录
        structured_record = db.query(StructuredRecord).filter(
            StructuredRecord.session_id == session_id
        ).order_by(StructuredRecord.created_at.desc()).first()

        if not structured_record:
            raise ValueError(f"会话 {session_id} 没有结构化记录")

        # 获取相似病历
        similar_cases = db.query(SimilarCaseMatch, MedicalDocument).join(
            MedicalDocument,
            SimilarCaseMatch.document_id == MedicalDocument.id
        ).filter(
            SimilarCaseMatch.session_id == session_id
        ).order_by(SimilarCaseMatch.rank_no).all()

        # 使用 LLM 或 Mock 生成草稿
        if settings.LLM_USE_MOCK:
            draft_content = DraftService._mock_generate_draft(structured_record, similar_cases)
        else:
            draft_content = DraftService._llm_generate_draft(structured_record, similar_cases)

        # 删除旧草稿
        db.query(EmrDraft).filter(
            EmrDraft.session_id == session_id,
            EmrDraft.draft_type == "emr_draft"
        ).delete()

        # 保存草稿
        source_case_ids = ",".join([str(match.document_id) for match, doc in similar_cases]) if similar_cases else None

        draft = EmrDraft(
            session_id=session_id,
            draft_type="emr_draft",
            content_json=draft_content,
            content_text=json.dumps(draft_content, ensure_ascii=False, indent=2),
            source_case_ids=source_case_ids
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)

        return draft

    @staticmethod
    def apply_similar_plan(db: Session, session_id: int, source_document_id: int) -> EmrDraft:
        """
        应用相似病历的检查治疗方案

        Args:
            db: 数据库会话
            session_id: 会话ID
            source_document_id: 来源文档ID

        Returns:
            病历草稿对象
        """
        # 获取结构化记录
        structured_record = db.query(StructuredRecord).filter(
            StructuredRecord.session_id == session_id
        ).order_by(StructuredRecord.created_at.desc()).first()

        if not structured_record:
            raise ValueError(f"会话 {session_id} 没有结构化记录")

        # 获取来源文档
        source_doc = db.query(MedicalDocument).filter(
            MedicalDocument.id == source_document_id
        ).first()

        if not source_doc:
            raise ValueError(f"文档 {source_document_id} 不存在")

        # Mock 应用方案
        draft_content = DraftService._mock_apply_similar_plan(structured_record, source_doc)

        # 删除旧草稿
        db.query(EmrDraft).filter(
            EmrDraft.session_id == session_id,
            EmrDraft.draft_type == "similar_plan"
        ).delete()

        # 保存草稿
        draft = EmrDraft(
            session_id=session_id,
            draft_type="similar_plan",
            content_json=draft_content,
            content_text=json.dumps(draft_content, ensure_ascii=False, indent=2),
            source_case_ids=str(source_document_id)
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)

        return draft

    @staticmethod
    def _mock_generate_draft(structured_record: StructuredRecord, similar_cases) -> dict:
        """
        Mock 生成草稿

        Args:
            structured_record: 结构化记录
            similar_cases: 相似病历列表

        Returns:
            草稿内容字典
        """
        return {
            "chief_complaint": structured_record.chief_complaint or "待补充",
            "present_illness": structured_record.present_illness or "待补充",
            "past_history": structured_record.past_history or "无特殊",
            "allergy_history": structured_record.allergy_history or "无已知药物过敏史",
            "physical_exam": structured_record.physical_exam or "待补充",
            "preliminary_diagnosis": structured_record.preliminary_diagnosis or "待补充",
            "suggested_exams": structured_record.suggested_exams or "建议完善相关检查",
            "treatment_plan": "【AI生成草稿，需医生确认】\n1. 建议完善相关检查明确诊断\n2. 根据检查结果制定治疗方案\n3. 注意观察病情变化"
        }

    @staticmethod
    def _llm_generate_draft(structured_record: StructuredRecord, similar_cases) -> dict:
        """
        使用 LLM 生成草稿

        Args:
            structured_record: 结构化记录
            similar_cases: 相似病历列表

        Returns:
            草稿内容字典
        """
        # 读取 prompt 模板
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "generate_emr_draft.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        # 构建结构化信息
        structured_info = {
            "chief_complaint": structured_record.chief_complaint,
            "present_illness": structured_record.present_illness,
            "past_history": structured_record.past_history,
            "allergy_history": structured_record.allergy_history,
            "physical_exam": structured_record.physical_exam,
            "preliminary_diagnosis": structured_record.preliminary_diagnosis,
            "suggested_exams": structured_record.suggested_exams
        }

        # 构建相似病历信息
        similar_info = []
        for match, doc in similar_cases[:3]:  # 只取前3个
            similar_info.append({
                "file_name": doc.file_name,
                "score": float(match.score) if match.score else 0,
                "reason": match.reason_text
            })

        # 填充 prompt
        prompt = prompt_template.format(
            structured_record=json.dumps(structured_info, ensure_ascii=False, indent=2),
            similar_cases=json.dumps(similar_info, ensure_ascii=False, indent=2)
        )

        # 调用 LLM
        llm_service = get_llm_service()
        response = llm_service.generate_json(
            prompt=prompt
        )

        return response

    @staticmethod
    def _mock_apply_similar_plan(structured_record: StructuredRecord, source_doc: MedicalDocument) -> dict:
        """
        Mock 应用相似方案

        Args:
            structured_record: 结构化记录
            source_doc: 来源文档

        Returns:
            草稿内容字典
        """
        return {
            "chief_complaint": structured_record.chief_complaint or "待补充",
            "present_illness": structured_record.present_illness or "待补充",
            "past_history": structured_record.past_history or "无特殊",
            "allergy_history": structured_record.allergy_history or "无已知药物过敏史",
            "physical_exam": structured_record.physical_exam or "待补充",
            "preliminary_diagnosis": structured_record.preliminary_diagnosis or "待补充",
            "suggested_exams": f"【参考 {source_doc.file_name}】\n建议完善：颈椎X光片或CT、血常规、血脂检查",
            "treatment_plan": f"【参考 {source_doc.file_name} 的治疗方案】\n1. 休息，避免长时间低头\n2. 物理治疗：热敷、按摩\n3. 药物治疗：根据检查结果考虑使用消炎镇痛药物\n4. 定期复查"
        }
