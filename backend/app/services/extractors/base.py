"""
抽取器抽象基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseExtractor(ABC):
    """抽取器抽象基类"""

    @abstractmethod
    async def extract(
        self,
        dialogue_text: str,
        use_mock: bool = False
    ) -> Dict[str, Any]:
        """
        从对话文本中抽取结构化信息

        Args:
            dialogue_text: 对话文本
            use_mock: 是否使用Mock模式

        Returns:
            结构化数据字典
        """
        pass

    @abstractmethod
    def get_extractor_name(self) -> str:
        """获取抽取器名称"""
        pass
