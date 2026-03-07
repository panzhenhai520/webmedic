"""
LangExtract抽取器实现
"""
import logging
from typing import Dict, Any
import re

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
        Mock模式：返回简化的结构化数据

        Args:
            dialogue_text: 对话文本

        Returns:
            模拟的结构化数据
        """
        # 简化的Mock实现
        symptoms = []
        if "痛" in dialogue_text:
            symptoms.append("疼痛")
        if "晕" in dialogue_text:
            symptoms.append("头晕")

        # 提取时间
        day_matches = re.findall(r'(\d+)\s*天', dialogue_text)
        duration = f"{day_matches[-1]}天" if day_matches else "未提及"

        return {
            "chief_complaint": f"{'、'.join(symptoms) if symptoms else '不适'}{duration}",
            "present_illness_history": f"患者主诉{duration}前出现{'、'.join(symptoms) if symptoms else '不适'}。",
            "past_medical_history": "既往体健",
            "allergy_history": "无" if "过敏" not in dialogue_text else "青霉素过敏",
            "physical_examination": "查体未见明显异常",
            "preliminary_diagnosis": "待查",
            "treatment_plan": "建议进一步检查"
        }

    def get_extractor_name(self) -> str:
        """获取抽取器名称"""
        return "langextract"
