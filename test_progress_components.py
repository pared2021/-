#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度条组件测试脚本
用于测试ProgressBar和StepProgress组件
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_progress_components():
    """测试进度条组件"""
    try:
        print("🧩 测试进度条组件...")
        
        # 导入PyQt6
        from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
        from PyQt6.QtCore import QTimer
        
        # 导入进度条组件
        from src.gui.modern_ui.components.progress import ProgressBar, StepProgress
        from src.gui.modern_ui.design_tokens import ComponentSize, ComponentVariant
        
        print("✅ 进度条组件导入成功")
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 创建主窗口
        window = QMainWindow()
        window.setWindowTitle("进度条组件测试")
        window.setGeometry(100, 100, 600, 400)
        
        # 创建中央部件
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建ProgressBar组件
        print("🔄 创建ProgressBar组件...")
        progress_bar = ProgressBar(
            size=ComponentSize.MEDIUM,
            variant=ComponentVariant.PRIMARY
        )
        progress_bar.set_value(50)  # 设置进度为50%
        layout.addWidget(progress_bar)
        
        # 创建StepProgress组件
        print("📋 创建StepProgress组件...")
        step_progress = StepProgress(
            steps=["步骤1", "步骤2", "步骤3", "步骤4"],
            current_step=1,
            size=ComponentSize.MEDIUM,
            variant=ComponentVariant.PRIMARY
        )
        layout.addWidget(step_progress)
        
        # 创建控制按钮
        def update_progress():
            current_value = progress_bar.value
            new_value = (current_value + 10) % 101
            progress_bar.set_value(new_value)
            
        def next_step():
            step_progress.next_step()
            
        def prev_step():
            step_progress.previous_step()
            
        update_btn = QPushButton("更新进度条")
        update_btn.clicked.connect(update_progress)
        layout.addWidget(update_btn)
        
        next_btn = QPushButton("下一步")
        next_btn.clicked.connect(next_step)
        layout.addWidget(next_btn)
        
        prev_btn = QPushButton("上一步")
        prev_btn.clicked.connect(prev_step)
        layout.addWidget(prev_btn)
        
        print("✅ 进度条组件创建成功")
        
        # 显示窗口
        window.show()
        
        print("🚀 进度条测试界面启动成功！")
        print("💡 测试功能:")
        print("   - ProgressBar: 显示进度百分比")
        print("   - StepProgress: 显示步骤进度")
        print("   - 点击按钮测试交互功能")
        
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

def main():
    """主函数"""
    print("=" * 60)
    print("🔄 进度条组件测试工具")
    print("=" * 60)
    
    # 测试进度条组件
    return test_progress_components()

if __name__ == "__main__":
    sys.exit(main())