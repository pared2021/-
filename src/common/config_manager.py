import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from enum import Enum
import logging
from threading import Lock

class ConfigType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"

@dataclass
class ConfigItem:
    key: str
    value: Any
    type: ConfigType
    description: str
    default: Any = None
    validators: List[Callable] = field(default_factory=list)
    env_var: Optional[str] = None

class ConfigManager:
    """统一的配置管理类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self._config_items: Dict[str, ConfigItem] = {}
        self._config_lock = Lock()
        self._observers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化默认配置
        self._init_default_config()
        self._load_config()
        
    def _init_default_config(self):
        """初始化默认配置项"""
        default_configs = [
            ConfigItem(
                key="window.refresh_interval",
                value=1000,
                type=ConfigType.INTEGER,
                description="窗口刷新间隔（毫秒）",
                env_var="WINDOW_REFRESH_INTERVAL"
            ),
            ConfigItem(
                key="window.last_selected_window",
                value="",
                type=ConfigType.STRING,
                description="最后选择的窗口标题"
            ),
            ConfigItem(
                key="template.duration",
                value=300,
                type=ConfigType.INTEGER,
                description="默认收集时间（秒）",
                env_var="TEMPLATE_DURATION"
            ),
            ConfigItem(
                key="template.interval",
                value=1.0,
                type=ConfigType.FLOAT,
                description="默认收集间隔（秒）",
                env_var="TEMPLATE_INTERVAL"
            ),
            ConfigItem(
                key="template.last_template_dir",
                value="",
                type=ConfigType.STRING,
                description="最后使用的模板目录"
            ),
            ConfigItem(
                key="model.last_model_dir",
                value="",
                type=ConfigType.STRING,
                description="最后使用的模型目录"
            ),
            ConfigItem(
                key="model.default_epochs",
                value=100,
                type=ConfigType.INTEGER,
                description="默认训练轮数",
                env_var="MODEL_DEFAULT_EPOCHS"
            ),
            ConfigItem(
                key="game_state.analysis_interval",
                value=1000,
                type=ConfigType.INTEGER,
                description="游戏状态分析间隔（毫秒）",
                env_var="GAME_STATE_ANALYSIS_INTERVAL"
            ),
            ConfigItem(
                key="game_state.last_state",
                value={},
                type=ConfigType.DICT,
                description="最后保存的游戏状态"
            )
        ]
        
        for config in default_configs:
            self._config_items[config.key] = config
            
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._merge_config(loaded_config)
                    
            # 检查环境变量覆盖
            self._check_env_vars()
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}")
            
    def _check_env_vars(self):
        """检查环境变量覆盖"""
        for config in self._config_items.values():
            if config.env_var and config.env_var in os.environ:
                env_value = os.environ[config.env_var]
                try:
                    if config.type == ConfigType.INTEGER:
                        env_value = int(env_value)
                    elif config.type == ConfigType.FLOAT:
                        env_value = float(env_value)
                    elif config.type == ConfigType.BOOLEAN:
                        env_value = env_value.lower() in ('true', '1', 'yes')
                    elif config.type == ConfigType.LIST:
                        env_value = json.loads(env_value)
                    elif config.type == ConfigType.DICT:
                        env_value = json.loads(env_value)
                        
                    config.value = env_value
                except Exception as e:
                    self.logger.warning(f"环境变量 {config.env_var} 转换失败: {str(e)}")
                    
    def _merge_config(self, loaded_config: Dict[str, Any]):
        """合并配置"""
        def merge_dict(base: Dict[str, Any], update: Dict[str, Any]):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
                    
        with self._config_lock:
            for key, value in loaded_config.items():
                if key in self._config_items:
                    self._config_items[key].value = value
                    
    def save_config(self):
        """保存配置到文件"""
        try:
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            config_data = {key: item.value for key, item in self._config_items.items()}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {str(e)}")
            
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """获取配置值"""
        try:
            if key_path in self._config_items:
                return self._config_items[key_path].value
            return default
        except Exception as e:
            self.logger.error(f"获取配置值失败: {str(e)}")
            return default
            
    def set_value(self, key_path: str, value: Any):
        """设置配置值"""
        try:
            if key_path not in self._config_items:
                self.logger.warning(f"尝试设置不存在的配置项: {key_path}")
                return
                
            config_item = self._config_items[key_path]
            
            # 类型检查
            if not self._validate_type(value, config_item.type):
                self.logger.error(f"配置值类型不匹配: {key_path}")
                return
                
            # 验证器检查
            for validator in config_item.validators:
                if not validator(value):
                    self.logger.error(f"配置值验证失败: {key_path}")
                    return
                    
            with self._config_lock:
                config_item.value = value
                self.save_config()
                
            # 通知观察者
            self._notify_observers(key_path, value)
        except Exception as e:
            self.logger.error(f"设置配置值失败: {str(e)}")
            
    def _validate_type(self, value: Any, expected_type: ConfigType) -> bool:
        """验证值类型"""
        try:
            if expected_type == ConfigType.INTEGER:
                return isinstance(value, int)
            elif expected_type == ConfigType.FLOAT:
                return isinstance(value, float)
            elif expected_type == ConfigType.BOOLEAN:
                return isinstance(value, bool)
            elif expected_type == ConfigType.STRING:
                return isinstance(value, str)
            elif expected_type == ConfigType.LIST:
                return isinstance(value, list)
            elif expected_type == ConfigType.DICT:
                return isinstance(value, dict)
            return False
        except Exception:
            return False
            
    def add_observer(self, key_path: str, callback: Callable):
        """添加配置变更观察者"""
        if key_path not in self._observers:
            self._observers[key_path] = []
        self._observers[key_path].append(callback)
        
    def remove_observer(self, key_path: str, callback: Callable):
        """移除配置变更观察者"""
        if key_path in self._observers:
            self._observers[key_path].remove(callback)
            
    def _notify_observers(self, key_path: str, new_value: Any):
        """通知观察者配置变更"""
        if key_path in self._observers:
            for callback in self._observers[key_path]:
                try:
                    callback(key_path, new_value)
                except Exception as e:
                    self.logger.error(f"通知观察者失败: {str(e)}")
                    
    def reload_config(self):
        """重新加载配置"""
        self._load_config()
        
    def get_all_configs(self) -> Dict[str, Any]:
        """获取所有配置"""
        return {key: item.value for key, item in self._config_items.items()}

    def get_window_config(self) -> Dict[str, Any]:
        """获取窗口相关配置"""
        return self.config.get('window', {})
        
    def get_template_config(self) -> Dict[str, Any]:
        """获取模板相关配置"""
        return self.config.get('template', {})
        
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型相关配置"""
        return self.config.get('model', {})
        
    def get_game_state_config(self) -> Dict[str, Any]:
        """获取游戏状态相关配置"""
        return self.config.get('game_state', {})
        
    def update_last_selected_window(self, window_title: str):
        """更新最后选择的窗口"""
        self.set_value('window.last_selected_window', window_title)
        
    def update_last_template_dir(self, template_dir: str):
        """更新最后使用的模板目录"""
        self.set_value('template.last_template_dir', template_dir)
        
    def update_last_model_dir(self, model_dir: str):
        """更新最后使用的模型目录"""
        self.set_value('model.last_model_dir', model_dir)
        
    def update_last_game_state(self, state: Dict[str, Any]):
        """更新最后保存的游戏状态"""
        self.set_value('game_state.last_state', state) 