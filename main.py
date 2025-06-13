#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏自动化工具 - 主启动器
此文件作为项目的统一入口点，调用src/main.py中的实际实现
"""

import sys
import os
import logging

def main():
    """主启动函数"""
    print("=" * 50)
    print("🎮 游戏自动化工具启动器")
    print("=" * 50)
    
    try:
        # 添加项目根目录到系统路径
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        print("📁 设置项目路径...")
        print(f"   项目根目录: {project_root}")
        
        # 检查src目录是否存在
        src_path = os.path.join(project_root, 'src')
        if not os.path.exists(src_path):
            print("❌ 错误：src目录不存在")
            print("   请确保项目结构完整")
            return 1
        
        print("🔧 导入主程序模块...")
        
        # 导入并运行src/main.py中的主程序
        from src.main import main as src_main
        
        print("🚀 启动主程序...")
        print("-" * 50)
        
        # 调用实际的主程序
        return src_main()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 可能的解决方案:")
        print("   1. 检查是否安装了所有依赖包")
        print("   2. 运行: pip install -r requirements.txt")
        print("   3. 检查Python版本是否符合要求")
        return 1
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # 设置基本日志配置
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行主程序
    exit_code = main()
    sys.exit(exit_code if exit_code is not None else 0)
