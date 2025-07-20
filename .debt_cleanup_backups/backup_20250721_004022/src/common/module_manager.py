"""智能模块管理器

提供统一的模块管理、导入解析和别名映射功能。
"""

import json
import logging
import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta

from .module_types import (
    ModuleInfo, ModuleStatus, ModuleCache, ModuleManagerConfig,
    ImportRequest
)
from .module_discovery import ModuleDiscovery


class ModuleManager:
    """智能模块管理器
    
    负责模块的发现、加载、别名管理和依赖解析。
    提供统一的模块访问接口，支持懒加载和缓存机制。
    """
    
    _instance: Optional['ModuleManager'] = None
    _initialized: bool = False
    
    def __new__(cls, config_path: Optional[str] = None) -> 'ModuleManager':
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化模块管理器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if self._initialized:
            return
        
        self.config_path = config_path or "config/module_config.json"
        self.config: Optional[ModuleManagerConfig] = None
        self.cache = ModuleCache()
        self.discovery: Optional[ModuleDiscovery] = None
        self.logger = logging.getLogger(__name__)
        
        # 性能统计
        self._import_requests: List[ImportRequest] = []
        self._load_times: Dict[str, float] = {}
        
        # 初始化状态
        self._is_initialized = False
        
        self._initialized = True
    
    def initialize(self) -> None:
        """初始化模块管理器
        
        加载配置、初始化发现器、扫描模块并设置别名。
        """
        if self._is_initialized:
            self.logger.warning("模块管理器已经初始化")
            return
        
        try:
            # 加载配置
            self._load_config()
            
            # 设置日志
            self._setup_logging()
            
            # 初始化模块发现器
            self.discovery = ModuleDiscovery(self.config)
            
            # 执行模块发现
            if self.config.auto_discovery:
                self._discover_all_modules()
            
            # 注册配置中的别名
            self._register_config_aliases()
            
            # 预加载指定模块
            if self.config.preload_modules:
                self._preload_modules()
            
            self._is_initialized = True
            self.logger.info("模块管理器初始化完成")
            
        except Exception as e:
            self.logger.error(f"模块管理器初始化失败: {e}")
            raise
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            config_file = Path(self.config_path)
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self.config = ModuleManagerConfig.from_dict(config_data)
                self.logger.info(f"配置文件加载成功: {self.config_path}")
            else:
                self.logger.warning(f"配置文件不存在，使用默认配置: {self.config_path}")
                self.config = ModuleManagerConfig()
                
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            self.config = ModuleManagerConfig()
    
    def _setup_logging(self) -> None:
        """设置日志记录"""
        log_level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        
        # 如果没有处理器，添加一个控制台处理器
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _discover_all_modules(self) -> None:
        """发现所有模块"""
        self.logger.info("开始模块发现")
        
        all_modules = []
        
        # 扫描所有配置的路径
        for scan_path in self.config.scan_paths:
            if Path(scan_path).exists():
                modules = self.discovery.scan_directory(scan_path)
                all_modules.extend(modules)
            else:
                self.logger.warning(f"扫描路径不存在: {scan_path}")
        
        # 构建依赖关系图
        if all_modules:
            dependency_graph = self.discovery.build_dependency_graph(all_modules)
            self.cache.dependency_graph = {k: set(v) for k, v in dependency_graph.items()}
        
        # 添加到缓存
        for module in all_modules:
            self.cache.add_module(module)
        
        self.cache.last_scan_time = datetime.now()
        self.logger.info(f"模块发现完成，共发现 {len(all_modules)} 个模块")
    
    def _register_config_aliases(self) -> None:
        """注册配置文件中的别名"""
        for alias, target in self.config.aliases.items():
            self.register_alias(alias, target)
        
        self.logger.info(f"注册了 {len(self.config.aliases)} 个配置别名")
    
    def _preload_modules(self) -> None:
        """预加载指定模块"""
        self.logger.info("开始预加载模块")
        
        for module_path in self.config.preload_modules:
            try:
                self.load_module(module_path)
                self.logger.debug(f"预加载模块成功: {module_path}")
            except Exception as e:
                self.logger.error(f"预加载模块失败 {module_path}: {e}")
        
        self.logger.info("模块预加载完成")
    
    def discover_modules(self) -> Dict[str, ModuleInfo]:
        """手动触发模块发现
        
        Returns:
            发现的模块信息字典
        """
        if not self.discovery:
            raise RuntimeError("模块管理器未初始化")
        
        self._discover_all_modules()
        return self.cache.modules.copy()
    
    def register_alias(self, alias: str, module_path: str) -> None:
        """注册模块别名
        
        Args:
            alias: 别名
            module_path: 目标模块路径
        """
        self.cache.aliases[alias] = module_path
        
        # 如果模块已存在，添加别名到模块信息
        module_info = self.cache.get_module(module_path)
        if module_info:
            module_info.add_alias(alias)
        
        self.logger.debug(f"注册别名: {alias} -> {module_path}")
    
    def get_module(self, identifier: str) -> Any:
        """获取模块对象
        
        Args:
            identifier: 模块标识符（路径或别名）
            
        Returns:
            模块对象
            
        Raises:
            ImportError: 模块不存在或加载失败
        """
        start_time = datetime.now()
        
        try:
            # 记录导入请求
            request = ImportRequest(
                identifier=identifier,
                requester=self._get_caller_module()
            )
            
            # 解析标识符到实际路径
            module_path = self._resolve_identifier(identifier)
            if not module_path:
                raise ImportError(f"无法解析模块标识符: {identifier}")
            
            request.resolved_path = module_path
            
            # 获取模块信息
            module_info = self.cache.get_module(module_path)
            
            # 如果模块已加载，直接返回
            if module_info and module_info.is_loaded():
                request.success = True
                return module_info.module_object
            
            # 加载模块
            module_obj = self.load_module(module_path)
            request.success = True
            
            return module_obj
            
        except Exception as e:
            request.error_message = str(e)
            self.logger.error(f"获取模块失败 {identifier}: {e}")
            raise
        
        finally:
            # 记录性能数据
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            request.load_time_ms = load_time
            
            if self.config.log_imports:
                self._import_requests.append(request)
    
    def load_module(self, module_path: str) -> Any:
        """加载指定模块
        
        Args:
            module_path: 模块路径
            
        Returns:
            加载的模块对象
            
        Raises:
            ImportError: 模块加载失败
        """
        start_time = datetime.now()
        
        try:
            # 获取或创建模块信息
            module_info = self.cache.get_module(module_path)
            if not module_info:
                # 如果缓存中没有，尝试创建基本信息
                module_info = ModuleInfo(
                    name=module_path,
                    path=module_path,
                    full_path=module_path
                )
                self.cache.add_module(module_info)
            
            # 如果已加载，直接返回
            if module_info.is_loaded():
                return module_info.module_object
            
            # 更新状态为加载中
            module_info.status = ModuleStatus.LOADING
            
            # 执行实际加载
            module_obj = importlib.import_module(module_path)
            
            # 更新模块信息
            module_info.module_object = module_obj
            module_info.status = ModuleStatus.LOADED
            module_info.load_time = datetime.now()
            
            # 记录加载时间
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            self._load_times[module_path] = load_time
            
            self.logger.debug(f"模块加载成功: {module_path} ({load_time:.2f}ms)")
            return module_obj
            
        except Exception as e:
            # 更新失败状态
            if module_info:
                module_info.status = ModuleStatus.FAILED
                module_info.error_message = str(e)
            
            self.logger.error(f"模块加载失败 {module_path}: {e}")
            raise ImportError(f"无法加载模块 {module_path}: {e}")
    
    def reload_module(self, identifier: str) -> Any:
        """重新加载模块
        
        Args:
            identifier: 模块标识符
            
        Returns:
            重新加载的模块对象
        """
        # 解析标识符
        module_path = self._resolve_identifier(identifier)
        if not module_path:
            raise ImportError(f"无法解析模块标识符: {identifier}")
        
        # 获取模块信息
        module_info = self.cache.get_module(module_path)
        
        try:
            # 如果模块已在sys.modules中，重新加载
            if module_path in sys.modules:
                module_obj = importlib.reload(sys.modules[module_path])
            else:
                module_obj = self.load_module(module_path)
            
            # 更新模块信息
            if module_info:
                module_info.module_object = module_obj
                module_info.status = ModuleStatus.LOADED
                module_info.load_time = datetime.now()
                module_info.error_message = None
            
            self.logger.info(f"模块重新加载成功: {module_path}")
            return module_obj
            
        except Exception as e:
            if module_info:
                module_info.status = ModuleStatus.FAILED
                module_info.error_message = str(e)
            
            self.logger.error(f"模块重新加载失败 {module_path}: {e}")
            raise
    
    def get_module_info(self, identifier: str) -> Optional[ModuleInfo]:
        """获取模块信息
        
        Args:
            identifier: 模块标识符
            
        Returns:
            模块信息对象，如果不存在则返回None
        """
        module_path = self._resolve_identifier(identifier)
        if module_path:
            return self.cache.get_module(module_path)
        return None
    
    def _resolve_identifier(self, identifier: str) -> Optional[str]:
        """解析模块标识符到实际路径
        
        Args:
            identifier: 模块标识符
            
        Returns:
            解析后的模块路径
        """
        # 直接查找
        if identifier in self.cache.modules:
            return identifier
        
        # 通过别名查找
        if identifier in self.cache.aliases:
            return self.cache.aliases[identifier]
        
        # 模糊匹配
        for module_path in self.cache.modules:
            if module_path.endswith(identifier) or identifier in module_path:
                return module_path
        
        # 如果都找不到，返回原标识符（可能是有效的Python模块路径）
        return identifier
    
    def _get_caller_module(self) -> str:
        """获取调用者模块名
        
        Returns:
            调用者模块名
        """
        import inspect
        
        frame = inspect.currentframe()
        try:
            # 向上查找调用栈，跳过当前模块的帧
            while frame:
                frame = frame.f_back
                if frame and frame.f_globals.get('__name__') != __name__:
                    return frame.f_globals.get('__name__', 'unknown')
            return 'unknown'
        finally:
            del frame
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取性能统计信息
        
        Returns:
            统计信息字典
        """
        total_modules = len(self.cache.modules)
        loaded_modules = sum(1 for m in self.cache.modules.values() if m.is_loaded())
        failed_modules = sum(1 for m in self.cache.modules.values() if m.is_failed())
        
        avg_load_time = 0
        if self._load_times:
            avg_load_time = sum(self._load_times.values()) / len(self._load_times)
        
        return {
            'total_modules': total_modules,
            'loaded_modules': loaded_modules,
            'failed_modules': failed_modules,
            'total_aliases': len(self.cache.aliases),
            'import_requests': len(self._import_requests),
            'average_load_time_ms': round(avg_load_time, 2),
            'cache_last_scan': self.cache.last_scan_time.isoformat() if self.cache.last_scan_time else None
        }
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self._import_requests.clear()
        self._load_times.clear()
        
        if self.discovery:
            self.discovery.clear_cache()
        
        self.logger.info("模块管理器缓存已清空")
    
    def is_initialized(self) -> bool:
        """检查是否已初始化
        
        Returns:
            是否已初始化
        """
        return self._is_initialized


# 全局模块管理器实例
_global_manager: Optional[ModuleManager] = None


def get_module_manager() -> ModuleManager:
    """获取全局模块管理器实例
    
    Returns:
        模块管理器实例
    """
    global _global_manager
    
    if _global_manager is None:
        _global_manager = ModuleManager()
        
    return _global_manager


def initialize_module_manager(config_path: Optional[str] = None) -> ModuleManager:
    """初始化全局模块管理器
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        初始化后的模块管理器实例
    """
    global _global_manager
    
    _global_manager = ModuleManager(config_path)
    _global_manager.initialize()
    
    return _global_manager


# 便捷函数
def get_module(identifier: str) -> Any:
    """便捷函数：获取模块
    
    Args:
        identifier: 模块标识符
        
    Returns:
        模块对象
    """
    return get_module_manager().get_module(identifier)


def register_alias(alias: str, module_path: str) -> None:
    """便捷函数：注册别名
    
    Args:
        alias: 别名
        module_path: 模块路径
    """
    get_module_manager().register_alias(alias, module_path)