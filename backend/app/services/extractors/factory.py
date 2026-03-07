"""
抽取器工厂类
"""
import logging
from typing import Optional

from app.core.config import settings
from .base import BaseExtractor
from .instructor_extractor import InstructorExtractor
from .langextract_extractor import LangExtractExtractor

logger = logging.getLogger(__name__)


class ExtractorFactory:
    """抽取器工厂类"""

    @staticmethod
    def create(extractor_type: Optional[str] = None) -> BaseExtractor:
        """
        创建抽取器实例

        Args:
            extractor_type: 抽取器类型（instructor/langextract），默认从配置读取

        Returns:
            抽取器实例
        """
        extractor_type = extractor_type or settings.EXTRACTOR_TYPE

        if extractor_type == "instructor":
            return InstructorExtractor()
        elif extractor_type == "langextract":
            return LangExtractExtractor(
                api_key=settings.DEEPSEEK_API_KEY,
                model="deepseek-chat"
            )
        else:
            raise ValueError(f"Unsupported extractor type: {extractor_type}")
