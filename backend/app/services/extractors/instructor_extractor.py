"""
Instructor抽取器实现（现有逻辑）
"""
import logging
from typing import Dict, Any

from app.services.llm_service import LLMService
from app.utils.medical_vocabulary import (
    extract_body_parts,
    extract_symptoms,
    extract_diseases,
    extract_duration
)
from .base import BaseExtractor

logger = logging.getLogger(__name__)


class InstructorExtractor(BaseExtractor):
    """Instructor抽取器实现"""

    def __init__(self):
        self.llm_service = LLMService()

    async def extract(
        self,
        dialogue_text: str,
        use_mock: bool = False
    ) -> Dict[str, Any]:
        """
        使用Instructor从对话文本中抽取结构化信息

        Args:
            dialogue_text: 对话文本
            use_mock: 是否使用Mock模式

        Returns:
            结构化数据字典
        """
        try:
            if use_mock:
                return self._generate_mock_json(dialogue_text)

            # 使用LLM服务进行抽取
            result = await self.llm_service.extract_structured_record(dialogue_text)
            logger.info("Instructor extraction completed")
            return result

        except Exception as e:
            logger.error(f"Instructor extraction failed: {e}")
            raise

    def _generate_mock_json(self, dialogue_text: str) -> Dict[str, Any]:
        """
        Mock模式：使用医疗词库从对话文本中提取关键信息

        Args:
            dialogue_text: 对话文本

        Returns:
            模拟的结构化数据
        """
        # 使用医疗词库提取信息
        body_parts = extract_body_parts(dialogue_text)
        symptoms = extract_symptoms(dialogue_text)
        diseases = extract_diseases(dialogue_text)
        duration = extract_duration(dialogue_text)

        # 提取过敏史
        allergy = "无"
        if "过敏" in dialogue_text:
            if "青霉素" in dialogue_text:
                allergy = "青霉素过敏"
            elif "头孢" in dialogue_text:
                allergy = "头孢过敏"
            else:
                allergy = "有过敏史（具体待查）"

        # 提取既往史
        past_history = "无特殊"
        if diseases:
            past_history = "、".join(diseases)
        elif "之前" in dialogue_text and "没有" in dialogue_text:
            past_history = "既往体健"

        # 构建主诉
        chief_complaint_parts = []
        if body_parts:
            chief_complaint_parts.append("、".join(body_parts))
        if symptoms:
            chief_complaint_parts.append("、".join(symptoms))
        if duration:
            chief_complaint_parts.append(duration)

        chief_complaint = "，".join(chief_complaint_parts) if chief_complaint_parts else "不适"

        # 构建现病史
        present_illness = f"患者主诉{chief_complaint}。"
        if duration and (symptoms or body_parts):
            parts_desc = "、".join(body_parts) if body_parts else ""
            symptoms_desc = "、".join(symptoms) if symptoms else ""
            present_illness = f"患者主诉{duration}前出现{parts_desc}{symptoms_desc}。"

        # 体格检查（仅记录对话中明确提到的）
        physical_exam = "未提及"

        # 初步诊断（如果对话中提到了疾病名称，记录下来）
        preliminary_diagnosis = "待查"
        if diseases:
            preliminary_diagnosis = "、".join(diseases)

        # 治疗方案（仅记录对话中提到的）
        treatment_plan = "未提及"

        return {
            "chief_complaint": chief_complaint,
            "present_illness_history": present_illness,
            "past_medical_history": past_history,
            "allergy_history": allergy,
            "physical_examination": physical_exam,
            "preliminary_diagnosis": preliminary_diagnosis,
            "treatment_plan": treatment_plan
        }

    def get_extractor_name(self) -> str:
        """获取抽取器名称"""
        return "instructor"
