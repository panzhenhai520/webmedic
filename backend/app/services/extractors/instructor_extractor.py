"""
Instructor抽取器实现（现有逻辑）
"""
import logging
from typing import Dict, Any
import re

from app.services.llm_service import LLMService
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
        Mock模式：从对话文本中提取关键信息

        Args:
            dialogue_text: 对话文本

        Returns:
            模拟的结构化数据
        """
        # 症状关键词映射
        symptom_keywords = {
            "痛": "疼痛", "晕": "头晕", "胀": "肿胀", "麻": "麻木",
            "酸": "酸痛", "累": "疲劳", "咳": "咳嗽", "烧": "发烧"
        }

        # 身体部位关键词
        body_part_keywords = {
            "颈": "颈部", "头": "头部", "肩": "肩部", "背": "背部",
            "腰": "腰部", "腿": "腿部", "手": "手部", "脚": "脚部"
        }

        # 提取症状和部位
        symptoms = []
        body_parts = []

        for keyword, symptom in symptom_keywords.items():
            if keyword in dialogue_text:
                symptoms.append(symptom)

        for keyword, part in body_part_keywords.items():
            if keyword in dialogue_text:
                body_parts.append(part)

        # 提取时间（取最后一次提到的时间）
        day_patterns = [
            r'(\d+)\s*天',
            r'(\d+)\s*日',
            r'(\d+)\s*周',
            r'(\d+)\s*个月'
        ]

        duration = "未提及"
        for pattern in day_patterns:
            matches = re.findall(pattern, dialogue_text)
            if matches:
                duration = f"{matches[-1]}天"  # 取最后一次提到的
                break

        # 提取过敏史
        allergy = "无" if "过敏" not in dialogue_text else "青霉素过敏"

        # 构建结构化结果
        chief_complaint = f"{','.join(body_parts) if body_parts else '颈部'}{','.join(symptoms) if symptoms else '疼痛'}{duration}"

        return {
            "chief_complaint": chief_complaint,
            "present_illness_history": f"患者主诉{chief_complaint}。",
            "past_medical_history": "既往体健",
            "allergy_history": allergy,
            "physical_examination": "颈部活动受限，压痛明显",
            "preliminary_diagnosis": "颈椎病",
            "treatment_plan": "建议进行颈椎X光检查，物理治疗"
        }

    def get_extractor_name(self) -> str:
        """获取抽取器名称"""
        return "instructor"
