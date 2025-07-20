#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏自动化工具 - 统一启动器
作为项目的单一入口点，负责环境设置和调用主程序
"""

import sys
import os


def setup_environment():
    """设置运行环境"""
    # 添加项目根目录到系统路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 验证项目结构
    src_path = os.path.join(project_root, 'src')
    if not os.path.exists(src_path):
        raise FileNotFoundError("项目结构不完整：src目录不存在")
    
    return project_root


def main():
    """统一启动器主函数"""
    try:
        # 设置环境
        project_root = setup_environment()
        
        # 导入并运行主程序
        from src.main import main as src_main
        
        # 调用实际的主程序，传递所有命令行参数
        return src_main()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("解决方案: pip install -r requirements.txt")
        return 1
        
    except FileNotFoundError as e:
        print(f"环境错误: {e}")
        print("请确保在正确的项目目录中运行此程序")
        return 1
        
    except Exception as e:
        print(f"启动失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
