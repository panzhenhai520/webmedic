#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebMedic Configuration Settings
使用 pydantic-settings 管理配置
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""

    # 应用基础配置
    APP_NAME: str = Field(default="WebMedic", description="应用名称")
    APP_ENV: str = Field(default="dev", description="运行环境: dev/prod")
    APP_HOST: str = Field(default="0.0.0.0", description="服务监听地址")
    APP_PORT: int = Field(default=8000, description="服务监听端口")

    # 数据库配置
    DB_HOST: str = Field(default="127.0.0.1", description="数据库主机")
    DB_PORT: int = Field(default=3306, description="数据库端口")
    DB_USER: str = Field(default="root", description="数据库用户名")
    DB_PASSWORD: str = Field(default="", description="数据库密码")
    DB_NAME: str = Field(default="webmedic_demo", description="数据库名称")

    # DeepSeek API 配置
    DEEPSEEK_API_KEY: str = Field(default="", description="DeepSeek API Key")
    DEEPSEEK_BASE_URL: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API Base URL"
    )
    DEEPSEEK_MODEL: str = Field(
        default="deepseek-chat",
        description="DeepSeek 模型名称"
    )

    # OpenAI API 配置（用于 Whisper 语音识别）
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")
    OPENAI_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API Base URL"
    )

    # ASR 引擎配置
    ASR_ENGINE: str = Field(
        default="whisper",
        description="ASR 引擎选择: whisper/dolphin"
    )
    ASR_USE_MOCK: bool = Field(
        default=False,
        description="ASR 是否使用 Mock 模式"
    )

    # Dolphin ASR 配置
    DOLPHIN_API_URL: str = Field(
        default="http://localhost:8000/asr",
        description="Dolphin ASR 服务地址"
    )
    DOLPHIN_API_KEY: str = Field(
        default="",
        description="Dolphin API Key"
    )

    # LLM 服务配置
    LLM_USE_MOCK: bool = Field(
        default=True,
        description="是否使用 Mock 模式（True=Mock, False=真实API）"
    )
    LLM_TIMEOUT: int = Field(
        default=60,
        description="LLM API 超时时间（秒）"
    )
    LLM_MAX_RETRIES: int = Field(
        default=3,
        description="LLM API 最大重试次数"
    )

    # 向量数据库配置
    VECTOR_DB_TYPE: str = Field(
        default="qdrant",
        description="向量数据库类型: qdrant/milvus/weaviate"
    )
    QDRANT_MODE: str = Field(
        default="embedded",
        description="Qdrant模式: embedded/server"
    )
    QDRANT_PATH: str = Field(
        default="./qdrant_storage",
        description="Qdrant内嵌模式存储路径"
    )
    QDRANT_URL: str = Field(
        default="",
        description="Qdrant服务器模式URL"
    )
    QDRANT_API_KEY: str = Field(
        default="",
        description="Qdrant服务器模式API密钥"
    )
    QDRANT_COLLECTION: str = Field(
        default="medical_cases",
        description="Qdrant集合名称"
    )
    QDRANT_VECTOR_SIZE: int = Field(
        default=1024,
        description="向量维度（BGE-M3为1024）"
    )

    # 嵌入模型配置
    EMBEDDING_MODEL: str = Field(
        default="BAAI/bge-m3",
        description="嵌入模型名称"
    )
    EMBEDDING_DEVICE: str = Field(
        default="cpu",
        description="计算设备: cpu/cuda"
    )
    EMBEDDING_BATCH_SIZE: int = Field(
        default=32,
        description="嵌入批处理大小"
    )

    # 抽取器配置
    EXTRACTOR_TYPE: str = Field(
        default="instructor",
        description="抽取器类型: instructor/langextract"
    )

    # 目录配置
    MEDICAL_RECORD_DIR: str = Field(
        default="D:\\webmedic\\backend\\medical_records",
        description="病历文件目录"
    )
    UPLOAD_DIR: str = Field(
        default="D:\\webmedic\\backend\\uploads",
        description="上传文件目录"
    )
    LOG_DIR: str = Field(
        default="D:\\webmedic\\backend\\logs",
        description="日志文件目录"
    )

    # CORS 配置（使用字符串，逗号分隔）
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080",
        description="允许的跨域来源（逗号分隔）"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """将 CORS_ORIGINS 字符串转换为列表"""
        if not self.CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def database_url(self) -> str:
        """生成数据库连接 URL"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )

    def ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.MEDICAL_RECORD_DIR,
            self.UPLOAD_DIR,
            self.LOG_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    class Config:
        """Pydantic 配置"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

# 确保目录存在
settings.ensure_directories()
