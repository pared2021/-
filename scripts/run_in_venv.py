#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动启动程序并确保在虚拟环境中运行
"""

import os
import sys
import subprocess
import venv
import site
import platform

def is_venv():
    """检查当前是否在虚拟环境中运行"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def create_venv_if_not_exists(venv_path):
    """如果虚拟环境不存在，则创建"""
    if not os.path.exists(venv_path):
        print(f"正在创建虚拟环境: {venv_path}")
        venv.create(venv_path, with_pip=True)
        return True
    return False

def get_venv_python(venv_path):
    """获取虚拟环境中Python解释器的路径"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "python.exe")
    return os.path.join(venv_path, "bin", "python")

def install_requirements(venv_python, requirements_file="requirements.txt"):
    """安装项目依赖"""
    if os.path.exists(requirements_file):
        print(f"正在安装项目依赖...")
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", requirements_file])
    else:
        print(f"警告: 依赖文件 {requirements_file} 不存在")

def run_in_venv():
    """确保在虚拟环境中运行程序"""
    # 设置虚拟环境路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(current_dir, "venv")
    
    # 检查是否在虚拟环境中
    if not is_venv():
        print("未在虚拟环境中运行，正在设置虚拟环境...")
        
        # 创建虚拟环境（如果不存在）
        newly_created = create_venv_if_not_exists(venv_path)
        
        # 获取虚拟环境中Python解释器的路径
        venv_python = get_venv_python(venv_path)
        
        # 如果是新创建的虚拟环境，安装依赖
        if newly_created:
            install_requirements(venv_python)
        
        # 使用虚拟环境中的Python重新运行此脚本
        print("正在启动虚拟环境中的程序...")
        os.execl(venv_python, venv_python, __file__)
    else:
        # 已经在虚拟环境中，启动主程序
        print("已在虚拟环境中运行")
        
        # 导入统一启动器并运行
        try:
            # 添加项目根目录到Python路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            # 直接运行统一启动器
            import importlib.util
            spec = importlib.util.spec_from_file_location("main", os.path.join(current_dir, "main.py"))
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            main_module.main()
        except ImportError as e:
            print(f"导入统一启动器失败: {e}")
            print("请确保已安装所有依赖项")
            sys.exit(1)

if __name__ == "__main__":
    run_in_venv() 