#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化UI测试脚本
用于测试新的现代化游戏风格界面
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_modern_ui():
    """测试现代化UI"""
    try:
        print("🎮 测试现代化UI界面...")
        
        # 导入PyQt6
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QCoreApplication
        
        # 导入现代化UI组件
        from src.gui.modern_ui.modern_main_window import ModernMainWindow
        from src.gui.modern_ui.modern_styles import MODERN_APP_STYLE
        
        print("✅ 现代化UI模块导入成功")
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 设置应用信息
        QCoreApplication.setApplicationName("游戏自动化工具")
        QCoreApplication.setOrganizationName("GameAutomation")
        QCoreApplication.setApplicationVersion("2.0.0")
        
        print("🎨 应用现代化样式...")
        
        # 创建现代化主窗口（不使用依赖注入容器进行测试）
        window = ModernMainWindow(container=None)
        window.show()
        
        print("🚀 现代化界面启动成功！")
        print("💡 界面特性:")
        print("   - 深色渐变背景")
        print("   - 卡片式布局")
        print("   - 现代化按钮和控件")
        print("   - 游戏风格设计")
        print("   - 无边框窗口")
        print("   - 阴影效果")
        
        # 运行应用
        return app.exec()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保已安装PyQt6: pip install PyQt6")
        return 1
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

def test_components():
    """测试现代化组件"""
    try:
        print("🧩 测试现代化组件...")
        
        # 测试样式导入
        from src.gui.modern_ui.modern_styles import (
            MODERN_APP_STYLE, GAME_THEME_COLORS, CARD_STYLE
        )
        print("✅ 样式模块导入成功")
        
        # 测试组件导入
        from src.gui.modern_ui.modern_widgets import (
            ModernCard, ModernButton, ModernProgressBar,
            ModernControlPanel, ModernGameView, ModernStatusPanel
        )
        print("✅ 组件模块导入成功")
        
        # 测试主窗口导入
        from src.gui.modern_ui.modern_main_window import ModernMainWindow
        print("✅ 主窗口模块导入成功")
        
        print("🎨 主题配色:")
        for key, value in GAME_THEME_COLORS.items():
            print(f"   {key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"❌ 组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🎮 现代化UI测试工具")
    print("=" * 60)
    
    # 测试组件
    if not test_components():
        print("❌ 组件测试失败，无法启动UI")
        return 1
    
    print("\n" + "=" * 60)
    print("🚀 启动现代化UI界面")
    print("=" * 60)
    
    # 测试UI
    return test_modern_ui()

if __name__ == "__main__":
    sys.exit(main())