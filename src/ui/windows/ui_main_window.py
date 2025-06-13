"""
主窗口模块
"""
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from qframelesswindow import FramelessWindow
from qfluentwidgets import (
    PushButton,
    ToggleButton,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    setTheme,
    Theme,
    FluentWindow,
    NavigationInterface,
    isDarkTheme,
)
from .pages import AutomationPage, SettingsPage


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口属性
        self.setWindowTitle("游戏自动化工具")
        self.resize(900, 650)

        # 初始化UI
        self._init_ui()

        # 设置深色主题
        setTheme(Theme.DARK)

    def _init_ui(self):
        """初始化UI"""
        # 创建页面
        self.automation_page = AutomationPage(self)
        self.settings_page = SettingsPage(self)

        # 添加页面到堆栈
        self.add_sub_interface(self.automation_page, FluentIcon.GAME, "自动化")
        self.add_sub_interface(self.settings_page, FluentIcon.SETTING, "设置")

        # 设置导航界面
        self.navigation_interface.setExpandWidth(200)
        self.navigation_interface.setRetractWidth(48)

    def show_info(self, title: str, content: str, success: bool = True):
        """显示信息提示"""
        InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        ) if success else InfoBar.error(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self,
        )
