#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能模块导入系统集成测试

测试整个系统的集成功能：
- 端到端的模块发现和加载流程
- 配置驱动的系统行为
- 别名解析和模块导入
- 性能和缓存机制
- 错误恢复和容错性
"""

import unittest
import tempfile
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 导入被测试的模块
from ..src.common.module_manager import ModuleManager, initialize_module_manager, get_module_manager
from ..src.common.module_discovery import ModuleDiscovery
from ..src.common.module_types import ModuleInfo, ModuleType, ModuleStatus


class TestModuleSystemIntegration(unittest.TestCase):
    """智能模块导入系统集成测试"""
    
    def setUp(self):
        """测试前准备"""
        # 重置单例实例
        ModuleManager._instance = None
        ModuleManager._initialized = False
        
        # 创建临时项目结构
        self.temp_project = tempfile.mkdtemp()
        self.create_project_structure()
        
        # 创建配置文件
        self.config_file = Path(self.temp_project) / 'config' / 'module_config.json'
        self.create_config_file()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_project, ignore_errors=True)
        
        # 重置单例
        ModuleManager._instance = None
        ModuleManager._initialized = False
    
    def create_project_structure(self):
        """创建完整的项目结构"""
        project_files = {
            # 主模块
            'src/__init__.py': '',
            'src/main.py': '''
import sys
from pathlib import Path

def main():
    print("Main application")
    return 0

if __name__ == "__main__":
    main()
''',
            
            # UI模块
            'src/ui/__init__.py': '',
            'src/ui/main_window.py': '''
from ..common.logger import get_logger
from ..config.manager import ConfigManager

class MainWindow:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = ConfigManager()
        
    def show(self):
        self.logger.info("Showing main window")
        return "Window shown"
''',
            'src/ui/dialogs.py': '''
from .main_window import MainWindow

class AboutDialog:
    def __init__(self, parent=None):
        self.parent = parent
        
    def exec(self):
        return "About dialog executed"
''',
            
            # 配置模块
            'src/config/__init__.py': '',
            'src/config/manager.py': '''
import json
from pathlib import Path
from ..common.logger import get_logger

class ConfigManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = {}
        
    def load(self, config_path):
        self.logger.info(f"Loading config from {config_path}")
        return True
        
    def get(self, key, default=None):
        return self.config.get(key, default)
''',
            
            # 通用模块
            'src/common/__init__.py': '',
            'src/common/logger.py': '''
import logging

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
''',
            'src/common/utils.py': '''
from pathlib import Path
from .logger import get_logger

def ensure_dir(path):
    """确保目录存在"""
    Path(path).mkdir(parents=True, exist_ok=True)
    return True

def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent.parent
''',
            
            # 游戏模块
            'src/game/__init__.py': '',
            'src/game/automation.py': '''
from ..common.logger import get_logger
from ..common.utils import ensure_dir

class GameAutomation:
    def __init__(self):
        self.logger = get_logger(__name__)
        
    def start(self):
        self.logger.info("Starting game automation")
        return "Automation started"
        
    def stop(self):
        self.logger.info("Stopping game automation")
        return "Automation stopped"
''',
            
            # 测试模块（应该被排除）
            'tests/__init__.py': '',
            'tests/test_example.py': '''
import unittest

class TestExample(unittest.TestCase):
    def test_something(self):
        self.assertTrue(True)
''',
            
            # 配置目录
            'config/__init__.py': '',
            
            # 文档（非Python文件）
            'README.md': '# Test Project\n\nThis is a test project.',
            'requirements.txt': 'pytest\nlogging\n',
        }
        
        # 创建所有文件
        for file_path, content in project_files.items():
            full_path = Path(self.temp_project) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
    
    def create_config_file(self):
        """创建模块管理器配置文件"""
        config = {
            "auto_discovery": True,
            "lazy_loading": True,
            "enable_cache": True,
            "scan_paths": [
                str(Path(self.temp_project) / 'src')
            ],
            "exclude_patterns": [
                "test_*",
                "*_test.py",
                "tests/*",
                "__pycache__/*"
            ],
            "module_aliases": {
                "ui": "src.ui.main_window",
                "config": "src.config.manager",
                "logger": "src.common.logger",
                "utils": "src.common.utils",
                "automation": "src.game.automation",
                "dialogs": "src.ui.dialogs"
            },
            "preload_modules": [
                "src.common.logger",
                "src.common.utils"
            ],
            "performance": {
                "enable_stats": True,
                "cache_size_limit": 50
            },
            "logging": {
                "level": "INFO",
                "enable_discovery_logs": True
            }
        }
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入配置文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def test_end_to_end_system_initialization(self):
        """测试端到端的系统初始化"""
        # 初始化模块管理器
        manager = initialize_module_manager(str(self.config_file))
        
        # 验证初始化成功
        self.assertIsInstance(manager, ModuleManager)
        self.assertTrue(manager.is_initialized())
        
        # 验证配置加载
        self.assertTrue(manager.config.auto_discovery)
        self.assertTrue(manager.config.lazy_loading)
        self.assertEqual(len(manager.config.module_aliases), 6)
        
        # 验证单例行为
        manager2 = get_module_manager()
        self.assertIs(manager, manager2)
    
    def test_automatic_module_discovery(self):
        """测试自动模块发现"""
        manager = initialize_module_manager(str(self.config_file))
        
        # 执行模块发现
        discovered_modules = manager.discover_modules()
        
        # 验证发现的模块数量（应该排除测试文件）
        self.assertGreater(len(discovered_modules), 5)
        
        # 验证特定模块被发现
        module_names = [mod.name for mod in discovered_modules]
        expected_modules = ['main', 'main_window', 'manager', 'logger', 'utils', 'automation']
        
        for expected in expected_modules:
            self.assertIn(expected, module_names)
        
        # 验证测试文件被排除
        self.assertNotIn('test_example', module_names)
        
        # 验证模块信息完整性
        for module in discovered_modules:
            self.assertIsInstance(module, ModuleInfo)
            self.assertIsNotNone(module.name)
            self.assertIsNotNone(module.path)
            self.assertEqual(module.status, ModuleStatus.DISCOVERED)
    
    def test_alias_resolution_and_loading(self):
        """测试别名解析和模块加载"""
        manager = initialize_module_manager(str(self.config_file))
        manager.discover_modules()
        
        # 测试别名解析
        resolved_ui = manager.resolve_identifier('ui')
        self.assertEqual(resolved_ui, 'src.ui.main_window')
        
        resolved_config = manager.resolve_identifier('config')
        self.assertEqual(resolved_config, 'src.config.manager')
        
        # 测试直接标识符（非别名）
        resolved_direct = manager.resolve_identifier('src.game.automation')
        self.assertEqual(resolved_direct, 'src.game.automation')
    
    @patch('sys.path')
    def test_module_loading_with_path_management(self, mock_path):
        """测试带路径管理的模块加载"""
        # 设置模拟的sys.path
        mock_path.__contains__ = MagicMock(return_value=False)
        mock_path.insert = MagicMock()
        
        manager = initialize_module_manager(str(self.config_file))
        manager.discover_modules()
        
        # 模拟模块加载
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_import.return_value = mock_module
            
            # 尝试加载模块
            result = manager.load_module('main_window')
            
            # 验证路径被添加到sys.path
            mock_path.insert.assert_called()
            
            # 验证模块导入被调用
            mock_import.assert_called()
    
    def test_preload_modules_functionality(self):
        """测试模块预加载功能"""
        manager = initialize_module_manager(str(self.config_file))
        manager.discover_modules()
        
        # 模拟预加载
        with patch('importlib.import_module') as mock_import:
            mock_logger_module = MagicMock()
            mock_utils_module = MagicMock()
            mock_import.side_effect = [mock_logger_module, mock_utils_module]
            
            # 执行预加载
            manager.preload_modules()
            
            # 验证预加载模块被导入
            self.assertEqual(mock_import.call_count, 2)
            
            # 验证模块被缓存
            self.assertGreater(len(manager.cache.loaded_modules), 0)
    
    def test_dependency_resolution(self):
        """测试依赖关系解析"""
        manager = initialize_module_manager(str(self.config_file))
        discovered_modules = manager.discover_modules()
        
        # 查找main_window模块
        main_window_module = None
        for module in discovered_modules:
            if module.name == 'main_window':
                main_window_module = module
                break
        
        self.assertIsNotNone(main_window_module)
        
        # 验证依赖关系被正确提取
        dependencies = main_window_module.dependencies
        self.assertIsInstance(dependencies, list)
        
        # 验证包含预期的依赖（可能包含相对导入）
        # 注意：具体的依赖名称可能因解析方式而异
        self.assertGreater(len(dependencies), 0)
    
    def test_performance_and_caching(self):
        """测试性能统计和缓存机制"""
        manager = initialize_module_manager(str(self.config_file))
        
        # 执行一些操作来生成统计数据
        discovered = manager.discover_modules()
        
        # 模拟模块加载以测试缓存
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_import.return_value = mock_module
            
            # 第一次加载（缓存未命中）
            result1 = manager.load_module('logger')
            
            # 第二次加载（应该从缓存获取）
            result2 = manager.load_module('logger')
            
            # 验证缓存工作
            self.assertEqual(result1, result2)
        
        # 获取性能统计
        stats = manager.get_performance_stats()
        
        # 验证统计数据
        self.assertIn('modules_discovered', stats)
        self.assertIn('modules_loaded', stats)
        self.assertIn('cache_hits', stats)
        self.assertIn('cache_misses', stats)
        self.assertGreater(stats['modules_discovered'], 0)
    
    def test_error_handling_and_recovery(self):
        """测试错误处理和恢复机制"""
        manager = initialize_module_manager(str(self.config_file))
        manager.discover_modules()
        
        # 测试加载不存在的模块
        result = manager.load_module('nonexistent_module')
        self.assertIsNone(result)
        
        # 测试导入失败的恢复
        with patch('importlib.import_module', side_effect=ImportError("Test import error")):
            result = manager.load_module('logger')
            self.assertIsNone(result)
            
            # 验证模块状态被正确更新
            module_info = manager.get_module('logger')
            if module_info:
                self.assertEqual(module_info.status, ModuleStatus.ERROR)
    
    def test_configuration_driven_behavior(self):
        """测试配置驱动的行为"""
        # 测试禁用自动发现的配置
        config_no_auto = {
            "auto_discovery": False,
            "lazy_loading": False,
            "enable_cache": False,
            "scan_paths": [str(Path(self.temp_project) / 'src')],
            "exclude_patterns": [],
            "module_aliases": {},
            "preload_modules": [],
            "performance": {"enable_stats": False},
            "logging": {"level": "WARNING"}
        }
        
        # 创建临时配置文件
        temp_config = Path(self.temp_project) / 'temp_config.json'
        with open(temp_config, 'w', encoding='utf-8') as f:
            json.dump(config_no_auto, f)
        
        # 使用新配置初始化
        ModuleManager._instance = None
        ModuleManager._initialized = False
        
        manager = initialize_module_manager(str(temp_config))
        
        # 验证配置生效
        self.assertFalse(manager.config.auto_discovery)
        self.assertFalse(manager.config.lazy_loading)
        self.assertFalse(manager.config.enable_cache)
        self.assertEqual(len(manager.config.module_aliases), 0)
    
    def test_module_reload_functionality(self):
        """测试模块重载功能"""
        manager = initialize_module_manager(str(self.config_file))
        manager.discover_modules()
        
        # 模拟模块加载和重载
        with patch('importlib.import_module') as mock_import, \
             patch('importlib.reload') as mock_reload:
            
            mock_module = MagicMock()
            mock_import.return_value = mock_module
            mock_reload.return_value = mock_module
            
            # 首次加载
            loaded_module = manager.load_module('utils')
            self.assertEqual(loaded_module, mock_module)
            
            # 重载模块
            reloaded_module = manager.reload_module('utils')
            self.assertEqual(reloaded_module, mock_module)
            
            # 验证reload被调用
            mock_reload.assert_called_once_with(mock_module)
    
    def test_cache_size_limit_enforcement(self):
        """测试缓存大小限制执行"""
        # 创建小缓存限制的配置
        config_small_cache = {
            "auto_discovery": True,
            "lazy_loading": True,
            "enable_cache": True,
            "scan_paths": [str(Path(self.temp_project) / 'src')],
            "exclude_patterns": [],
            "module_aliases": {},
            "preload_modules": [],
            "performance": {
                "enable_stats": True,
                "cache_size_limit": 2  # 很小的限制
            },
            "logging": {"level": "INFO"}
        }
        
        # 创建临时配置
        temp_config = Path(self.temp_project) / 'small_cache_config.json'
        with open(temp_config, 'w', encoding='utf-8') as f:
            json.dump(config_small_cache, f)
        
        # 重置并初始化
        ModuleManager._instance = None
        ModuleManager._initialized = False
        
        manager = initialize_module_manager(str(temp_config))
        manager.discover_modules()
        
        # 模拟加载多个模块以测试缓存限制
        with patch('importlib.import_module') as mock_import:
            mock_modules = [MagicMock() for _ in range(5)]
            mock_import.side_effect = mock_modules
            
            # 加载多个模块
            module_names = ['logger', 'utils', 'main_window', 'manager', 'automation']
            for name in module_names:
                manager.load_module(name)
            
            # 验证缓存大小不超过限制
            cache_size = len(manager.cache.loaded_modules)
            self.assertLessEqual(cache_size, 2)
    
    def test_logging_integration(self):
        """测试日志集成"""
        with self.assertLogs(level='INFO') as log_context:
            manager = initialize_module_manager(str(self.config_file))
            manager.discover_modules()
        
        # 验证有日志输出
        self.assertGreater(len(log_context.output), 0)
    
    def test_real_world_usage_scenario(self):
        """测试真实世界使用场景"""
        # 初始化系统
        manager = initialize_module_manager(str(self.config_file))
        
        # 发现模块
        discovered = manager.discover_modules()
        self.assertGreater(len(discovered), 0)
        
        # 使用别名获取模块信息
        ui_path = manager.resolve_identifier('ui')
        self.assertEqual(ui_path, 'src.ui.main_window')
        
        # 获取模块信息
        ui_info = manager.get_module_info('main_window')
        if ui_info:
            self.assertIn('name', ui_info)
            self.assertIn('status', ui_info)
        
        # 检查性能统计
        stats = manager.get_performance_stats()
        self.assertIsInstance(stats, dict)
        
        # 清理缓存
        manager.clear_cache()
        self.assertEqual(len(manager.cache.loaded_modules), 0)


if __name__ == '__main__':
    unittest.main()