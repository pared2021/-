"""模块发现器

负责扫描项目目录，发现Python模块并构建模块信息。
"""

import os
import ast
import fnmatch
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime

from .module_types import ModuleInfo, ModuleType, ModuleStatus, ModuleManagerConfig


class ModuleDiscovery:
    """模块发现器
    
    扫描指定目录，识别Python模块和包，提取模块信息并构建依赖关系图。
    """
    
    def __init__(self, config: ModuleManagerConfig):
        """初始化模块发现器
        
        Args:
            config: 模块管理器配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # 缓存已扫描的模块
        self._discovered_modules: Dict[str, ModuleInfo] = {}
        self._dependency_cache: Dict[str, Set[str]] = {}
        
    def _setup_logging(self) -> None:
        """设置日志记录"""
        if self.config.log_discoveries:
            self.logger.setLevel(getattr(logging, self.config.log_level.upper(), logging.INFO))
    
    def scan_directory(self, root_path: str) -> List[ModuleInfo]:
        """递归扫描目录，发现所有Python模块
        
        Args:
            root_path: 根目录路径
            
        Returns:
            发现的模块信息列表
        """
        self.logger.info(f"开始扫描目录: {root_path}")
        
        discovered_modules = []
        root_path_obj = Path(root_path)
        
        if not root_path_obj.exists():
            self.logger.warning(f"目录不存在: {root_path}")
            return discovered_modules
        
        # 递归遍历目录
        for current_path in root_path_obj.rglob("*.py"):
            # 检查是否应该排除此文件
            if self._should_exclude(current_path):
                continue
            
            try:
                module_info = self.extract_module_info(str(current_path))
                if module_info:
                    discovered_modules.append(module_info)
                    self._discovered_modules[module_info.path] = module_info
                    
            except Exception as e:
                self.logger.error(f"提取模块信息失败 {current_path}: {e}")
        
        self.logger.info(f"扫描完成，发现 {len(discovered_modules)} 个模块")
        return discovered_modules
    
    def _should_exclude(self, file_path: Path) -> bool:
        """检查文件是否应该被排除
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否应该排除
        """
        file_str = str(file_path)
        
        # 检查排除模式
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(file_str, f"*{pattern}*"):
                return True
        
        # 排除隐藏文件和目录
        for part in file_path.parts:
            if part.startswith('.'):
                return True
        
        return False
    
    def is_python_module(self, file_path: str) -> bool:
        """检查文件是否为Python模块
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否为Python模块
        """
        path_obj = Path(file_path)
        
        # 检查文件扩展名
        if path_obj.suffix != '.py':
            return False
        
        # 检查是否为有效的Python文件
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 尝试解析AST以验证语法
                ast.parse(content)
                return True
        except (SyntaxError, UnicodeDecodeError, FileNotFoundError):
            return False
    
    def extract_module_info(self, file_path: str) -> Optional[ModuleInfo]:
        """从文件路径提取模块信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            模块信息对象，如果提取失败则返回None
        """
        if not self.is_python_module(file_path):
            return None
        
        try:
            path_obj = Path(file_path)
            
            # 计算相对路径和模块名
            relative_path = self._get_relative_path(file_path)
            module_name = self._path_to_module_name(relative_path)
            
            # 获取文件统计信息
            stat_info = path_obj.stat()
            file_size = stat_info.st_size
            last_modified = datetime.fromtimestamp(stat_info.st_mtime)
            
            # 计算行数
            line_count = self._count_lines(file_path)
            
            # 提取依赖关系
            dependencies = self._extract_dependencies(file_path)
            
            # 创建模块信息
            module_info = ModuleInfo(
                name=module_name,
                path=relative_path,
                full_path=file_path,
                dependencies=dependencies,
                status=ModuleStatus.DISCOVERED,
                last_modified=last_modified,
                file_size=file_size,
                line_count=line_count
            )
            
            self.logger.debug(f"提取模块信息: {module_name} ({relative_path})")
            return module_info
            
        except Exception as e:
            self.logger.error(f"提取模块信息失败 {file_path}: {e}")
            return None
    
    def _get_relative_path(self, file_path: str) -> str:
        """获取相对于项目根目录的路径
        
        Args:
            file_path: 绝对文件路径
            
        Returns:
            相对路径
        """
        path_obj = Path(file_path)
        
        # 尝试找到项目根目录
        current_dir = path_obj.parent
        while current_dir.parent != current_dir:
            if (current_dir / 'src').exists() or (current_dir / 'main.py').exists():
                try:
                    return str(path_obj.relative_to(current_dir))
                except ValueError:
                    pass
            current_dir = current_dir.parent
        
        # 如果找不到项目根目录，返回文件名
        return path_obj.name
    
    def _path_to_module_name(self, relative_path: str) -> str:
        """将文件路径转换为模块名
        
        Args:
            relative_path: 相对路径
            
        Returns:
            模块名
        """
        path_obj = Path(relative_path)
        
        # 移除.py扩展名
        if path_obj.suffix == '.py':
            path_obj = path_obj.with_suffix('')
        
        # 将路径分隔符替换为点号
        module_name = str(path_obj).replace(os.sep, '.')
        
        # 处理__init__.py文件
        if module_name.endswith('.__init__'):
            module_name = module_name[:-9]  # 移除.__init__
        
        return module_name
    
    def _count_lines(self, file_path: str) -> int:
        """计算文件行数
        
        Args:
            file_path: 文件路径
            
        Returns:
            行数
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except (FileNotFoundError, UnicodeDecodeError):
            return 0
    
    def _extract_dependencies(self, file_path: str) -> List[str]:
        """提取文件的导入依赖
        
        Args:
            file_path: 文件路径
            
        Returns:
            依赖模块列表
        """
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 遍历AST节点，查找import语句
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module)
            
            # 过滤和清理依赖
            dependencies = self._filter_dependencies(dependencies)
            
        except (SyntaxError, FileNotFoundError, UnicodeDecodeError) as e:
            self.logger.warning(f"提取依赖失败 {file_path}: {e}")
        
        return dependencies
    
    def _filter_dependencies(self, dependencies: List[str]) -> List[str]:
        """过滤和清理依赖列表
        
        Args:
            dependencies: 原始依赖列表
            
        Returns:
            过滤后的依赖列表
        """
        filtered = []
        
        for dep in dependencies:
            # 跳过标准库模块
            if self._is_standard_library(dep):
                continue
            
            # 跳过相对导入
            if dep.startswith('.'):
                continue
            
            # 只保留项目内部模块
            if dep.startswith('src.') or any(dep.startswith(path) for path in self.config.scan_paths):
                filtered.append(dep)
        
        return list(set(filtered))  # 去重
    
    def _is_standard_library(self, module_name: str) -> bool:
        """检查是否为标准库模块
        
        Args:
            module_name: 模块名
            
        Returns:
            是否为标准库模块
        """
        # 常见的标准库模块
        stdlib_modules = {
            'os', 'sys', 'json', 'logging', 'datetime', 'pathlib', 'typing',
            'collections', 'itertools', 'functools', 'operator', 'copy',
            'pickle', 're', 'math', 'random', 'time', 'threading', 'asyncio',
            'unittest', 'pytest', 'dataclasses', 'enum', 'abc', 'contextlib'
        }
        
        # 检查顶级模块名
        top_level = module_name.split('.')[0]
        return top_level in stdlib_modules
    
    def build_dependency_graph(self, modules: List[ModuleInfo]) -> Dict[str, List[str]]:
        """构建模块依赖关系图
        
        Args:
            modules: 模块信息列表
            
        Returns:
            依赖关系图，键为模块路径，值为依赖的模块路径列表
        """
        self.logger.info("构建依赖关系图")
        
        dependency_graph = {}
        module_map = {module.name: module.path for module in modules}
        
        for module in modules:
            resolved_deps = []
            
            for dep in module.dependencies:
                # 尝试解析依赖到实际模块路径
                resolved_path = self._resolve_dependency(dep, module_map)
                if resolved_path:
                    resolved_deps.append(resolved_path)
            
            dependency_graph[module.path] = resolved_deps
            
            # 更新模块的依赖信息
            module.dependencies = resolved_deps
        
        # 构建反向依赖关系（谁依赖了这个模块）
        self._build_reverse_dependencies(modules, dependency_graph)
        
        self.logger.info(f"依赖关系图构建完成，包含 {len(dependency_graph)} 个模块")
        return dependency_graph
    
    def _resolve_dependency(self, dependency: str, module_map: Dict[str, str]) -> Optional[str]:
        """解析依赖到实际模块路径
        
        Args:
            dependency: 依赖模块名
            module_map: 模块名到路径的映射
            
        Returns:
            解析后的模块路径，如果无法解析则返回None
        """
        # 直接匹配
        if dependency in module_map:
            return module_map[dependency]
        
        # 尝试部分匹配
        for module_name, module_path in module_map.items():
            if module_name.endswith(dependency) or dependency.endswith(module_name):
                return module_path
        
        return None
    
    def _build_reverse_dependencies(self, modules: List[ModuleInfo], 
                                   dependency_graph: Dict[str, List[str]]) -> None:
        """构建反向依赖关系
        
        Args:
            modules: 模块信息列表
            dependency_graph: 依赖关系图
        """
        # 创建路径到模块的映射
        path_to_module = {module.path: module for module in modules}
        
        # 构建反向依赖
        for module_path, dependencies in dependency_graph.items():
            for dep_path in dependencies:
                if dep_path in path_to_module:
                    dep_module = path_to_module[dep_path]
                    dep_module.add_dependent(module_path)
    
    def get_discovered_modules(self) -> Dict[str, ModuleInfo]:
        """获取已发现的模块
        
        Returns:
            已发现的模块字典
        """
        return self._discovered_modules.copy()
    
    def clear_cache(self) -> None:
        """清空发现缓存"""
        self._discovered_modules.clear()
        self._dependency_cache.clear()
        self.logger.info("模块发现缓存已清空")