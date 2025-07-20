"""
配置提供者

为依赖注入容器提供配置管理功能
"""
from typing import Dict, Any, Optional
import logging
from pathlib import Path


class ConfigProvider:
    """
    配置提供者
    
    为依赖注入容器提供配置相关的服务
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self._config_path = config_path or "config.json"
        self._logger = logging.getLogger(__name__)
        self._default_configs = self._get_default_configs()
    
    def get_config_path(self) -> str:
        """获取配置文件路径"""
        return self._config_path
    
    def get_default_configs(self) -> Dict[str, Any]:
        """获取默认配置"""
        return self._default_configs.copy()
    
    def _get_default_configs(self) -> Dict[str, Any]:
        """获取默认配置定义"""
        return {
            "game_analyzer": {
                "confidence_threshold": 0.8,
                "max_analysis_time": 5.0,
                "use_gpu": True,
                "model_path": "models/game_analyzer.onnx"
            },
            "automation": {
                "action_delay": 0.1,
                "max_retry_count": 3,
                "safety_mode": True,
                "emergency_stop_key": "F12"
            },
            "window_manager": {
                "capture_method": "win32",
                "window_search_timeout": 10,
                "auto_focus": True
            },
            "input_controller": {
                "mouse_speed": 1.0,
                "keyboard_delay": 0.05,
                "scroll_speed": 3
            },
            "performance": {
                "fps_limit": 60,
                "memory_limit_mb": 2048,
                "cpu_usage_limit": 80
            },
            "logging": {
                "level": "INFO",
                "max_file_size_mb": 10,
                "backup_count": 5,
                "console_output": True
            },
            "ui": {
                "theme": "dark",
                "language": "zh_CN",
                "font_size": 12,
                "show_tooltips": True
            },
            "games": {
                "genshin": {
                    "window_title": "原神",
                    "window_class": "UnityWndClass",
                    "resolution": [1920, 1080],
                    "fullscreen": True
                },
                "starrail": {
                    "window_title": "崩坏：星穹铁道",
                    "window_class": "UnityWndClass",
                    "resolution": [1920, 1080],
                    "fullscreen": True
                },
                "zzz": {
                    "window_title": "绝区零",
                    "window_class": "UnityWndClass",
                    "resolution": [1920, 1080],
                    "fullscreen": True
                },
                "arknights": {
                    "window_title": "明日方舟",
                    "window_class": "UnityWndClass",
                    "resolution": [1920, 1080],
                    "fullscreen": False
                }
            },
            "templates": {
                "base_path": "templates",
                "cache_size": 100,
                "auto_reload": True
            },
            "supported_games": ["genshin", "starrail", "zzz", "arknights"]
        }
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置的有效性"""
        try:
            # 验证必需的配置键
            required_keys = ["game_analyzer", "automation", "window_manager"]
            for key in required_keys:
                if key not in config:
                    self._logger.error(f"Missing required config key: {key}")
                    return False
            
            # 验证数值范围
            if "game_analyzer" in config:
                analyzer_config = config["game_analyzer"]
                if "confidence_threshold" in analyzer_config:
                    threshold = analyzer_config["confidence_threshold"]
                    if not (0.0 <= threshold <= 1.0):
                        self._logger.error(f"Invalid confidence_threshold: {threshold}")
                        return False
            
            # 验证文件路径
            if "templates" in config:
                template_config = config["templates"]
                if "base_path" in template_config:
                    base_path = Path(template_config["base_path"])
                    if not base_path.exists():
                        self._logger.warning(f"Template base path does not exist: {base_path}")
                        # 不返回False，因为路径可能稍后创建
            
            return True
            
        except Exception as e:
            self._logger.error(f"Config validation failed: {str(e)}")
            return False
    
    def merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置"""
        try:
            merged = base_config.copy()
            
            def deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
                for key, value in source.items():
                    if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                        deep_merge(target[key], value)
                    else:
                        target[key] = value
            
            deep_merge(merged, override_config)
            return merged
            
        except Exception as e:
            self._logger.error(f"Config merge failed: {str(e)}")
            return base_config
    
    def get_environment_config(self) -> Dict[str, Any]:
        """获取环境相关的配置"""
        import os
        import platform
        
        env_config = {}
        
        # 操作系统相关配置
        if platform.system() == "Windows":
            env_config["window_manager"] = {
                "capture_method": "win32",
                "dpi_aware": True
            }
        elif platform.system() == "Linux":
            env_config["window_manager"] = {
                "capture_method": "x11",
                "dpi_aware": False
            }
        elif platform.system() == "Darwin":
            env_config["window_manager"] = {
                "capture_method": "quartz",
                "dpi_aware": True
            }
        
        # 环境变量配置
        if os.getenv("GAME_AUTOMATION_DEBUG"):
            env_config["logging"] = {
                "level": "DEBUG",
                "console_output": True
            }
        
        if os.getenv("GAME_AUTOMATION_GPU_DISABLED"):
            env_config["game_analyzer"] = {
                "use_gpu": False
            }
        
        return env_config 