"""
配置仓储实现

基于现有Config类的Clean Architecture实现
提供统一的配置管理接口
"""
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import json
import logging
from ...core.interfaces.repositories import IConfigRepository

# 导入现有的配置管理实现
from ...services.config import Config


class ConfigRepository(IConfigRepository):
    """
    配置仓储实现
    
    封装现有的Config类，提供Clean Architecture接口
    """
    
    def __init__(self):
        self._config_instance = None
        self._initialized = False
        self._logger = logging.getLogger(__name__)
    
    def _ensure_initialized(self) -> bool:
        """确保配置实例已初始化"""
        if not self._initialized:
            try:
                self._config_instance = Config()
                self._initialized = True
            except Exception as e:
                self._logger.error(f"Failed to initialize config: {str(e)}")
                return False
        return True
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        if not self._ensure_initialized():
            return default
        
        try:
            # 支持嵌套键访问 (e.g., "games.genshin.window_title")
            keys = key.split('.')
            value = self._config_instance.get_config(keys[0], default)
            
            # 处理嵌套键
            for nested_key in keys[1:]:
                if isinstance(value, dict) and nested_key in value:
                    value = value[nested_key]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self._logger.error(f"Failed to get config for key '{key}': {str(e)}")
            return default
    
    def set_config(self, key: str, value: Any) -> bool:
        """设置配置值"""
        if not self._ensure_initialized():
            return False
        
        try:
            # 支持嵌套键设置
            keys = key.split('.')
            if len(keys) == 1:
                self._config_instance.set_config(key, value)
            else:
                # 处理嵌套键设置
                self._set_nested_config(keys, value)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to set config for key '{key}': {str(e)}")
            return False
    
    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置"""
        if not self._ensure_initialized():
            return {}
        
        try:
            # 如果Config类有get_all_configs方法，使用它
            if hasattr(self._config_instance, 'get_all_configs'):
                return self._config_instance.get_all_configs()
            else:
                # 否则尝试获取所有已知的配置键
                return self._get_all_configs_fallback()
                
        except Exception as e:
            self._logger.error(f"Failed to get all configs: {str(e)}")
            return {}
    
    def save_configs(self) -> bool:
        """保存配置到持久化存储"""
        if not self._ensure_initialized():
            return False
        
        try:
            if hasattr(self._config_instance, 'save_configs'):
                return self._config_instance.save_configs()
            else:
                # 使用Config类的save方法
                self._config_instance.save()
                return True
                
        except Exception as e:
            self._logger.error(f"Failed to save configs: {str(e)}")
            return False
    
    def load_configs(self) -> bool:
        """从持久化存储加载配置"""
        if not self._ensure_initialized():
            return False
        
        try:
            if hasattr(self._config_instance, 'load_configs'):
                return self._config_instance.load_configs()
            else:
                # 重新创建Config实例来加载配置
                self._config_instance = Config()
                return True
                
        except Exception as e:
            self._logger.error(f"Failed to load configs: {str(e)}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """重置为默认配置"""
        try:
            if hasattr(self._config_instance, 'reset_to_defaults'):
                return self._config_instance.reset_to_defaults()
            else:
                # 简单的重置实现
                self._config_instance = Config()
                return True
                
        except Exception as e:
            self._logger.error(f"Failed to reset to defaults: {str(e)}")
            return False
    
    def backup_configs(self, backup_path: Union[str, Path]) -> bool:
        """备份配置"""
        if not self._ensure_initialized():
            return False
        
        try:
            backup_path = Path(backup_path)
            configs = self.get_all_configs()
            
            # 创建备份目录
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存为JSON文件
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(configs, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to backup configs: {str(e)}")
            return False
    
    def restore_configs(self, backup_path: Union[str, Path]) -> bool:
        """恢复配置"""
        if not self._ensure_initialized():
            return False
        
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                self._logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # 加载备份文件
            with open(backup_path, 'r', encoding='utf-8') as f:
                configs = json.load(f)
            
            # 恢复配置
            for key, value in configs.items():
                self.set_config(key, value)
            
            # 保存配置
            return self.save_configs()
            
        except Exception as e:
            self._logger.error(f"Failed to restore configs: {str(e)}")
            return False
    
    def _set_nested_config(self, keys: List[str], value: Any) -> None:
        """设置嵌套配置值"""
        if len(keys) == 1:
            self._config_instance.set_config(keys[0], value)
            return
        
        # 获取或创建嵌套字典
        root_key = keys[0]
        current_config = self._config_instance.get_config(root_key, {})
        
        # 如果不是字典，创建新的字典
        if not isinstance(current_config, dict):
            current_config = {}
        
        # 设置嵌套值
        nested_config = current_config
        for key in keys[1:-1]:
            if key not in nested_config:
                nested_config[key] = {}
            nested_config = nested_config[key]
        
        nested_config[keys[-1]] = value
        
        # 保存根配置
        self._config_instance.set_config(root_key, current_config)
    
    def _get_all_configs_fallback(self) -> Dict[str, Any]:
        """获取所有配置的备选实现"""
        try:
            # 尝试获取Config实例的所有属性
            configs = {}
            
            # 获取常见的配置键
            common_keys = [
                'game_analyzer', 'automation', 'window_manager', 'input_controller',
                'performance', 'logging', 'ui', 'games', 'templates', 'supported_games'
            ]
            
            for key in common_keys:
                value = self._config_instance.get_config(key)
                if value is not None:
                    configs[key] = value
            
            return configs
            
        except Exception as e:
            self._logger.error(f"Fallback config retrieval failed: {str(e)}")
            return {}
    
    def get_config_instance(self) -> Optional[Config]:
        """获取底层Config实例（用于兼容性）"""
        self._ensure_initialized()
        return self._config_instance