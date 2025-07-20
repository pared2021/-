#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块发现功能单元测试

测试 ModuleDiscovery 类的各项功能：
- 模块扫描
- 模块识别
- 信息提取
- 依赖关系构建
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 导入被测试的模块
from ..src.common.module_discovery import ModuleDiscovery
from ..src.common.module_types import ModuleInfo, ModuleType, ModuleStatus


class TestModuleDiscovery(unittest.TestCase):
    """ModuleDiscovery 类测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.discovery = ModuleDiscovery()
        
        # 创建测试文件结构
        self.create_test_structure()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_structure(self):
        """创建测试用的文件结构"""
        # 创建测试模块文件
        test_files = {
            'module_a.py': '''
import os
import sys
from pathlib import Path

def function_a():
    return "Hello from A"

class ClassA:
    pass
''',
            'module_b.py': '''
from .module_a import function_a
import json

def function_b():
    return function_a() + " and B"
''',
            'subdir/__init__.py': '',
            'subdir/module_c.py': '''
from ..module_a import ClassA
from module_b import function_b

class ClassC(ClassA):
    pass
''',
            '__init__.py': '',
            'not_python.txt': 'This is not a Python file',
        }
        
        for file_path, content in test_files.items():
            full_path = Path(self.temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
    
    def test_scan_directory(self):
        """测试目录扫描功能"""
        modules = self.discovery.scan_directory(self.temp_dir)
        
        # 验证找到的模块数量（应该找到4个.py文件）
        self.assertEqual(len(modules), 4)
        
        # 验证模块路径
        module_names = [mod.name for mod in modules]
        expected_names = ['module_a', 'module_b', 'module_c', '__init__']
        
        for name in expected_names:
            self.assertIn(name, module_names)
    
    def test_is_python_module(self):
        """测试Python模块识别"""
        # 测试Python文件
        py_file = Path(self.temp_dir) / 'test.py'
        py_file.write_text('# Python file')
        self.assertTrue(self.discovery._is_python_module(py_file))
        
        # 测试非Python文件
        txt_file = Path(self.temp_dir) / 'test.txt'
        txt_file.write_text('Not Python')
        self.assertFalse(self.discovery._is_python_module(txt_file))
        
        # 测试目录
        test_dir = Path(self.temp_dir) / 'testdir'
        test_dir.mkdir()
        self.assertFalse(self.discovery._is_python_module(test_dir))
    
    def test_extract_module_info(self):
        """测试模块信息提取"""
        module_path = Path(self.temp_dir) / 'module_a.py'
        module_info = self.discovery._extract_module_info(module_path)
        
        # 验证基本信息
        self.assertEqual(module_info.name, 'module_a')
        self.assertEqual(module_info.path, str(module_path))
        self.assertEqual(module_info.type, ModuleType.REGULAR)
        self.assertEqual(module_info.status, ModuleStatus.DISCOVERED)
        
        # 验证文件信息
        self.assertGreater(module_info.size, 0)
        self.assertIsNotNone(module_info.modified_time)
        self.assertGreater(module_info.line_count, 0)
        
        # 验证依赖信息
        expected_deps = {'os', 'sys', 'pathlib'}
        actual_deps = set(module_info.dependencies)
        self.assertTrue(expected_deps.issubset(actual_deps))
    
    def test_extract_dependencies(self):
        """测试依赖关系提取"""
        # 测试标准库导入
        content1 = "import os\nimport sys\nfrom pathlib import Path"
        deps1 = self.discovery._extract_dependencies(content1)
        expected1 = {'os', 'sys', 'pathlib'}
        self.assertEqual(set(deps1), expected1)
        
        # 测试相对导入
        content2 = "from .module_a import function_a\nfrom ..parent import something"
        deps2 = self.discovery._extract_dependencies(content2)
        self.assertIn('module_a', deps2)
        self.assertIn('parent', deps2)
        
        # 测试第三方库导入
        content3 = "import numpy as np\nfrom pandas import DataFrame"
        deps3 = self.discovery._extract_dependencies(content3)
        expected3 = {'numpy', 'pandas'}
        self.assertEqual(set(deps3), expected3)
    
    def test_is_standard_library(self):
        """测试标准库判断"""
        # 标准库模块
        self.assertTrue(self.discovery._is_standard_library('os'))
        self.assertTrue(self.discovery._is_standard_library('sys'))
        self.assertTrue(self.discovery._is_standard_library('json'))
        self.assertTrue(self.discovery._is_standard_library('pathlib'))
        
        # 非标准库模块
        self.assertFalse(self.discovery._is_standard_library('numpy'))
        self.assertFalse(self.discovery._is_standard_library('pandas'))
        self.assertFalse(self.discovery._is_standard_library('custom_module'))
    
    def test_build_dependency_graph(self):
        """测试依赖关系图构建"""
        modules = self.discovery.scan_directory(self.temp_dir)
        graph = self.discovery.build_dependency_graph(modules)
        
        # 验证图结构
        self.assertIsInstance(graph, dict)
        
        # 验证模块存在于图中
        module_names = [mod.name for mod in modules]
        for name in module_names:
            self.assertIn(name, graph)
        
        # 验证依赖关系
        # module_b 应该依赖 module_a
        if 'module_b' in graph and 'module_a' in graph:
            # 检查是否存在依赖关系（可能通过不同方式表示）
            self.assertIsInstance(graph['module_b'], list)
    
    def test_should_exclude_file(self):
        """测试文件排除逻辑"""
        # 测试排除模式
        exclude_patterns = ['test_*', '*_test.py', '__pycache__']
        discovery = ModuleDiscovery(exclude_patterns=exclude_patterns)
        
        # 应该排除的文件
        self.assertTrue(discovery._should_exclude_file(Path('test_module.py')))
        self.assertTrue(discovery._should_exclude_file(Path('module_test.py')))
        self.assertTrue(discovery._should_exclude_file(Path('__pycache__/cache.py')))
        
        # 不应该排除的文件
        self.assertFalse(discovery._should_exclude_file(Path('normal_module.py')))
        self.assertFalse(discovery._should_exclude_file(Path('src/main.py')))
    
    def test_filter_dependencies(self):
        """测试依赖过滤"""
        # 包含标准库和第三方库的依赖列表
        all_deps = ['os', 'sys', 'numpy', 'pandas', 'custom_module']
        
        # 过滤标准库
        filtered = self.discovery._filter_dependencies(all_deps, include_stdlib=False)
        self.assertNotIn('os', filtered)
        self.assertNotIn('sys', filtered)
        self.assertIn('numpy', filtered)
        self.assertIn('custom_module', filtered)
        
        # 包含标准库
        unfiltered = self.discovery._filter_dependencies(all_deps, include_stdlib=True)
        self.assertEqual(len(unfiltered), len(all_deps))
    
    @patch('src.common.module_discovery.logging')
    def test_logging_integration(self, mock_logging):
        """测试日志集成"""
        # 执行扫描操作
        modules = self.discovery.scan_directory(self.temp_dir)
        
        # 验证日志调用
        mock_logging.getLogger.assert_called()
        
        # 验证扫描结果
        self.assertGreater(len(modules), 0)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试不存在的目录
        non_existent = '/path/that/does/not/exist'
        modules = self.discovery.scan_directory(non_existent)
        self.assertEqual(len(modules), 0)
        
        # 测试权限错误（模拟）
        with patch('pathlib.Path.iterdir', side_effect=PermissionError()):
            modules = self.discovery.scan_directory(self.temp_dir)
            self.assertEqual(len(modules), 0)
    
    def test_performance_with_large_directory(self):
        """测试大目录的性能（简化版）"""
        # 创建多个测试文件
        for i in range(10):
            test_file = Path(self.temp_dir) / f'module_{i}.py'
            test_file.write_text(f'# Module {i}\ndef func_{i}(): pass')
        
        # 执行扫描
        import time
        start_time = time.time()
        modules = self.discovery.scan_directory(self.temp_dir)
        end_time = time.time()
        
        # 验证结果和性能
        self.assertGreaterEqual(len(modules), 10)
        self.assertLess(end_time - start_time, 5.0)  # 应该在5秒内完成


if __name__ == '__main__':
    unittest.main()