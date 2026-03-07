#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebMedic Backend Entry Point
启动 FastAPI 应用
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_ENV == "dev",
        log_level="info"
    )
