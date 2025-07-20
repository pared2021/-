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

# 配置系统导入
from .common.app_config import init_application_metadata, setup_application_properties
from .services.config import config, get_config

def safe_print(message, fallback_prefix=""):
    """安全的print函数，处理Unicode编码问题"""
    try:
        print(message)
    except UnicodeEncodeError:
        # 移除emoji字符，使用简化版本
        import re
        # 移除emoji和特殊Unicode字符
        safe_message = re.sub(r'[^\x00-\x7F]+', fallback_prefix, message)
        print(safe_message)

def setup_logging():
    """设置日志配置 - 使用统一配置系统"""
    try:
        # 获取日志配置
        log_config = config.get_logging_config()
        log_level = getattr(logging, log_config.get('level', 'INFO').upper())
        log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file = log_config.get('file', 'logs/main.log')
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # 设置日志处理器
        handlers = []
        
        # 文件处理器
        if log_config.get('enable_file', True):
            handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
        
        # 控制台处理器
        if log_config.get('enable_console', True):
            handlers.append(logging.StreamHandler(sys.stdout))
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=handlers,
            force=True  # 重新配置已存在的logger
        )
        
    except Exception as e:
        # 降级到默认日志配置
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/main.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.getLogger(__name__).warning(f"使用默认日志配置，配置加载失败: {e}")

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
        missing_deps.append("PyQt6")
    
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
        
        # 检查PyQt6版本
        try:
            import PyQt6
            pyqt6_version = getattr(PyQt6, '__version__', '0.0.0')
            print(f"📱 PyQt6版本: {pyqt6_version}")
        except ImportError:
            print("❌ PyQt6未安装")
        
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

def start_gui_app():
    """启动传统GUI应用 - 统一使用PyQt6，集成配置系统和Clean Architecture"""
    deps = check_dependencies()
    
    if not deps['pyqt6']:
        raise RuntimeError("缺少PyQt6依赖，请运行: pip install PyQt6")
    
    print("📱 启动传统GUI应用 (PyQt6)")
    
    # 导入PyQt6
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QCoreApplication
    from .gui.main_window import MainWindow
    
    # 导入Clean Architecture组件
    from .application.containers.main_container import MainContainer

def start_modern_gui_app():
    """启动现代化GUI应用 - 基于游戏界面设计"""
    deps = check_dependencies()
    
    if not deps['pyqt6']:
        raise RuntimeError("缺少PyQt6依赖，请运行: pip install PyQt6")
    
    print("🎮 启动现代化GUI应用 (PyQt6 + 游戏风格UI)")
    
    # 导入PyQt6
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QCoreApplication
    from .gui.modern_ui.modern_main_window import ModernMainWindow
    
    # 导入Clean Architecture组件
    from .application.containers.main_container import MainContainer
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    try:
        # 初始化应用元数据（必须在QApplication创建后）
        init_application_metadata()
        
        # 获取应用配置
        app_config = config.get_application_config()
        
        # 设置应用属性
        setup_application_properties(
            window_title=app_config.get('window_title', '游戏自动操作工具 - 现代化界面'),
            window_size=tuple(app_config.get('window_size', [1600, 1000])),
            theme=app_config.get('theme', 'modern')
        )
        
        # 设置应用信息（用于关于对话框等，兼容性检查）
        try:
            QCoreApplication.setApplicationDisplayName(app_config.get('window_title', '游戏自动操作工具 - 现代化界面'))
        except AttributeError:
            # 某些PyQt6版本可能不支持此方法
            pass
        
        print(f"🏷️ 应用名称: {QCoreApplication.applicationName()}")
        print(f"🏢 组织名称: {QCoreApplication.organizationName()}")
        print(f"📌 版本: {QCoreApplication.applicationVersion()}")
        
    except Exception as e:
        logging.getLogger(__name__).warning(f"应用配置初始化失败，使用默认设置: {e}")
    
    # 注册模块别名（在容器初始化前）
    try:
        from .common.module_manager import get_module_manager
        manager = get_module_manager()
        if manager.is_initialized():
            print("📋 模块别名已通过配置文件注册")
        else:
            print("⚠️  模块管理器未初始化，跳过别名注册")
    except Exception as e:
        logging.getLogger(__name__).warning(f"模块别名注册失败: {e}")
    
    # 初始化依赖注入容器
    print("🔧 初始化依赖注入容器...")
    container = MainContainer()
    
    # 创建并显示现代化主窗口，注入依赖
    window = ModernMainWindow(container)
    window.show()
    
    return app.exec()

def start_cli_app():
    """启动命令行应用"""
    print("🖥️ 启动命令行模式")
    
    # 导入CLI模块
    try:
        from .cli.main import CLIApp
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
  python main.py                       # 自动检测模式（默认现代化界面）
  python main.py --gui                 # 启动传统图形界面
  python main.py --modern-gui          # 启动现代化图形界面
  python main.py --cli                 # 启动命令行界面
  python main.py --debug               # 调试模式
  python main.py --config-info         # 显示配置信息
  python main.py --config-export config.json  # 导出配置
        """
    )
    
    parser.add_argument(
        '--gui', action='store_true',
        help='启动图形界面（传统UI）'
    )
    
    parser.add_argument(
        '--modern-gui', action='store_true',
        help='启动现代化图形界面'
    )
    
    parser.add_argument(
        '--cli', action='store_true', 
        help='启动命令行界面'
    )
    
    parser.add_argument(
        '--debug', action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--config-info', action='store_true',
        help='显示配置系统信息'
    )
    
    parser.add_argument(
        '--config-export', type=str, metavar='FILE',
        help='导出配置到指定文件'
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
        
        # 获取应用信息
        try:
            app_config = config.get_application_config()
            app_name = app_config.get('window_title', '游戏自动化工具')
            app_version = app_config.get('version', '1.0.0')
        except:
            app_name = "游戏自动化工具"
            app_version = "1.0.0"
        
        print("=" * 60)
        try:
            print(f"🎮 {app_name} v{app_version} 启动中...")
        except UnicodeEncodeError:
            print(f"[GAME] {app_name} v{app_version} 启动中...")
        print("=" * 60)
        
        # 解析命令行参数
        args = parse_arguments()
        
        # 设置调试模式
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("调试模式已启用")
        
        # 处理配置相关命令
        if args.config_info:
            print("📊 配置系统信息:")
            storage_info = config.get_storage_info()
            for key, value in storage_info.items():
                print(f"  {key}: {value}")
            return 0
        
        if args.config_export:
            print(f"📤 导出配置到: {args.config_export}")
            if config.export_to_json(args.config_export):
                print("✅ 配置导出成功")
                return 0
            else:
                print("❌ 配置导出失败")
                return 1
        
        # 检查依赖
        deps = check_dependencies()
        logger.info(f"依赖检查完成: PyQt6={deps['pyqt6']}")
        
        # 初始化智能模块管理器
        try:
            from .common.module_manager import initialize_module_manager
            print("🔧 初始化智能模块管理器...")
            module_manager = initialize_module_manager()
            logger.info("智能模块管理器初始化成功")
            print("✅ 智能模块管理器已启动")
        except Exception as e:
            logger.warning(f"智能模块管理器初始化失败，使用传统导入方式: {e}")
            print(f"⚠️  模块管理器初始化失败: {e}")
        
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
        elif args.modern_gui:
            # 强制现代化GUI模式
            return start_modern_gui_app()
        elif args.gui:
            # 强制传统GUI模式
            return start_gui_app()
        else:
            # 自动检测模式
            has_display = detect_display()
            logger.info(f"显示器检测: {has_display}")
            
            if has_display and deps['pyqt6']:
                print("🖥️ 检测到显示器，启动现代化图形界面")
                print("💡 使用 --gui 启动传统界面，--modern-gui 启动现代化界面")
                return start_modern_gui_app()
            else:
                print("📟 未检测到显示器或GUI框架，启动命令行模式")
                return start_cli_app()
                
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
        return 0
    except Exception as e:
        logger.error(f"程序启动失败: {e}", exc_info=True)
        safe_print(f"❌ 程序启动失败: {e}", "[ERROR] ")
        return 1

if __name__ == "__main__":
    sys.exit(main())