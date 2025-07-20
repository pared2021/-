#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能模块导入系统

使用方法:
  py test_import.py  # 注意：在Windows上使用py命令而不是python
"""

import sys
import os
import time

print("=== 智能模块导入系统测试 ===")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print()

# 测试直接导入
print("=== 测试直接导入 ===")
try:
    from src.common import module_types
    print("✅ 成功导入 src.common.module_types")
    print(f"Available attributes: {[attr for attr in dir(module_types) if not attr.startswith('_')]}")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 其他错误: {e}")
    sys.exit(1)

# 测试模块管理器
print("\n=== 测试模块管理器 ===")
try:
    # 初始化模块管理器
    from src.common.module_manager import initialize_module_manager
    
    print("开始初始化模块管理器...")
    start_time = time.time()
    
    module_manager = initialize_module_manager()
    
    end_time = time.time()
    print(f"✅ 初始化完成，耗时: {end_time - start_time:.4f}秒")
    
    # 获取统计信息
    stats = module_manager.get_statistics()
    print("\n模块统计信息:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 测试别名导入
    print("\n测试别名导入:")
    aliases = module_manager.cache.aliases
    print(f"已注册别名数量: {len(aliases)}")
    
    # 测试几个关键别名
    test_aliases = ['@config', '@logger', '@common', '@core']
    for alias in test_aliases:
        if alias in aliases:
            print(f"  {alias} -> {aliases[alias]}")
            try:
                module = module_manager.get_module(alias)
                print(f"    ✅ 成功加载模块: {module.__name__}")
            except Exception as e:
                print(f"    ❌ 加载失败: {e}")
        else:
            print(f"  ❌ 别名未注册: {alias}")
    
    # 测试模块发现
    print("\n测试模块发现:")
    discovered_modules = module_manager.discover_modules()
    print(f"发现的模块数量: {len(discovered_modules)}")
    
    # 检查关键模块是否被发现
    key_modules = [
        'src.common.module_manager',
        'src.common.module_discovery',
        'src.common.module_types'
    ]
    
    for module_name in key_modules:
        if module_name in discovered_modules:
            print(f"  ✅ 发现: {module_name}")
        else:
            print(f"  ❌ 未发现: {module_name}")
    
    print("\n🎉 模块管理器测试成功!")
    
except ImportError as e:
    print(f"❌ 导入模块管理器失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 模块管理器测试失败: {e}")
    print(f"错误类型: {type(e).__name__}")
    sys.exit(1)

print("\n=== 测试完成 ===")
print("\n💡 提示: 在Windows上请使用 'py test_import.py' 命令运行此脚本")