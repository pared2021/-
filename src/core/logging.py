"""
日志配置模块
支持结构化日志和多种输出格式
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

from src.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """设置应用日志配置"""
    
    # 确保日志目录存在
    log_dir = Path(settings.LOGS_DIR)
    log_dir.mkdir(exist_ok=True)
    
    logging_config = get_logging_config()
    logging.config.dictConfig(logging_config)
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logging_config() -> Dict[str, Any]:
    """获取日志配置字典"""
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL.value,
                "formatter": "detailed" if settings.is_development else "default",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {  # root logger
                "level": settings.LOG_LEVEL.value,
                "handlers": ["console"],
                "propagate": False,
            },
            "src": {
                "level": settings.LOG_LEVEL.value,
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    
    return config


__all__ = [
    "setup_logging",
    "get_logging_config"
] 