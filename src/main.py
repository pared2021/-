import sys
import os
import atexit
import logging
from typing import Optional

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 首先导入并设置环境
from src.common.app_utils import setup_environment
print("设置应用程序环境...")
setup_environment()

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.views.main_window import MainWindow
from src.common.containers import Container
from src.common.system_initializer import initialize_container
from src.common.app_utils import set_app_style
from src.common.system_cleanup import cleanup

# 全局容器实例
container: Optional[Container] = None

def main():
    """程序入口"""
    global container
    
    print("初始化依赖注入容器...")
    try:
        # 初始化依赖注入容器
        container = initialize_container()
        if not container:
            print("程序初始化失败: 容器为空")
            return
        
        # 从容器获取服务
        print("获取服务...")
        config = container.config()
        logger = container.logger()
        
        # 设置日志级别为DEBUG以获取更多信息
        logger.set_level(logging.DEBUG)
        
        window_manager = container.window_manager()
        image_processor = container.image_processor()
        game_analyzer = container.game_analyzer()
        action_simulator = container.action_simulator()
        game_state = container.game_state()
        auto_operator = container.auto_operator()
        
        print("所有服务初始化成功")
        logger.info("程序启动")
        
        # 注册退出时清理资源
        atexit.register(cleanup, container)
        
        # 创建Qt应用
        print("创建Qt应用...")
        app = QApplication(sys.argv)
        
        # 设置应用样式
        print("设置应用样式...")
        set_app_style(app)
        
        # 创建主窗口，传入所有必要的服务
        print("创建主窗口...")
        window = MainWindow(
            logger=logger,
            window_manager=window_manager,
            game_analyzer=game_analyzer,
            auto_operator=auto_operator,
            image_processor=image_processor,
            action_simulator=action_simulator,
            game_state=game_state,
            config=config
        )
        
        # 显示主窗口
        print("显示主窗口...")
        window.show()
        window.activateWindow()
        window.raise_()
        
        # 运行应用
        print("启动应用事件循环...")
        sys.exit(app.exec())
    
    except Exception as e:
        print(f"程序启动异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()