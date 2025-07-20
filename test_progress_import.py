#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度条组件导入测试
用于测试progress.py模块的导入是否正常
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """测试各个模块的导入"""
    try:
        print("🔍 测试模块导入...")
        
        # 测试design_tokens导入
        print("📋 测试design_tokens导入...")
        from src.gui.modern_ui.design_tokens import DesignTokens, ComponentSize, ComponentVariant
        print("✅ design_tokens导入成功")
        
        # 测试style_generator导入
        print("🎨 测试style_generator导入...")
        from src.gui.modern_ui.style_generator import StyleGenerator
        print("✅ style_generator导入成功")
        
        # 测试base组件导入
        print("🏗️ 测试base组件导入...")
        from src.gui.modern_ui.components.base import BaseComponent
        print("✅ base组件导入成功")
        
        # 测试typography组件导入
        print("📝 测试typography组件导入...")
        from src.gui.modern_ui.components.typography import Typography
        print("✅ typography组件导入成功")
        
        # 测试progress组件导入
        print("🔄 测试progress组件导入...")
        from src.gui.modern_ui.components.progress import ProgressBar, StepProgress
        print("✅ progress组件导入成功")
        
        print("\n🎉 所有模块导入测试通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """测试基本功能"""
    try:
        print("\n🧪 测试基本功能...")
        
        # 导入必要模块
        from src.gui.modern_ui.design_tokens import DesignTokens, ComponentSize, ComponentVariant
        from src.gui.modern_ui.style_generator import StyleGenerator
        
        # 创建design_tokens实例
        design_tokens = DesignTokens()
        print("✅ DesignTokens实例创建成功")
        
        # 创建style_generator实例
        style_generator = StyleGenerator()
        print("✅ StyleGenerator实例创建成功")
        
        # 测试样式生成
        style = style_generator.generate_progress_style(
            size=ComponentSize.MEDIUM,
            variant=ComponentVariant.PRIMARY
        )
        print("✅ 进度条样式生成成功")
        print(f"📄 生成的样式长度: {len(style)} 字符")
        
        print("\n🎉 基本功能测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 进度条组件导入测试工具")
    print("=" * 60)
    
    # 测试导入
    if not test_imports():
        print("❌ 导入测试失败")
        return 1
    
    # 测试基本功能
    if not test_basic_functionality():
        print("❌ 功能测试失败")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 所有测试通过！进度条组件可以正常使用")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())