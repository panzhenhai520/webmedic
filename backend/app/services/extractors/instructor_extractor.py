"""
Instructor抽取器实现（现有逻辑）
"""
import logging
from typing import Dict, Any

from app.services.llm_service import LLMService
from app.utils.medical_vocabulary import (
    extract_complaint_pairs,
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
        严格按 speaker 角色分离：只从患者发言提取症状，从医生发言提取检查和诊断

        Args:
            dialogue_text: 对话文本（格式：每行 "patient: ..." 或 "doctor: ..."）

        Returns:
            模拟的结构化数据
        """
        # 按角色分离对话行
        patient_lines = []
        doctor_lines = []
        for line in dialogue_text.split('\n'):
            stripped = line.strip()
            if stripped.startswith('patient:'):
                patient_lines.append(stripped[len('patient:'):].strip())
            elif stripped.startswith('doctor:'):
                doctor_lines.append(stripped[len('doctor:'):].strip())

        patient_text = ' '.join(patient_lines)
        doctor_text = ' '.join(doctor_lines)

        logger.info(f"Mock提取 - 患者发言({len(patient_lines)}条): {patient_text[:100]}")
        logger.info(f"Mock提取 - 医生发言({len(doctor_lines)}条): {doctor_text[:100]}")

        # 使用主谓配对提取，避免单字误匹配（如"恶心"→心脏、"头晕"→头部）
        pairs, standalone_symptoms, standalone_body_parts = (
            extract_complaint_pairs(patient_text) if patient_text else ([], [], [])
        )
        duration = extract_duration(patient_text) if patient_text else ""

        # 为后续现病史/日志使用，展开所有部位和症状
        body_parts = [bp for bp, _ in pairs] + standalone_body_parts
        symptoms = [sym for _, sym in pairs] + standalone_symptoms

        # 只从医生发言提取疾病诊断
        diseases = extract_diseases(doctor_text) if doctor_text else []

        # 提取过敏史（从患者发言）
        allergy = "无"
        if "过敏" in patient_text:
            if "青霉素" in patient_text:
                allergy = "青霉素过敏"
            elif "头孢" in patient_text:
                allergy = "头孢过敏"
            else:
                allergy = "有过敏史（具体待查）"

        # 提取既往史（从患者发言）
        past_history = "无特殊"
        patient_diseases = extract_diseases(patient_text) if patient_text else []
        if patient_diseases:
            past_history = "、".join(patient_diseases)
        elif "没有" in patient_text and ("病史" in patient_text or "慢性病" in patient_text):
            past_history = "既往体健"

        # 提取体格检查（从医生发言）
        physical_exam = "未提及"
        physical_keywords = ["血压", "心率", "体温", "听诊", "压痛", "mmHg", "次/分", "活动受限", "肌肉紧张"]
        physical_parts = [line for line in doctor_lines if any(kw in line for kw in physical_keywords)]
        if physical_parts:
            physical_exam = "；".join(physical_parts)

        # 提取初步诊断（从医生发言）
        preliminary_diagnosis = "待查"
        diagnosis_keywords = ["诊断为", "初步诊断", "考虑", "可能是", "可能为"]
        for line in doctor_lines:
            for kw in diagnosis_keywords:
                if kw in line:
                    idx = line.find(kw) + len(kw)
                    diag = line[idx:].strip().rstrip('。，,.').strip()[:30]
                    if diag:
                        preliminary_diagnosis = diag
                        break
        if preliminary_diagnosis == "待查" and diseases:
            preliminary_diagnosis = "、".join(diseases)

        # 构建主诉：主语+谓语形式（"颈部疼痛"），避免部位与症状割裂
        complaint_items = []
        for bp, sym in pairs:
            complaint_items.append(f"{bp}{sym}")       # e.g. "颈部疼痛"
        for sym in standalone_symptoms:
            complaint_items.append(sym)                # e.g. "头晕"、"恶心"、"失眠"
        for bp in standalone_body_parts:
            complaint_items.append(f"{bp}不适")        # 有部位但无对应症状

        chief_complaint = "，".join(complaint_items) if complaint_items else "不适"
        if duration:
            chief_complaint += f"，持续约{duration}"

        # 构建现病史
        present_illness = f"患者主诉{chief_complaint}。"
        if duration and (symptoms or body_parts):
            parts_desc = "、".join(body_parts) if body_parts else ""
            symptoms_desc = "、".join(symptoms) if symptoms else ""
            present_illness = f"患者{duration}前出现{parts_desc}{symptoms_desc}。"

        # 治疗方案（仅记录对话中提到的）
        treatment_plan = "未提及"

        logger.info(f"Mock提取结果 - 主诉: {chief_complaint}, 部位: {body_parts}, 症状: {symptoms}")

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
