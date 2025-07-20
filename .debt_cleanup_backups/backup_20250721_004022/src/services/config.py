#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理服务 - 基于PyQt6 QSettings标准模式
遵循PyQt6最佳实践，使用QSettings进行配置存储
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field

# PyQt6导入
try:
    from PyQt6.QtCore import QSettings, QCoreApplication
    from src.common.app_config import init_application_metadata, get_app_info
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    print("⚠️ PyQt6不可用，配置服务将使用JSON文件模式")

# 可选依赖
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


@dataclass
class ConfigDefaults:
    """配置默认值定义"""
    
    # 应用程序配置
    APPLICATION = {
        "name": "GameAutomationTool",
        "version": "1.0.0", 
        "window_title": "游戏自动操作工具",
        "window_size": [800, 600],
        "language": "zh_CN",
        "theme": "default"
    }
    
    # 热键配置
    HOTKEYS = {
        "start_record": "F9",
        "stop_record": "F10",
        "start_playback": "F11", 
        "stop_playback": "F12"
    }
    
    # 播放选项
    PLAYBACK_OPTIONS = {
        "speed": 1.0,
        "loop_count": 1,
        "random_delay": 0.0
    }
    
    # 窗口管理
    WINDOW = {
        "last_selected": "",
        "refresh_interval": 1000,
        "screenshot_interval": 0.1,
        "activation_delay": 0.5
    }
    
    # 模板配置
    TEMPLATE = {
        "duration": 300,
        "interval": 0.5,
        "last_dir": "templates",
        "save_dir": "templates",
        "similarity_threshold": 0.9,
        "min_size": 20,
        "max_size": 200
    }
    
    # 游戏状态
    GAME_STATE = {
        "analysis_interval": 1000,
        "confidence_threshold": 0.8,
        "detection_methods": ["template_matching", "feature_detection"],
        "auto_save": True,
        "max_history_size": 1000,
        "cache_duration": 5000
    }
    
    # 自动化配置
    AUTOMATION = {
        "default_delay": 0.1,
        "random_factor": 0.1,
        "retry_count": 3,
        "timeout": 30,
        "mouse_speed": 0.5,
        "mouse_offset": 5,
        "click_delay": 0.1
    }
    
    # 日志配置
    LOGGING = {
        "level": "INFO",
        "file": "logs/application.log",
        "max_size": "10MB",
        "backup_count": 5,
        "enable_console": True,
        "enable_file": True,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
    
    # 性能配置
    PERFORMANCE = {
        "max_memory_usage": "512MB",
        "cpu_limit": 80,
        "gpu_acceleration": True,
        "display_fps": 30,
        "update_interval": 33
    }


class Config:
    """
    统一配置管理器 - 基于PyQt6 QSettings
    支持两种模式：
    1. QSettings模式（推荐）- 使用系统原生配置存储
    2. JSON文件模式（备用）- 当PyQt6不可用时
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置管理器"""
        if Config._initialized:
            return
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self._use_qsettings = PYQT6_AVAILABLE
        # 支持多个可能的配置文件路径
        self._config_file = self._find_config_file()
        self._qsettings = None
        self._json_config = {}
        
        # 初始化
        self._init_storage()
        self._ensure_directories()
        Config._initialized = True
    
    def _find_config_file(self) -> str:
        """查找配置文件的正确路径"""
        possible_paths = [
            "config/config.json",  # 新的组织结构
            "config.json",         # 原始位置
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"找到配置文件: {path}")
                return path
        
        # 如果都不存在，使用新的默认路径
        default_path = "config/config.json"
        self.logger.info(f"使用默认配置文件路径: {default_path}")
        return default_path
    
    def _init_storage(self):
        """初始化存储系统"""
        if self._use_qsettings:
            try:
                # 确保应用元数据已设置
                if not QCoreApplication.organizationName():
                    init_application_metadata()
                
                # 创建QSettings实例，使用应用元数据
                self._qsettings = QSettings()
                
                # 验证QSettings可用性
                test_key = "system/qsettings_test"
                self._qsettings.setValue(test_key, "test")
                if self._qsettings.value(test_key) == "test":
                    self._qsettings.remove(test_key)
                    self.logger.info("QSettings初始化成功")
                    self._migrate_from_json_if_needed()
                else:
                    raise RuntimeError("QSettings功能测试失败")
                    
            except Exception as e:
                self.logger.warning(f"QSettings初始化失败，降级到JSON模式: {e}")
                self._use_qsettings = False
                self._qsettings = None
        
        if not self._use_qsettings:
            self._load_json_config()
    
    def _migrate_from_json_if_needed(self):
        """如果需要，从JSON配置迁移到QSettings"""
        if not os.path.exists(self._config_file):
            return
        
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                json_config = json.load(f)
            
            # 检查QSettings是否为空（首次运行）
            if not self._qsettings.childGroups():
                self.logger.info("检测到JSON配置文件，开始迁移到QSettings...")
                self._import_json_to_qsettings(json_config)
                
                # 备份原JSON文件
                backup_file = f"{self._config_file}.backup"
                os.rename(self._config_file, backup_file)
                self.logger.info(f"JSON配置已迁移，原文件备份为: {backup_file}")
                
        except Exception as e:
            self.logger.error(f"配置迁移失败: {e}")
    
    def _import_json_to_qsettings(self, json_config: dict):
        """将JSON配置导入到QSettings"""
        def import_recursive(data: dict, prefix: str = ""):
            for key, value in data.items():
                full_key = f"{prefix}/{key}" if prefix else key
                
                if isinstance(value, dict):
                    # 递归处理嵌套字典
                    import_recursive(value, full_key)
                else:
                    # 设置值
                    self._qsettings.setValue(full_key, value)
        
        import_recursive(json_config)
        self._qsettings.sync()
    
    def _load_json_config(self):
        """加载JSON配置（备用模式）"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._json_config = json.load(f)
                self.logger.info("JSON配置加载成功")
            else:
                self._json_config = self._create_default_config()
                self._save_json_config()
                self.logger.info("创建默认JSON配置")
        except Exception as e:
            self.logger.error(f"JSON配置加载失败: {e}")
            self._json_config = self._create_default_config()
    
    def _save_json_config(self):
        """保存JSON配置"""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._json_config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"JSON配置保存失败: {e}")
    
    def _create_default_config(self) -> dict:
        """创建默认配置"""
        return {
            "application": ConfigDefaults.APPLICATION.copy(),
            "hotkeys": ConfigDefaults.HOTKEYS.copy(),
            "playback_options": ConfigDefaults.PLAYBACK_OPTIONS.copy(),
            "window": ConfigDefaults.WINDOW.copy(),
            "template": ConfigDefaults.TEMPLATE.copy(),
            "game_state": ConfigDefaults.GAME_STATE.copy(),
            "automation": ConfigDefaults.AUTOMATION.copy(),
            "logging": ConfigDefaults.LOGGING.copy(),
            "performance": ConfigDefaults.PERFORMANCE.copy()
        }
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            "config",
            "logs",
            "templates", 
            "screenshots",
            "models",
            "data"
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                self.logger.warning(f"创建目录失败 {directory}: {e}")
    
    # === 核心配置访问方法 ===
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持分层访问（如 'application/name'）
            default: 默认值
            
        Returns:
            配置值
        """
        if self._use_qsettings:
            return self._qsettings.value(key, default)
        else:
            # JSON模式下的分层访问
            keys = key.split('/')
            value = self._json_config
            
            try:
                for k in keys:
                    value = value[k]
                return value
            except (KeyError, TypeError):
                return default
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        if self._use_qsettings:
            self._qsettings.setValue(key, value)
            self._qsettings.sync()
        else:
            # JSON模式下的分层设置
            keys = key.split('/')
            config = self._json_config
            
            # 导航到父级
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            self._save_json_config()
    
    def remove(self, key: str):
        """删除配置项"""
        if self._use_qsettings:
            self._qsettings.remove(key)
            self._qsettings.sync()
        else:
            keys = key.split('/')
            config = self._json_config
            
            try:
                # 导航到父级
                for k in keys[:-1]:
                    config = config[k]
                
                # 删除键
                if keys[-1] in config:
                    del config[keys[-1]]
                    self._save_json_config()
            except (KeyError, TypeError):
                pass
    
    def clear(self):
        """清空所有配置"""
        if self._use_qsettings:
            self._qsettings.clear()
            self._qsettings.sync()
        else:
            self._json_config = self._create_default_config()
            self._save_json_config()
    
    # === 分组配置访问方法 ===
    
    def get_application_config(self) -> dict:
        """获取应用程序配置"""
        return self._get_section("application", ConfigDefaults.APPLICATION)
    
    def get_hotkeys(self) -> dict:
        """获取热键配置"""
        return self._get_section("hotkeys", ConfigDefaults.HOTKEYS)
    
    def get_playback_options(self) -> dict:
        """获取播放选项"""
        return self._get_section("playback_options", ConfigDefaults.PLAYBACK_OPTIONS)
    
    def get_window_config(self) -> dict:
        """获取窗口配置"""
        return self._get_section("window", ConfigDefaults.WINDOW)
    
    def get_template_config(self) -> dict:
        """获取模板配置"""
        return self._get_section("template", ConfigDefaults.TEMPLATE)
    
    def get_game_state_config(self) -> dict:
        """获取游戏状态配置"""
        return self._get_section("game_state", ConfigDefaults.GAME_STATE)
    
    def get_automation_config(self) -> dict:
        """获取自动化配置"""
        return self._get_section("automation", ConfigDefaults.AUTOMATION)
    
    def get_logging_config(self) -> dict:
        """获取日志配置"""
        return self._get_section("logging", ConfigDefaults.LOGGING)
    
    def get_performance_config(self) -> dict:
        """获取性能配置"""
        return self._get_section("performance", ConfigDefaults.PERFORMANCE)
    
    def _get_section(self, section: str, defaults: dict) -> dict:
        """获取配置分组"""
        if self._use_qsettings:
            result = {}
            self._qsettings.beginGroup(section)
            for key in defaults.keys():
                result[key] = self._qsettings.value(key, defaults[key])
            self._qsettings.endGroup()
            return result
        else:
            return self._json_config.get(section, defaults.copy())
    
    # === 兼容性方法 ===
    
    def get_config(self, key: str, default=None):
        """兼容旧版接口"""
        return self.get(key, default)
    
    def set_config(self, key: str, value):
        """兼容旧版接口"""
        self.set(key, value)
    
    def delete_config(self, key: str):
        """兼容旧版接口"""
        self.remove(key)
    
    def clear_config(self):
        """兼容旧版接口"""
        self.clear()
    
    # === 实用方法 ===
    
    def get_storage_info(self) -> dict:
        """获取存储信息"""
        info = {
            "mode": "QSettings" if self._use_qsettings else "JSON",
            "pyqt6_available": PYQT6_AVAILABLE
        }
        
        if self._use_qsettings:
            info.update({
                "organization": QCoreApplication.organizationName(),
                "application": QCoreApplication.applicationName(),
                "settings_path": self._qsettings.fileName() if hasattr(self._qsettings, 'fileName') else "系统存储"
            })
        else:
            info.update({
                "config_file": os.path.abspath(self._config_file),
                "file_exists": os.path.exists(self._config_file)
            })
        
        return info
    
    def export_to_json(self, file_path: str) -> bool:
        """导出配置到JSON文件"""
        try:
            config_data = {}
            
            if self._use_qsettings:
                # 从QSettings读取所有配置
                def read_recursive(group_prefix: str = ""):
                    if group_prefix:
                        self._qsettings.beginGroup(group_prefix)
                    
                    result = {}
                    
                    # 读取当前组的所有键
                    for key in self._qsettings.childKeys():
                        result[key] = self._qsettings.value(key)
                    
                    # 递归读取子组
                    for group in self._qsettings.childGroups():
                        if group_prefix:
                            self._qsettings.endGroup()
                            full_group = f"{group_prefix}/{group}"
                        else:
                            full_group = group
                        
                        result[group] = read_recursive(full_group)
                        
                        if group_prefix:
                            self._qsettings.beginGroup(group_prefix)
                    
                    if group_prefix:
                        self._qsettings.endGroup()
                    
                    return result
                
                config_data = read_recursive()
            else:
                config_data = self._json_config.copy()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"配置已导出到: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"配置导出失败: {e}")
            return False
    
    def import_from_json(self, file_path: str) -> bool:
        """从JSON文件导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if self._use_qsettings:
                self._import_json_to_qsettings(config_data)
            else:
                self._json_config = config_data
                self._save_json_config()
            
            self.logger.info(f"配置已从 {file_path} 导入")
            return True
            
        except Exception as e:
            self.logger.error(f"配置导入失败: {e}")
            return False


# 创建全局配置实例
config = Config()


# === 便捷访问函数 ===

def get_config(key: str, default=None):
    """便捷的配置获取函数"""
    return config.get(key, default)


def set_config(key: str, value):
    """便捷的配置设置函数"""
    config.set(key, value)


# 导出
__all__ = ['Config', 'config', 'get_config', 'set_config', 'ConfigDefaults']