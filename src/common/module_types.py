"""模块管理系统的数据类型定义

此模块定义了智能模块导入系统中使用的核心数据结构。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum


class ModuleStatus(Enum):
    """模块状态枚举"""
    DISCOVERED = "discovered"
    LOADING = "loading"
    LOADED = "loaded"
    FAILED = "failed"
    UNLOADED = "unloaded"


class ModuleType(Enum):
    """模块类型枚举"""
    PACKAGE = "package"
    MODULE = "module"
    SERVICE = "service"
    GAME = "game"
    CORE = "core"
    UTILITY = "utility"
    UNKNOWN = "unknown"


@dataclass
class ModuleInfo:
    """模块信息数据类
    
    包含模块的完整元数据信息，用于模块管理和导入解析。
    """
    name: str
    path: str
    full_path: str
    module_type: ModuleType = ModuleType.UNKNOWN
    aliases: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    status: ModuleStatus = ModuleStatus.DISCOVERED
    load_time: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    module_object: Optional[Any] = None
    file_size: int = 0
    line_count: int = 0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.full_path:
            self.full_path = self.path
        
        # 根据路径推断模块类型
        if self.module_type == ModuleType.UNKNOWN:
            self.module_type = self._infer_module_type()
    
    def _infer_module_type(self) -> ModuleType:
        """根据路径推断模块类型"""
        path_lower = self.path.lower()
        
        if 'service' in path_lower:
            return ModuleType.SERVICE
        elif 'game' in path_lower:
            return ModuleType.GAME
        elif 'core' in path_lower:
            return ModuleType.CORE
        elif 'util' in path_lower or 'tool' in path_lower:
            return ModuleType.UTILITY
        elif self.path.endswith('__init__.py'):
            return ModuleType.PACKAGE
        else:
            return ModuleType.MODULE
    
    def is_loaded(self) -> bool:
        """检查模块是否已加载"""
        return self.status == ModuleStatus.LOADED and self.module_object is not None
    
    def is_failed(self) -> bool:
        """检查模块是否加载失败"""
        return self.status == ModuleStatus.FAILED
    
    def add_alias(self, alias: str) -> None:
        """添加别名"""
        if alias not in self.aliases:
            self.aliases.append(alias)
    
    def remove_alias(self, alias: str) -> None:
        """移除别名"""
        if alias in self.aliases:
            self.aliases.remove(alias)
    
    def add_dependency(self, dependency: str) -> None:
        """添加依赖"""
        if dependency not in self.dependencies:
            self.dependencies.append(dependency)
    
    def add_dependent(self, dependent: str) -> None:
        """添加依赖者"""
        if dependent not in self.dependents:
            self.dependents.append(dependent)


@dataclass
class ImportRequest:
    """导入请求数据类"""
    identifier: str  # 模块标识符（可能是别名或路径）
    requester: str   # 请求者模块路径
    timestamp: datetime = field(default_factory=datetime.now)
    resolved_path: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None
    load_time_ms: float = 0.0


@dataclass
class ModuleCache:
    """模块缓存数据类"""
    modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    aliases: Dict[str, str] = field(default_factory=dict)
    dependency_graph: Dict[str, Set[str]] = field(default_factory=dict)
    last_scan_time: Optional[datetime] = None
    cache_version: str = "1.0"
    
    def get_module(self, identifier: str) -> Optional[ModuleInfo]:
        """获取模块信息"""
        # 直接查找
        if identifier in self.modules:
            return self.modules[identifier]
        
        # 通过别名查找
        if identifier in self.aliases:
            real_path = self.aliases[identifier]
            return self.modules.get(real_path)
        
        return None
    
    def add_module(self, module_info: ModuleInfo) -> None:
        """添加模块"""
        self.modules[module_info.path] = module_info
        
        # 添加别名映射
        for alias in module_info.aliases:
            self.aliases[alias] = module_info.path
    
    def remove_module(self, path: str) -> None:
        """移除模块"""
        if path in self.modules:
            module_info = self.modules[path]
            
            # 移除别名映射
            for alias in module_info.aliases:
                self.aliases.pop(alias, None)
            
            # 移除模块
            del self.modules[path]
            
            # 移除依赖关系
            self.dependency_graph.pop(path, None)
    
    def clear(self) -> None:
        """清空缓存"""
        self.modules.clear()
        self.aliases.clear()
        self.dependency_graph.clear()
        self.last_scan_time = None


@dataclass
class ModuleManagerConfig:
    """模块管理器配置数据类"""
    auto_discovery: bool = True
    lazy_loading: bool = True
    cache_enabled: bool = True
    scan_paths: List[str] = field(default_factory=lambda: ["src"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["__pycache__", "*.pyc", "tests"])
    aliases: Dict[str, str] = field(default_factory=dict)
    preload_modules: List[str] = field(default_factory=list)
    max_cache_size: int = 1000
    cache_ttl_seconds: int = 3600
    enable_profiling: bool = False
    log_level: str = "INFO"
    log_imports: bool = False
    log_discoveries: bool = True
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ModuleManagerConfig':
        """从字典创建配置对象"""
        # 提取module_manager部分
        manager_config = config_dict.get('module_manager', {})
        performance_config = manager_config.get('performance', {})
        logging_config = manager_config.get('logging', {})
        
        return cls(
            auto_discovery=manager_config.get('auto_discovery', True),
            lazy_loading=manager_config.get('lazy_loading', True),
            cache_enabled=manager_config.get('cache_enabled', True),
            scan_paths=manager_config.get('scan_paths', ["src"]),
            exclude_patterns=manager_config.get('exclude_patterns', ["__pycache__", "*.pyc", "tests"]),
            aliases=manager_config.get('aliases', {}),
            preload_modules=manager_config.get('preload_modules', []),
            max_cache_size=performance_config.get('max_cache_size', 1000),
            cache_ttl_seconds=performance_config.get('cache_ttl_seconds', 3600),
            enable_profiling=performance_config.get('enable_profiling', False),
            log_level=logging_config.get('level', 'INFO'),
            log_imports=logging_config.get('log_imports', False),
            log_discoveries=logging_config.get('log_discoveries', True)
        )