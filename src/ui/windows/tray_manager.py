from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
import os

class TrayManager(QSystemTrayIcon):
    """托盘图标管理器"""
    
    # 定义信号
    show_window = pyqtSignal()  # 显示窗口信号
    start_automation = pyqtSignal()  # 开始自动化信号
    stop_automation = pyqtSignal()  # 停止自动化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取图标路径
        icon_path = os.path.join("resources", "icons", "window.png")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            # 如果图标文件不存在，使用系统默认图标
            self.setIcon(QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon))
            
        self.setToolTip("游戏自动化工具")
        self._setup_menu()
        self.activated.connect(self._on_activated)
        
        # 确保托盘图标可见
        self.show()
        
    def _setup_menu(self):
        """设置托盘菜单"""
        menu = QMenu()
        
        # 添加菜单项
        self.show_action = menu.addAction("显示主窗口")
        self.show_action.triggered.connect(self.show_window.emit)
        
        menu.addSeparator()
        
        self.start_action = menu.addAction("开始自动化")
        self.start_action.triggered.connect(self.start_automation.emit)
        
        self.stop_action = menu.addAction("停止自动化")
        self.stop_action.triggered.connect(self.stop_automation.emit)
        self.stop_action.setEnabled(False)
        
        menu.addSeparator()
        
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(QApplication.instance().quit)
        
        self.setContextMenu(menu)
    
    def _on_activated(self, reason):
        """托盘图标被激活时的处理"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window.emit()
    
    def update_automation_status(self, is_running: bool):
        """更新自动化状态
        
        Args:
            is_running: 是否正在运行
        """
        self.start_action.setEnabled(not is_running)
        self.stop_action.setEnabled(is_running)
        
        if is_running:
            self.setToolTip("游戏自动化工具 (运行中)")
        else:
            self.setToolTip("游戏自动化工具") 