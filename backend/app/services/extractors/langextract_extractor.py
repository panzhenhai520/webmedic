"""
LangExtract抽取器实现
"""
import logging
from typing import Dict, Any

from app.utils.medical_vocabulary import (
    extract_body_parts,
    extract_symptoms,
    extract_diseases,
    extract_duration
)
from .base import BaseExtractor

logger = logging.getLogger(__name__)


class LangExtractExtractor(BaseExtractor):
    """LangExtract抽取器实现"""

    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        """
        初始化LangExtract抽取器

        Args:
            api_key: DeepSeek API密钥
            model: 模型名称
        """
        self.api_key = api_key
        self.model = model
        # 注意：langextract库需要安装后才能导入
        try:
            from langextract import LangExtract
            self.extractor = LangExtract(api_key=api_key, model=model)
        except ImportError:
            logger.warning("langextract not installed, will use mock mode")
            self.extractor = None

    async def extract(
        self,
        dialogue_text: str,
        use_mock: bool = False
    ) -> Dict[str, Any]:
        """
        使用LangExtract从对话文本中抽取结构化信息

        Args:
            dialogue_text: 对话文本
            use_mock: 是否使用Mock模式

        Returns:
            结构化数据字典
        """
        try:
            if use_mock or not self.extractor:
                return self._generate_mock_json(dialogue_text)

            # 定义抽取schema
            schema = {
                "chief_complaint": "主诉",
                "present_illness_history": "现病史",
                "past_medical_history": "既往史",
                "allergy_history": "过敏史",
                "physical_examination": "体格检查",
                "preliminary_diagnosis": "初步诊断",
                "treatment_plan": "治疗方案"
            }

            # 使用LangExtract进行抽取
            result = self.extractor.extract(
                text=dialogue_text,
                schema=schema
            )

            logger.info("LangExtract extraction completed")
            return result

        except Exception as e:
            logger.error(f"LangExtract extraction failed: {e}")
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

        return {
            "chief_complaint": chief_complaint,
            "present_illness_history": present_illness,
            "past_medical_history": past_history,
            "allergy_history": allergy,
            "physical_examination": "未提及",
            "preliminary_diagnosis": "、".join(diseases) if diseases else "待查",
            "treatment_plan": "未提及"
        }

    def get_extractor_name(self) -> str:
        """获取抽取器名称"""
        return "langextract"
