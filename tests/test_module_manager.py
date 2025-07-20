#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块管理器单元测试

测试 ModuleManager 类的各项功能：
- 单例模式
- 配置加载
- 模块发现和注册
- 别名管理
- 模块加载和重载
- 性能统计
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# 导入被测试的模块
from ..src.common.module_manager import ModuleManager, get_module_manager, initialize_module_manager
from ..src.common.module_types import ModuleInfo, ModuleType, ModuleStatus, ModuleManagerConfig


class TestModuleManager(unittest.TestCase):
    """ModuleManager 类测试"""
    
    def setUp(self):
        """测试前准备"""
        # 重置单例实例
        ModuleManager._instance = None
        ModuleManager._initialized = False
        
        # 创建临时目录和配置
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / 'test_config.json'
        
        # 创建测试配置
        self.test_config = {
            "auto_discovery": True,
            "lazy_loading": True,
            "enable_cache": True,
            "scan_paths": [self.temp_dir],
            "exclude_patterns": ["test_*", "*_test.py"],
            "module_aliases": {
                "ui": "src.ui.main_window",
                "config": "src.config.manager"
            },
            "preload_modules": ["src.common.logger"],
            "performance": {
                "enable_stats": True,
                "cache_size_limit": 100
            },
            "logging": {
                "level": "INFO",
                "enable_discovery_logs": True
            }
        }
        
        # 写入配置文件
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_config, f, indent=2)
        
        # 创建测试模块文件
        self.create_test_modules()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        # 重置单例
        ModuleManager._instance = None
        ModuleManager._initialized = False
    
    def create_test_modules(self):
        """创建测试用的模块文件"""
        test_modules = {
            'test_module_a.py': '''
def function_a():
    return "Hello from A"

class ClassA:
    def method_a(self):
        return "Method A"
''',
            'test_module_b.py': '''
from .test_module_a import function_a

def function_b():
    return function_a() + " and B"

class ClassB:
    pass
''',
            'subdir/__init__.py': '',
            'subdir/test_module_c.py': '''
class ClassC:
    def __init__(self):
        self.value = "C"
'''
        }
        
        for file_path, content in test_modules.items():
            full_path = Path(self.temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        # 创建两个实例
        manager1 = ModuleManager()
        manager2 = ModuleManager()
        
        # 验证是同一个实例
        self.assertIs(manager1, manager2)
        
        # 验证全局函数返回同一实例
        manager3 = get_module_manager()
        self.assertIs(manager1, manager3)
    
    def test_config_loading(self):
        """测试配置加载"""
        manager = ModuleManager()
        
        # 测试从文件加载配置
        manager.load_config(str(self.config_file))
        
        # 验证配置加载
        self.assertTrue(manager.config.auto_discovery)
        self.assertTrue(manager.config.lazy_loading)
        self.assertEqual(len(manager.config.scan_paths), 1)
        self.assertIn(self.temp_dir, manager.config.scan_paths)
        
        # 验证别名配置
        self.assertIn('ui', manager.config.module_aliases)
        self.assertEqual(manager.config.module_aliases['ui'], 'src.ui.main_window')
    
    def test_config_loading_with_dict(self):
        """测试从字典加载配置"""
        manager = ModuleManager()
        manager.load_config(self.test_config)
        
        # 验证配置
        self.assertTrue(manager.config.auto_discovery)
        self.assertEqual(len(manager.config.module_aliases), 2)
    
    def test_config_loading_invalid_file(self):
        """测试加载无效配置文件"""
        manager = ModuleManager()
        
        # 测试不存在的文件
        with self.assertLogs(level='WARNING'):
            manager.load_config('/path/that/does/not/exist.json')
        
        # 验证使用默认配置
        self.assertIsNotNone(manager.config)
    
    @patch('src.common.module_manager.ModuleDiscovery')
    def test_discover_modules(self, mock_discovery_class):
        """测试模块发现"""
        # 设置模拟
        mock_discovery = MagicMock()
        mock_discovery_class.return_value = mock_discovery
        
        # 创建模拟的模块信息
        mock_modules = [
            ModuleInfo(
                name='test_module_a',
                path=str(Path(self.temp_dir) / 'test_module_a.py'),
                type=ModuleType.REGULAR,
                status=ModuleStatus.DISCOVERED
            ),
            ModuleInfo(
                name='test_module_b', 
                path=str(Path(self.temp_dir) / 'test_module_b.py'),
                type=ModuleType.REGULAR,
                status=ModuleStatus.DISCOVERED
            )
        ]
        mock_discovery.scan_directory.return_value = mock_modules
        
        # 执行测试
        manager = ModuleManager()
        manager.load_config(self.test_config)
        discovered = manager.discover_modules()
        
        # 验证结果
        self.assertEqual(len(discovered), 2)
        self.assertIn('test_module_a', [mod.name for mod in discovered])
        
        # 验证模块已注册
        self.assertIn('test_module_a', manager.modules)
    
    def test_register_alias(self):
        """测试别名注册"""
        manager = ModuleManager()
        
        # 注册别名
        manager.register_alias('test_alias', 'test.module.path')
        
        # 验证别名注册
        self.assertIn('test_alias', manager.aliases)
        self.assertEqual(manager.aliases['test_alias'], 'test.module.path')
    
    def test_register_multiple_aliases(self):
        """测试批量别名注册"""
        manager = ModuleManager()
        
        aliases = {
            'alias1': 'module.path1',
            'alias2': 'module.path2',
            'alias3': 'module.path3'
        }
        
        manager.register_aliases(aliases)
        
        # 验证所有别名
        for alias, path in aliases.items():
            self.assertIn(alias, manager.aliases)
            self.assertEqual(manager.aliases[alias], path)
    
    def test_preload_modules(self):
        """测试模块预加载"""
        manager = ModuleManager()
        manager.load_config(self.test_config)
        
        # 模拟预加载模块存在
        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_import.return_value = mock_module
            
            manager.preload_modules()
            
            # 验证导入调用
            mock_import.assert_called()
    
    def test_get_module_existing(self):
        """测试获取已存在的模块"""
        manager = ModuleManager()
        
        # 创建模拟模块信息
        module_info = ModuleInfo(
            name='test_module',
            path='/path/to/test_module.py',
            type=ModuleType.REGULAR,
            status=ModuleStatus.LOADED
        )
        manager.modules['test_module'] = module_info
        
        # 获取模块
        result = manager.get_module('test_module')
        
        # 验证结果
        self.assertEqual(result, module_info)
    
    def test_get_module_nonexistent(self):
        """测试获取不存在的模块"""
        manager = ModuleManager()
        
        # 获取不存在的模块
        result = manager.get_module('nonexistent_module')
        
        # 验证返回None
        self.assertIsNone(result)
    
    @patch('importlib.import_module')
    def test_load_module(self, mock_import):
        """测试模块加载"""
        manager = ModuleManager()
        
        # 设置模拟
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        
        # 创建模块信息
        module_info = ModuleInfo(
            name='test_module',
            path='/path/to/test_module.py',
            type=ModuleType.REGULAR,
            status=ModuleStatus.DISCOVERED
        )
        manager.modules['test_module'] = module_info
        
        # 加载模块
        result = manager.load_module('test_module')
        
        # 验证结果
        self.assertEqual(result, mock_module)
        self.assertEqual(module_info.status, ModuleStatus.LOADED)
        
        # 验证缓存
        self.assertIn('test_module', manager.cache.loaded_modules)
    
    @patch('importlib.reload')
    @patch('importlib.import_module')
    def test_reload_module(self, mock_import, mock_reload):
        """测试模块重载"""
        manager = ModuleManager()
        
        # 设置模拟
        mock_module = MagicMock()
        mock_import.return_value = mock_module
        mock_reload.return_value = mock_module
        
        # 创建已加载的模块
        module_info = ModuleInfo(
            name='test_module',
            path='/path/to/test_module.py',
            type=ModuleType.REGULAR,
            status=ModuleStatus.LOADED
        )
        manager.modules['test_module'] = module_info
        manager.cache.loaded_modules['test_module'] = mock_module
        
        # 重载模块
        result = manager.reload_module('test_module')
        
        # 验证重载调用
        mock_reload.assert_called_once_with(mock_module)
        self.assertEqual(result, mock_module)
    
    def test_get_module_info(self):
        """测试获取模块信息"""
        manager = ModuleManager()
        
        # 创建模块信息
        module_info = ModuleInfo(
            name='test_module',
            path='/path/to/test_module.py',
            type=ModuleType.REGULAR,
            status=ModuleStatus.LOADED,
            size=1024,
            line_count=50
        )
        manager.modules['test_module'] = module_info
        
        # 获取信息
        info = manager.get_module_info('test_module')
        
        # 验证信息
        self.assertEqual(info['name'], 'test_module')
        self.assertEqual(info['status'], 'loaded')
        self.assertEqual(info['size'], 1024)
        self.assertEqual(info['line_count'], 50)
    
    def test_resolve_identifier_alias(self):
        """测试别名解析"""
        manager = ModuleManager()
        manager.register_alias('ui', 'src.ui.main_window')
        
        # 解析别名
        resolved = manager.resolve_identifier('ui')
        
        # 验证解析结果
        self.assertEqual(resolved, 'src.ui.main_window')
    
    def test_resolve_identifier_direct(self):
        """测试直接标识符解析"""
        manager = ModuleManager()
        
        # 解析非别名标识符
        resolved = manager.resolve_identifier('direct.module.path')
        
        # 验证返回原始路径
        self.assertEqual(resolved, 'direct.module.path')
    
    @patch('inspect.currentframe')
    def test_get_caller_module(self, mock_frame):
        """测试调用者模块获取"""
        manager = ModuleManager()
        
        # 设置模拟帧
        mock_frame_obj = MagicMock()
        mock_frame_obj.f_back.f_back.f_globals = {'__name__': 'test.caller.module'}
        mock_frame.return_value = mock_frame_obj
        
        # 获取调用者模块
        caller = manager._get_caller_module()
        
        # 验证结果
        self.assertEqual(caller, 'test.caller.module')
    
    def test_performance_stats(self):
        """测试性能统计"""
        manager = ModuleManager()
        manager.load_config(self.test_config)
        
        # 模拟一些操作来生成统计数据
        manager.stats['modules_discovered'] = 5
        manager.stats['modules_loaded'] = 3
        manager.stats['cache_hits'] = 10
        manager.stats['cache_misses'] = 2
        
        # 获取性能统计
        stats = manager.get_performance_stats()
        
        # 验证统计数据
        self.assertEqual(stats['modules_discovered'], 5)
        self.assertEqual(stats['modules_loaded'], 3)
        self.assertEqual(stats['cache_hits'], 10)
        self.assertEqual(stats['cache_misses'], 2)
        self.assertIn('cache_hit_rate', stats)
    
    def test_clear_cache(self):
        """测试缓存清理"""
        manager = ModuleManager()
        
        # 添加一些缓存数据
        manager.cache.loaded_modules['test1'] = MagicMock()
        manager.cache.loaded_modules['test2'] = MagicMock()
        
        # 清理缓存
        manager.clear_cache()
        
        # 验证缓存已清空
        self.assertEqual(len(manager.cache.loaded_modules), 0)
    
    def test_is_initialized(self):
        """测试初始化状态检查"""
        manager = ModuleManager()
        
        # 初始状态
        self.assertFalse(manager.is_initialized())
        
        # 加载配置后
        manager.load_config(self.test_config)
        self.assertTrue(manager.is_initialized())
    
    def test_initialize_module_manager_function(self):
        """测试全局初始化函数"""
        # 使用配置文件初始化
        manager = initialize_module_manager(str(self.config_file))
        
        # 验证初始化
        self.assertIsInstance(manager, ModuleManager)
        self.assertTrue(manager.is_initialized())
        
        # 验证单例
        manager2 = get_module_manager()
        self.assertIs(manager, manager2)
    
    def test_error_handling_import_failure(self):
        """测试导入失败的错误处理"""
        manager = ModuleManager()
        
        # 创建模块信息
        module_info = ModuleInfo(
            name='failing_module',
            path='/path/to/failing_module.py',
            type=ModuleType.REGULAR,
            status=ModuleStatus.DISCOVERED
        )
        manager.modules['failing_module'] = module_info
        
        # 模拟导入失败
        with patch('importlib.import_module', side_effect=ImportError("Module not found")):
            result = manager.load_module('failing_module')
        
        # 验证错误处理
        self.assertIsNone(result)
        self.assertEqual(module_info.status, ModuleStatus.ERROR)
    
    def test_lazy_loading_behavior(self):
        """测试懒加载行为"""
        manager = ModuleManager()
        config = self.test_config.copy()
        config['lazy_loading'] = True
        manager.load_config(config)
        
        # 创建模块信息但不立即加载
        module_info = ModuleInfo(
            name='lazy_module',
            path='/path/to/lazy_module.py',
            type=ModuleType.REGULAR,
            status=ModuleStatus.DISCOVERED
        )
        manager.modules['lazy_module'] = module_info
        
        # 验证模块未立即加载
        self.assertEqual(module_info.status, ModuleStatus.DISCOVERED)
        self.assertNotIn('lazy_module', manager.cache.loaded_modules)


if __name__ == '__main__':
    unittest.main()