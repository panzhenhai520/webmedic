#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Service
大语言模型服务统一封装
支持 Mock 和真实 DeepSeek API 两种模式
"""

import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM 服务类
    统一封装 DeepSeek API 调用
    支持 Mock/Real 双模式切换
    """

    def __init__(self):
        """初始化 LLM 服务"""
        self.use_mock = settings.LLM_USE_MOCK
        self.client = None

        if not self.use_mock:
            # 真实模式：初始化 OpenAI 客户端连接 DeepSeek
            if not settings.DEEPSEEK_API_KEY:
                logger.warning("DEEPSEEK_API_KEY 未配置，将使用 Mock 模式")
                self.use_mock = True
            else:
                try:
                    self.client = OpenAI(
                        api_key=settings.DEEPSEEK_API_KEY,
                        base_url=settings.DEEPSEEK_BASE_URL
                    )
                    logger.info("LLM Service 初始化成功 - 真实模式")
                except Exception as e:
                    logger.error(f"初始化 OpenAI 客户端失败: {e}")
                    self.use_mock = True
                    logger.warning("降级为 Mock 模式")

        if self.use_mock:
            logger.info("LLM Service 初始化成功 - Mock 模式")

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        生成 JSON 格式的响应

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            解析后的 JSON 字典

        Raises:
            ValueError: 如果返回的不是有效 JSON
            Exception: API 调用失败
        """
        if self.use_mock:
            return self._generate_mock_json(prompt)

        return self._generate_real_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def _generate_mock_json(self, prompt: str) -> Dict[str, Any]:
        """
        Mock 模式：基于对话内容进行简单提取

        Args:
            prompt: 提示词（包含对话内容）

        Returns:
            提取的 JSON 数据
        """
        import re

        logger.info("使用 Mock 模式生成 JSON（基于对话内容）")

        # 根据 prompt 内容返回不同的 mock 数据
        if "结构化" in prompt or "病历" in prompt:
            # 初始化结果
            result = {
                "chief_complaint": "未提及",
                "present_illness": "未提及",
                "past_history": "未提及",
                "allergy_history": "未提及",
                "physical_exam": "未提及",
                "preliminary_diagnosis": "未提及",
                "suggested_exams": "未提及",
                "warning_flags": "未提及"
            }

            # 从 prompt 中精确提取对话行（只取 patient:/doctor: 开头的行）
            # 这样可以避免 prompt 说明文字中的词汇干扰匹配
            patient_lines = []
            doctor_lines = []
            for line in prompt.split('\n'):
                stripped = line.strip()
                if stripped.startswith('patient:'):
                    patient_lines.append(stripped[len('patient:'):].strip())
                elif stripped.startswith('doctor:'):
                    doctor_lines.append(stripped[len('doctor:'):].strip())

            patient_text = ' '.join(patient_lines)
            doctor_text = ' '.join(doctor_lines)

            logger.info(f"Mock提取 - 患者发言({len(patient_lines)}条): {patient_text[:100]}")
            logger.info(f"Mock提取 - 医生发言({len(doctor_lines)}条): {doctor_text[:100]}")

            # 如果没有提取到对话行，说明格式不符，回退为空（不能用整个prompt，否则会误匹配）
            if not patient_lines and not doctor_lines:
                logger.warning("未能从prompt中识别到对话行，使用空文本")
                patient_text = ""
                doctor_text = ""

            # 症状关键词（只从患者发言中提取）
            symptom_keywords = {
                "疼痛": "疼痛", "头痛": "头痛", "头晕": "头晕", "眩晕": "眩晕",
                "恶心": "恶心", "呕吐": "呕吐", "咳嗽": "咳嗽",
                "发烧": "发热", "发热": "发热", "乏力": "乏力",
                "无力": "无力", "不舒服": "不适", "酸痛": "酸痛", "胀痛": "胀痛",
                "疼": "疼痛", "晕": "头晕", "痛": "疼痛"
            }

            # 部位关键词（只从患者发言中提取）
            body_part_keywords = {
                "颈部": "颈部", "脖子": "颈部", "颈椎": "颈椎",
                "头部": "头部", "肩部": "肩部", "背部": "背部",
                "腰部": "腰部", "腿部": "腿部", "胸部": "胸部",
                "腹部": "腹部", "肚子": "腹部", "手部": "手部",
                "脚部": "足部", "膝关节": "膝关节", "腰": "腰部",
                "背": "背部", "头": "头部", "颈": "颈部"
            }

            # 1. 只从患者发言提取症状和部位
            symptoms = []
            body_parts = []

            for keyword, symptom in symptom_keywords.items():
                if keyword in patient_text:
                    if symptom not in symptoms:
                        symptoms.append(symptom)

            for keyword, part in body_part_keywords.items():
                if keyword in patient_text:
                    if part not in body_parts:
                        body_parts.append(part)

            # 2. 只从患者发言提取时间
            days = None
            day_patterns = [
                r'([一二三四五六七八九十百]+)\s*天',
                r'(\d+)\s*天',
                r'(\d+)\s*日',
            ]
            chinese_numbers = {
                '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
                '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                '三四': 3
            }

            for pattern in day_patterns:
                matches = re.findall(pattern, patient_text)
                if matches:
                    last_match = matches[-1]
                    if last_match.isdigit():
                        days = int(last_match)
                    elif last_match in chinese_numbers:
                        days = chinese_numbers[last_match]
                    break

            # 3. 过敏史（从患者发言提取）
            allergy_items = []
            allergens = ["青霉素", "头孢", "磺胺", "海鲜", "花生", "鸡蛋", "牛奶"]
            if any(k in patient_text for k in ["过敏", "不能吃", "不能用"]):
                for allergen in allergens:
                    if allergen in patient_text:
                        allergy_items.append(allergen)

            # 4. 既往史（从患者发言提取）
            past_keywords = {
                "高血压": "高血压", "糖尿病": "糖尿病", "心脏病": "心脏病",
                "肝炎": "肝炎", "肾病": "肾病", "手术": "手术史",
                "颈椎病": "颈椎病", "颈椎": "颈椎病"
            }
            past_history_items = []
            for keyword, disease in past_keywords.items():
                if keyword in patient_text:
                    past_history_items.append(disease)

            # 5. 体格检查（从医生发言提取）
            physical_exam_parts = []
            physical_keywords = ["血压", "心率", "体温", "听诊", "压痛", "活动受限", "肌肉紧张", "mmHg", "次/分"]
            for line in doctor_lines:
                if any(kw in line for kw in physical_keywords):
                    physical_exam_parts.append(line)
            if physical_exam_parts:
                result["physical_exam"] = "；".join(physical_exam_parts)

            # 6. 初步诊断（从医生发言提取）
            diagnosis_keywords = ["诊断为", "初步诊断", "考虑", "可能是", "可能为"]
            for line in doctor_lines:
                for kw in diagnosis_keywords:
                    if kw in line:
                        idx = line.find(kw) + len(kw)
                        diagnosis = line[idx:].strip().rstrip('。，,.')[:30]
                        if diagnosis:
                            result["preliminary_diagnosis"] = diagnosis
                            break

            # 7. 构建主诉（去重，只用患者提到的内容）
            if body_parts or symptoms:
                parts = []
                if body_parts:
                    parts.append(body_parts[0])
                if symptoms:
                    parts.append(symptoms[0])
                chief = "、".join(parts)
                if days:
                    chief += f"{days}天"
                result["chief_complaint"] = chief

            # 8. 构建现病史
            if result["chief_complaint"] != "未提及":
                illness_parts = []
                if days:
                    illness_parts.append(f"患者{days}天前出现")
                else:
                    illness_parts.append("患者近期出现")
                if body_parts:
                    illness_parts.append(body_parts[0])
                if symptoms:
                    illness_parts.append("、".join(symptoms))
                if "加重" in patient_text or "严重" in patient_text:
                    illness_parts.append("，症状加重")
                if "睡眠" in patient_text and ("差" in patient_text or "不好" in patient_text):
                    illness_parts.append("，伴睡眠欠佳")
                result["present_illness"] = "".join(illness_parts) + "。"

            # 9. 过敏史
            if allergy_items:
                result["allergy_history"] = f"对{'、'.join(allergy_items)}过敏"
            elif "没有过敏" in patient_text or "不过敏" in patient_text:
                result["allergy_history"] = "无药物过敏史"

            # 10. 既往史
            if past_history_items:
                result["past_history"] = f"既往有{'、'.join(list(dict.fromkeys(past_history_items)))}"
            elif "没有" in patient_text and ("病史" in patient_text or "慢性" in patient_text):
                result["past_history"] = "既往体健"

            # 11. 建议检查
            if result["preliminary_diagnosis"] != "未提及":
                if "颈椎" in result["preliminary_diagnosis"]:
                    result["suggested_exams"] = "颈椎X光片或CT、血常规"
                elif "头痛" in result["preliminary_diagnosis"]:
                    result["suggested_exams"] = "头颅CT、血常规"
                else:
                    result["suggested_exams"] = "相关影像学检查、血常规"

            # 11. 风险标记
            warnings = []
            if allergy_items:
                warnings.append(f"注意{' '.join(allergy_items)}过敏")
            if "头晕" in symptoms or "眩晕" in symptoms:
                warnings.append("注意防跌倒")

            if warnings:
                result["warning_flags"] = "；".join(warnings)

            logger.info(f"Mock 提取结果：主诉={result['chief_complaint']}")
            return result

        # 默认返回空结构
        return {
            "chief_complaint": "未提及",
            "present_illness": "未提及",
            "past_history": "未提及",
            "allergy_history": "未提及",
            "physical_exam": "未提及",
            "preliminary_diagnosis": "未提及",
            "suggested_exams": "未提及",
            "warning_flags": "未提及"
        }

    def _generate_real_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        真实模式：调用 DeepSeek API

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            解析后的 JSON 字典

        Raises:
            ValueError: 如果返回的不是有效 JSON
            Exception: API 调用失败
        """
        logger.info("使用真实 DeepSeek API 生成 JSON")

        try:
            # 构建消息列表
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })

            # 调用 DeepSeek API
            response = self.client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}
            )

            # 提取响应内容
            content = response.choices[0].message.content
            logger.info(f"DeepSeek API 返回内容: {content[:200]}...")

            # 解析 JSON
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析失败: {e}")
                logger.error(f"原始内容: {content}")
                raise ValueError(f"API 返回的不是有效的 JSON: {e}")

        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {e}")
            raise Exception(f"LLM API 调用失败: {str(e)}")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        生成文本响应（非 JSON）

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            生成的文本

        Raises:
            Exception: API 调用失败
        """
        if self.use_mock:
            return "这是 Mock 模式的文本响应"

        try:
            # 构建消息列表
            messages = []
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            messages.append({
                "role": "user",
                "content": prompt
            })

            # 调用 DeepSeek API
            response = self.client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # 提取响应内容
            content = response.choices[0].message.content
            return content

        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {e}")
            raise Exception(f"LLM API 调用失败: {str(e)}")


# 全局 LLM 服务实例（延迟初始化）
_llm_service_instance = None


def get_llm_service() -> LLMService:
    """
    获取 LLM 服务实例（单例模式）

    Returns:
        LLM 服务实例
    """
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance


# 为了向后兼容，保留 llm_service 变量
# 但改为使用函数获取实例
class _LLMServiceProxy:
    """LLM Service 代理类，用于延迟初始化"""

    def __getattr__(self, name):
        return getattr(get_llm_service(), name)


llm_service = _LLMServiceProxy()
