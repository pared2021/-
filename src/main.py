#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏自动化工具 - 统一主程序入口
自动检测环境并选择合适的主程序启动
"""

import sys
import os
import logging
import argparse
from typing import Optional

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/main.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """检查依赖是否满足"""
    missing_deps = []
    available_deps = {}
    
    # 检查PyQt6
    try:
        import PyQt6
        pyqt6_available = True
        available_deps['PyQt6'] = PyQt6.__version__ if hasattr(PyQt6, '__version__') else 'unknown'
    except ImportError:
        pyqt6_available = False
    
    # 检查PySide6  
    try:
        import PySide6
        pyside6_available = True
        available_deps['PySide6'] = PySide6.__version__ if hasattr(PySide6, '__version__') else 'unknown'
    except ImportError:
        pyside6_available = False
    
    # 至少需要一个GUI框架
    if not pyqt6_available and not pyside6_available:
        missing_deps.append("PyQt6 或 PySide6")
    
    # 检查桌面自动化核心依赖
    core_deps = {
        'numpy': 'numpy',
        'opencv-python': 'cv2', 
        'psutil': 'psutil',
        'pyautogui': 'pyautogui',
        'pywin32': 'win32gui',  # Windows依赖
        'loguru': 'loguru',
        'Pillow': 'PIL'
    }
    
    for package_name, import_name in core_deps.items():
        try:
            module = __import__(import_name)
            # 尝试获取版本信息
            version = getattr(module, '__version__', 'unknown')
            available_deps[package_name] = version
        except ImportError:
            missing_deps.append(package_name)
    
    # 检查AI相关依赖（可选）
    ai_deps = {
        'torch': 'torch',
        'torchvision': 'torchvision'
    }
    
    ai_missing = []
    for package_name, import_name in ai_deps.items():
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            available_deps[package_name] = version
        except ImportError:
            ai_missing.append(package_name)
    
    return {
        'pyqt6': pyqt6_available,
        'pyside6': pyside6_available,
        'missing': missing_deps,
        'ai_missing': ai_missing,
        'available': available_deps
    }

def install_missing_dependencies(missing_deps: list) -> bool:
    """自动安装缺失的依赖
    
    Args:
        missing_deps: 缺失的依赖列表
        
    Returns:
        bool: 是否安装成功
    """
    if not missing_deps:
        return True
    
    import subprocess
    
    print("🔧 检测到缺失依赖，尝试自动安装...")
    
    for dep in missing_deps:
        if dep == "PyQt6 或 PySide6":
            # 优先尝试安装PyQt6
            dep = "PyQt6"
        
        print(f"📦 安装 {dep}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ {dep} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {dep} 安装失败: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ 安装过程中发生错误: {e}")
            return False
    
    print("🎉 所有依赖安装完成，重新验证...")
    
    # 重新验证依赖
    new_deps = check_dependencies()
    if new_deps['missing']:
        print(f"⚠️  仍有未解决的依赖: {', '.join(new_deps['missing'])}")
        return False
    
    return True

def validate_dependency_compatibility() -> bool:
    """验证依赖版本兼容性
    
    Returns:
        bool: 依赖是否兼容
    """
    try:
        # 检查numpy版本
        import numpy as np
        numpy_version = tuple(map(int, np.__version__.split('.')[:2]))
        if numpy_version < (1, 20):
            print(f"⚠️  NumPy版本过低: {np.__version__} (建议 >= 1.20.0)")
            return False
        
        # 检查OpenCV版本
        try:
            import cv2
            opencv_version = tuple(map(int, cv2.__version__.split('.')[:2]))
            if opencv_version < (4, 5):
                print(f"⚠️  OpenCV版本过低: {cv2.__version__} (建议 >= 4.5.0)")
                return False
        except ImportError:
            pass
        
        # 检查PyQt6/PySide6版本
        try:
            import PyQt6
            # PyQt6版本检查
            pyqt6_version = getattr(PyQt6, '__version__', '0.0.0')
            print(f"📱 PyQt6版本: {pyqt6_version}")
        except ImportError:
            try:
                import PySide6
                pyside6_version = getattr(PySide6, '__version__', '0.0.0')
                print(f"📱 PySide6版本: {pyside6_version}")
            except ImportError:
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ 依赖兼容性检查失败: {e}")
        return False

def detect_display():
    """检测是否有显示器"""
    try:
        if os.name == 'nt':  # Windows
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            return True
        else:  # Linux/Mac
            return os.environ.get('DISPLAY') is not None
    except:
        return False

def start_gui_app(ui_framework: str = 'auto'):
    """启动GUI应用
    
    Args:
        ui_framework: UI框架选择 ('pyqt6', 'pyside6', 'auto')
    """
    deps = check_dependencies()
    
    # 自动选择UI框架
    if ui_framework == 'auto':
        if deps['pyqt6']:
            ui_framework = 'pyqt6'
        elif deps['pyside6']:
            ui_framework = 'pyside6'
        else:
            raise RuntimeError("没有可用的UI框架，请安装PyQt6或PySide6")
    
    print(f"📱 启动GUI应用 (使用 {ui_framework.upper()})")
    
    if ui_framework == 'pyqt6':
        # 使用PyQt6主窗口
        from src.gui.main_window import MainWindow
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec()
        
    elif ui_framework == 'pyside6':
        # 使用PySide6主窗口
        from src.services.main import MainWindow, main as services_main
        return services_main()
        
    else:
        raise ValueError(f"不支持的UI框架: {ui_framework}")

def start_cli_app():
    """启动命令行应用"""
    print("🖥️ 启动命令行模式")
    
    # 导入CLI模块
    try:
        from src.cli.main import CLIApp
        app = CLIApp()
        return app.run()
    except ImportError:
        print("❌ CLI模块未实现，使用基础CLI模式")
        return start_basic_cli()

def start_basic_cli():
    """启动基础CLI模式"""
    print("=" * 50)
    print("🎮 游戏自动化工具 - 命令行模式")
    print("=" * 50)
    
    # 基础功能检查
    deps = check_dependencies()
    print("📦 依赖检查:")
    print(f"  PyQt6: {'✅' if deps['pyqt6'] else '❌'}")
    print(f"  PySide6: {'✅' if deps['pyside6'] else '❌'}")
    
    if deps['missing']:
        print(f"  缺少依赖: {', '.join(deps['missing'])}")
        print("💡 请运行: pip install -r requirements.txt")
        return 1
    
    print("\n✅ 所有依赖已满足")
    print("💡 使用 --gui 参数启动图形界面")
    return 0

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="游戏自动化工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python -m src.main                    # 自动检测模式
  python -m src.main --gui              # 强制GUI模式
  python -m src.main --cli              # 强制CLI模式
  python -m src.main --gui --ui pyqt6   # 指定PyQt6
        """
    )
    
    parser.add_argument(
        '--gui', action='store_true',
        help='启动图形界面'
    )
    
    parser.add_argument(
        '--cli', action='store_true', 
        help='启动命令行界面'
    )
    
    parser.add_argument(
        '--ui', choices=['pyqt6', 'pyside6', 'auto'], default='auto',
        help='选择UI框架 (默认: auto)'
    )
    
    parser.add_argument(
        '--debug', action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--config', type=str, default='config',
        help='配置文件目录 (默认: config)'
    )
    
    return parser.parse_args()

def main():
    """主入口函数"""
    try:
        # 确保日志目录存在
        os.makedirs('logs', exist_ok=True)
        
        # 设置日志
        setup_logging()
        logger = logging.getLogger(__name__)
        
        print("=" * 60)
        print("🎮 游戏自动化工具启动中...")
        print("=" * 60)
        
        # 解析命令行参数
        args = parse_arguments()
        
        # 设置调试模式
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("调试模式已启用")
        
        # 检查依赖
        deps = check_dependencies()
        logger.info(f"依赖检查完成: PyQt6={deps['pyqt6']}, PySide6={deps['pyside6']}")
        
        # 显示可用依赖信息
        if deps['available']:
            print("📦 已安装的依赖:")
            for name, version in deps['available'].items():
                print(f"  ✅ {name}: {version}")
        
        # 处理缺失的核心依赖
        if deps['missing']:
            logger.error(f"缺少依赖: {', '.join(deps['missing'])}")
            print(f"❌ 缺少核心依赖: {', '.join(deps['missing'])}")
            
            # 尝试自动安装
            try:
                if install_missing_dependencies(deps['missing']):
                    print("✅ 依赖安装成功，继续启动")
                else:
                    print("❌ 依赖安装失败")
                    print("💡 请手动运行: pip install -r requirements.txt")
                    return 1
            except Exception as e:
                logger.error(f"自动安装依赖失败: {e}")
                print("💡 请手动运行: pip install -r requirements.txt")
                return 1
        
        # 处理AI依赖（可选）
        if deps['ai_missing']:
            print(f"⚠️  AI功能依赖缺失: {', '.join(deps['ai_missing'])}")
            print("💡 如需AI功能，请安装: pip install torch torchvision")
        
        # 验证依赖兼容性
        if not validate_dependency_compatibility():
            logger.warning("依赖版本兼容性检查未通过，可能影响功能")
            print("⚠️  某些依赖版本可能过低，建议更新")
        else:
            print("✅ 依赖兼容性检查通过")
        
        # 决定启动模式
        if args.cli:
            # 强制CLI模式
            return start_cli_app()
        elif args.gui:
            # 强制GUI模式
            return start_gui_app(args.ui)
        else:
            # 自动检测模式
            has_display = detect_display()
            logger.info(f"显示器检测: {has_display}")
            
            if has_display and (deps['pyqt6'] or deps['pyside6']):
                print("🖥️ 检测到显示器，启动图形界面")
                return start_gui_app(args.ui)
            else:
                print("📟 未检测到显示器或GUI框架，启动命令行模式")
                return start_cli_app()
                
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
        return 0
    except Exception as e:
        logger.error(f"程序启动失败: {e}", exc_info=True)
        print(f"❌ 程序启动失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 