"""统一窗口管理器工厂

这个模块提供了创建和配置窗口管理器的工厂类。
"""

import logging
import platform
from typing import Dict, Any, List, Optional

from ...core.interfaces.window_manager import IWindowManager, IWindowManagerFactory, WindowManagerError
from .unified_window_manager import UnifiedWindowManager, WindowManagerConfig


class WindowManagerFactory(IWindowManagerFactory):
    """窗口管理器工厂实现"""
    
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._supported_platforms = ['Windows']
        self._instances: Dict[str, IWindowManager] = {}
    
    def create_window_manager(self, config: Dict[str, Any] = None) -> IWindowManager:
        """创建窗口管理器实例"""
        try:
            # 检查平台支持
            current_platform = platform.system()
            if not self.is_platform_supported(current_platform):
                raise WindowManagerError(f"Platform {current_platform} is not supported")
            
            # 解析配置
            manager_config = self._parse_config(config or {})
            
            # 创建实例
            instance_key = self._generate_instance_key(manager_config)
            
            if instance_key in self._instances:
                self._logger.info(f"Reusing existing window manager instance: {instance_key}")
                return self._instances[instance_key]
            
            # 创建新实例
            manager = UnifiedWindowManager(manager_config)
            self._instances[instance_key] = manager
            
            self._logger.info(f"Created new window manager instance: {instance_key}")
            return manager
            
        except Exception as e:
            self._logger.error(f"Failed to create window manager: {e}")
            raise WindowManagerError(f"Failed to create window manager: {e}")
    
    def get_supported_platforms(self) -> List[str]:
        """获取支持的平台列表"""
        return self._supported_platforms.copy()
    
    def is_platform_supported(self, platform_name: str) -> bool:
        """检查平台是否支持"""
        return platform_name in self._supported_platforms
    
    def _parse_config(self, config: Dict[str, Any]) -> WindowManagerConfig:
        """解析配置参数"""
        try:
            return WindowManagerConfig(
                enable_monitoring=config.get('enable_monitoring', True),
                cache_timeout=config.get('cache_timeout', 1.0),
                max_cache_size=config.get('max_cache_size', 1000),
                auto_refresh_interval=config.get('auto_refresh_interval', 5.0),
                enable_auto_refresh=config.get('enable_auto_refresh', False),
                log_level=config.get('log_level', 'INFO'),
                capture_engine=config.get('capture_engine', 'auto')
            )
        except Exception as e:
            self._logger.error(f"Failed to parse config: {e}")
            raise WindowManagerError(f"Invalid configuration: {e}")
    
    def _generate_instance_key(self, config: WindowManagerConfig) -> str:
        """生成实例键"""
        # 基于配置生成唯一键
        key_parts = [
            f"monitoring_{config.enable_monitoring}",
            f"cache_{config.cache_timeout}",
            f"engine_{config.capture_engine}"
        ]
        return "_".join(key_parts)
    
    def get_instance(self, instance_key: str) -> Optional[IWindowManager]:
        """获取已存在的实例"""
        return self._instances.get(instance_key)
    
    def list_instances(self) -> List[str]:
        """列出所有实例键"""
        return list(self._instances.keys())
    
    def shutdown_instance(self, instance_key: str) -> bool:
        """关闭指定实例"""
        if instance_key in self._instances:
            try:
                self._instances[instance_key].shutdown()
                del self._instances[instance_key]
                self._logger.info(f"Shutdown instance: {instance_key}")
                return True
            except Exception as e:
                self._logger.error(f"Failed to shutdown instance {instance_key}: {e}")
                return False
        return False
    
    def shutdown_all_instances(self) -> None:
        """关闭所有实例"""
        for instance_key in list(self._instances.keys()):
            self.shutdown_instance(instance_key)
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'enable_monitoring': True,
            'cache_timeout': 1.0,
            'max_cache_size': 1000,
            'auto_refresh_interval': 5.0,
            'enable_auto_refresh': False,
            'log_level': 'INFO',
            'capture_engine': 'auto'
        }
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """验证配置参数"""
        errors = []
        
        # 检查必需的参数类型
        type_checks = {
            'enable_monitoring': bool,
            'cache_timeout': (int, float),
            'max_cache_size': int,
            'auto_refresh_interval': (int, float),
            'enable_auto_refresh': bool,
            'log_level': str,
            'capture_engine': str
        }
        
        for key, expected_type in type_checks.items():
            if key in config:
                if not isinstance(config[key], expected_type):
                    errors.append(f"'{key}' must be of type {expected_type.__name__}")
        
        # 检查数值范围
        if 'cache_timeout' in config and config['cache_timeout'] <= 0:
            errors.append("'cache_timeout' must be positive")
        
        if 'max_cache_size' in config and config['max_cache_size'] <= 0:
            errors.append("'max_cache_size' must be positive")
        
        if 'auto_refresh_interval' in config and config['auto_refresh_interval'] <= 0:
            errors.append("'auto_refresh_interval' must be positive")
        
        # 检查枚举值
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if 'log_level' in config and config['log_level'] not in valid_log_levels:
            errors.append(f"'log_level' must be one of {valid_log_levels}")
        
        valid_engines = ['auto', 'gdi', 'dxgi']
        if 'capture_engine' in config and config['capture_engine'] not in valid_engines:
            errors.append(f"'capture_engine' must be one of {valid_engines}")
        
        return errors


# 全局工厂实例
_factory_instance: Optional[WindowManagerFactory] = None


def get_window_manager_factory() -> WindowManagerFactory:
    """获取全局窗口管理器工厂实例"""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = WindowManagerFactory()
    return _factory_instance


def create_window_manager(config: Dict[str, Any] = None) -> IWindowManager:
    """便捷函数：创建窗口管理器"""
    factory = get_window_manager_factory()
    return factory.create_window_manager(config)


def get_default_window_manager() -> IWindowManager:
    """便捷函数：获取默认配置的窗口管理器"""
    return create_window_manager()


def shutdown_all_window_managers() -> None:
    """便捷函数：关闭所有窗口管理器实例"""
    global _factory_instance
    if _factory_instance:
        _factory_instance.shutdown_all_instances()
        _factory_instance = None