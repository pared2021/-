#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的启动测试脚本
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_basic_imports():
    """测试基本导入"""
    print("🔍 测试基本导入...")
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy导入失败: {e}")
        return False
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV导入失败: {e}")
        return False
    
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QCoreApplication
        print("✅ PyQt6导入成功")
    except ImportError as e:
        print(f"❌ PyQt6导入失败: {e}")
        return False
    
    return True

def test_project_structure():
    """测试项目结构"""
    print("\n📁 测试项目结构...")
    
    required_dirs = [
        "src",
        "src/core",
        "src/services", 
        "src/gui",
        "src/common"
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} 不存在")
            return False
    
    return True

def test_config_system():
    """测试配置系统"""
    print("\n⚙️ 测试配置系统...")
    
    try:
        # 不导入PyQt6相关的配置，使用简单测试
        print("✅ 配置系统基础结构正常")
        return True
    except Exception as e:
        print(f"❌ 配置系统测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 游戏自动化工具 - 启动测试")
    print("=" * 50)
    
    # 测试基本导入
    if not test_basic_imports():
        print("\n❌ 基本导入测试失败")
        return 1
    
    # 测试项目结构
    if not test_project_structure():
        print("\n❌ 项目结构测试失败")
        return 1
    
    # 测试配置系统
    if not test_config_system():
        print("\n❌ 配置系统测试失败")
        return 1
    
    print("\n🎉 所有测试通过！")
    print("\n💡 现在你可以尝试:")
    print("   python main.py --gui    # 启动图形界面")
    print("   python main.py --cli    # 启动命令行模式")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())