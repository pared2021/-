"""
配置管理模块
"""
from ...services.config import Config as ConfigManager
from .performance_config import PerformanceConfig

__all__ = ["ConfigManager", "PerformanceConfig"]
