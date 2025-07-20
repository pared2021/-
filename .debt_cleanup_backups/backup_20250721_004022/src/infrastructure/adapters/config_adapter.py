"""配置服务适配器

这个模块提供了配置服务的适配器实现，将现有的配置系统包装为符合IConfigService接口的服务。
使用适配器模式来保持向后兼容性，同时支持新的依赖注入架构。
"""

from typing import Any, Dict, Optional, Union
from pathlib import Path

from ...core.interfaces.services import IConfigService


class ConfigServiceAdapter(IConfigService):
    """配置服务适配器
    
    将现有的配置系统适配为IConfigService接口。
    这样可以在不修改现有配置代码的情况下，使其符合新的架构。
    """
    
    def __init__(self):
        self._config_instance = None
        self._is_initialized = False
    
    def _ensure_config_loaded(self) -> None:
        """确保配置已加载"""
        if not self._is_initialized:
            try:
                # 导入现有的配置系统
                from ...common.config import config
                self._config_instance = config
                self._is_initialized = True
            except ImportError as e:
                raise RuntimeError(f"无法导入现有配置系统: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        self._ensure_config_loaded()
        
        if self._config_instance is None:
            return default
        
        # 支持点分隔的键路径，如 'database.host'
        keys = key.split('.')
        value = self._config_instance
        
        try:
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                elif hasattr(value, 'get') and callable(getattr(value, 'get')):
                    value = value.get(k)
                elif isinstance(value, dict):
                    value = value[k]
                else:
                    return default
            return value
        except (KeyError, AttributeError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self._ensure_config_loaded()
        
        if self._config_instance is None:
            raise RuntimeError("配置系统未初始化")
        
        # 支持点分隔的键路径设置
        keys = key.split('.')
        target = self._config_instance
        
        # 导航到目标位置
        for k in keys[:-1]:
            if hasattr(target, k):
                target = getattr(target, k)
            elif isinstance(target, dict):
                if k not in target:
                    target[k] = {}
                target = target[k]
            else:
                raise ValueError(f"无法设置配置路径: {key}")
        
        # 设置最终值
        final_key = keys[-1]
        if hasattr(target, final_key):
            setattr(target, final_key, value)
        elif isinstance(target, dict):
            target[final_key] = value
        else:
            raise ValueError(f"无法设置配置键: {final_key}")
    
    def has(self, key: str) -> bool:
        """检查配置键是否存在"""
        self._ensure_config_loaded()
        
        if self._config_instance is None:
            return False
        
        keys = key.split('.')
        value = self._config_instance
        
        try:
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                elif hasattr(value, 'get') and callable(getattr(value, 'get')):
                    if k not in value:
                        return False
                    value = value.get(k)
                elif isinstance(value, dict):
                    if k not in value:
                        return False
                    value = value[k]
                else:
                    return False
            return True
        except (KeyError, AttributeError, TypeError):
            return False
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """获取配置段"""
        self._ensure_config_loaded()
        
        section_data = self.get(section, {})
        
        if isinstance(section_data, dict):
            return section_data
        elif hasattr(section_data, '__dict__'):
            # 如果是对象，转换为字典
            return {k: v for k, v in section_data.__dict__.items() 
                   if not k.startswith('_')}
        else:
            return {}
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """批量更新配置"""
        for key, value in config_dict.items():
            self.set(key, value)
    
    def reload(self) -> None:
        """重新加载配置"""
        self._is_initialized = False
        self._config_instance = None
        self._ensure_config_loaded()
    
    def get_config_path(self) -> Optional[Path]:
        """获取配置文件路径"""
        self._ensure_config_loaded()
        
        if self._config_instance and hasattr(self._config_instance, 'config_file'):
            config_file = getattr(self._config_instance, 'config_file')
            if config_file:
                return Path(config_file)
        
        # 尝试从常见位置推断配置文件路径
        possible_paths = [
            Path('config.json'),
            Path('config.yaml'),
            Path('config.yml'),
            Path('settings.json'),
            Path('src/config.json'),
            Path('src/config.yaml')
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def save(self, path: Optional[Union[str, Path]] = None) -> None:
        """保存配置到文件"""
        self._ensure_config_loaded()
        
        if self._config_instance is None:
            raise RuntimeError("配置系统未初始化")
        
        # 如果现有配置系统有保存方法，使用它
        if hasattr(self._config_instance, 'save'):
            if path:
                self._config_instance.save(str(path))
            else:
                self._config_instance.save()
            return
        
        # 否则尝试手动保存
        import json
        
        save_path = path or self.get_config_path()
        if save_path is None:
            raise ValueError("无法确定配置文件保存路径")
        
        save_path = Path(save_path)
        
        # 将配置对象转换为字典
        if hasattr(self._config_instance, '__dict__'):
            config_data = {k: v for k, v in self._config_instance.__dict__.items() 
                          if not k.startswith('_')}
        else:
            config_data = dict(self._config_instance)
        
        # 保存为JSON格式
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        self._ensure_config_loaded()
        
        if self._config_instance is None:
            return {}
        
        if hasattr(self._config_instance, '__dict__'):
            return {k: v for k, v in self._config_instance.__dict__.items() 
                   if not k.startswith('_')}
        elif isinstance(self._config_instance, dict):
            return dict(self._config_instance)
        else:
            return {}
    
    def clear(self) -> None:
        """清空配置"""
        self._ensure_config_loaded()
        
        if self._config_instance is None:
            return
        
        if hasattr(self._config_instance, 'clear'):
            self._config_instance.clear()
        elif hasattr(self._config_instance, '__dict__'):
            # 清空对象属性（保留私有属性）
            attrs_to_remove = [k for k in self._config_instance.__dict__.keys() 
                              if not k.startswith('_')]
            for attr in attrs_to_remove:
                delattr(self._config_instance, attr)
    
    def is_loaded(self) -> bool:
        """检查配置是否已加载"""
        return self._is_initialized and self._config_instance is not None