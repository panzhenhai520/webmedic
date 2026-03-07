#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clinical Hint Service
临床提示生成服务
"""

import os
import json
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.clinical_hint import ClinicalHint
from app.models.structured_record import StructuredRecord
from app.models.medical_document import MedicalDocument
from app.models.similar_case_match import SimilarCaseMatch
from app.core.config import settings
from app.services.llm_service import get_llm_service


class ClinicalHintService:
    """临床提示生成服务"""

    @staticmethod
    def generate_hints(db: Session, session_id: int) -> Dict[str, List]:
        """
        生成临床提示

        Args:
            db: 数据库会话
            session_id: 会话ID

        Returns:
            包含 warnings, followup_questions, suggested_exams 的字典
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

        # 使用 LLM 或 Mock 生成提示
        if settings.LLM_USE_MOCK:
            hints = ClinicalHintService._mock_generate_hints(structured_record, similar_cases)
        else:
            hints = ClinicalHintService._llm_generate_hints(structured_record, similar_cases)

        # 删除旧提示
        db.query(ClinicalHint).filter(
            ClinicalHint.session_id == session_id
        ).delete()

        # 保存风险提示
        for warning in hints.get("warnings", []):
            hint = ClinicalHint(
                session_id=session_id,
                hint_type="warning",
                hint_title=warning.get("hint_title"),
                hint_content=warning.get("hint_content"),
                severity=warning.get("severity", "info"),
                source_model="mock" if settings.LLM_USE_MOCK else settings.DEEPSEEK_MODEL
            )
            db.add(hint)

        # 保存追问建议
        for question in hints.get("followup_questions", []):
            hint = ClinicalHint(
                session_id=session_id,
                hint_type="question",
                hint_title=question.get("question"),
                hint_content=question.get("reason", ""),
                severity="info",
                source_model="mock" if settings.LLM_USE_MOCK else settings.DEEPSEEK_MODEL
            )
            db.add(hint)

        # 保存建议检查
        for exam in hints.get("suggested_exams", []):
            hint = ClinicalHint(
                session_id=session_id,
                hint_type="exam",
                hint_title=exam.get("exam_name"),
                hint_content=exam.get("reason", ""),
                severity="info",
                source_model="mock" if settings.LLM_USE_MOCK else settings.DEEPSEEK_MODEL
            )
            db.add(hint)

        db.commit()

        return hints

    @staticmethod
    def _mock_generate_hints(structured_record: StructuredRecord, similar_cases) -> Dict[str, List]:
        """
        Mock 生成提示

        Args:
            structured_record: 结构化记录
            similar_cases: 相似病历列表

        Returns:
            提示字典
        """
        warnings = []
        followup_questions = []
        suggested_exams = []

        # 根据过敏史生成风险提示
        if structured_record.allergy_history and "青霉素" in structured_record.allergy_history:
            warnings.append({
                "hint_title": "药物过敏提示",
                "hint_content": "患者对青霉素过敏，用药时需避免使用青霉素类抗生素",
                "severity": "warn"
            })

        # 根据症状生成风险提示
        if structured_record.chief_complaint and ("头晕" in structured_record.chief_complaint or "眩晕" in structured_record.chief_complaint):
            warnings.append({
                "hint_title": "需注意跌倒风险",
                "hint_content": "患者有头晕症状，建议注意防跌倒，避免高空作业和驾驶",
                "severity": "warn"
            })

        # 生成追问建议
        if not structured_record.past_history or structured_record.past_history == "无特殊":
            followup_questions.append({
                "question": "是否有高血压、糖尿病等慢性病史？",
                "reason": "了解既往病史有助于评估当前病情和用药风险"
            })

        if structured_record.physical_exam and "血压" in structured_record.physical_exam:
            # 如果已有血压数据，不需要追问
            pass
        else:
            followup_questions.append({
                "question": "最近是否测量过血压？",
                "reason": "血压数据有助于评估心血管状况"
            })

        # 生成建议检查
        if structured_record.preliminary_diagnosis and "颈椎" in structured_record.preliminary_diagnosis:
            suggested_exams.append({
                "exam_name": "颈椎X光片或CT",
                "reason": "明确颈椎病变程度，指导治疗方案"
            })
            suggested_exams.append({
                "exam_name": "血常规",
                "reason": "排除感染等其他因素"
            })

        # 如果没有生成任何提示，添加默认提示
        if not warnings:
            warnings.append({
                "hint_title": "一般提示",
                "hint_content": "建议根据检查结果制定治疗方案，注意观察病情变化",
                "severity": "info"
            })

        if not suggested_exams:
            suggested_exams.append({
                "exam_name": "相关检查",
                "reason": "根据症状和初步诊断完善相关检查"
            })

        return {
            "warnings": warnings,
            "followup_questions": followup_questions,
            "suggested_exams": suggested_exams
        }

    @staticmethod
    def _llm_generate_hints(structured_record: StructuredRecord, similar_cases) -> Dict[str, List]:
        """
        使用 LLM 生成提示

        Args:
            structured_record: 结构化记录
            similar_cases: 相似病历列表

        Returns:
            提示字典
        """
        # 读取 prompt 模板
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "generate_clinical_hints.txt")
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
