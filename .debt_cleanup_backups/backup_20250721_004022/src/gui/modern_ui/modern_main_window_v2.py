"""现代化主窗口 v2.0

基于新组件系统的重新设计版本
"""

import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMenuBar, QToolBar, QDockWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from components import (
    BaseComponent, VBox, HBox, Grid, Card, Button, IconButton,
    Typography, Heading, Body, Caption, Icon, MaterialIcon,
    ProgressBar, Input, SearchInput
)
from design_tokens import design_tokens, ComponentSize
from style_generator import StyleGenerator


class ModernHeaderBar(BaseComponent):
    """现代化头部栏"""
    
    # 信号
    menu_clicked = pyqtSignal()
    search_changed = pyqtSignal(str)
    profile_clicked = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(ComponentSize.LARGE, parent=parent)
        
        # 组件
        self._layout: Optional[QHBoxLayout] = None
        self._logo: Optional[Icon] = None
        self._title: Optional[Heading] = None
        self._search: Optional[SearchInput] = None
        self._actions: Optional[HBox] = None
        self._profile: Optional[IconButton] = None
    
    def setup_ui(self):
        """设置UI"""
        # 主布局
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(16, 8, 16, 8)
        self._layout.setSpacing(16)
        
        # Logo和标题区域
        logo_area = HBox(parent=self)
        logo_area.set_spacing(12)
        
        self._logo = MaterialIcon("games", icon_size=32, color="text.primary", parent=self)
        self._title = Heading("游戏自动化工具", level=3, parent=self)
        
        logo_area.add_widget(self._logo)
        logo_area.add_widget(self._title)
        logo_area.add_stretch()
        
        # 搜索区域
        self._search = SearchInput(
            placeholder="搜索功能...",
            size=ComponentSize.MEDIUM,
            parent=self
        )
        self._search.setFixedWidth(300)
        
        # 操作区域
        self._actions = HBox(parent=self)
        self._actions.set_spacing(8)
        
        # 通知按钮
        notifications_btn = IconButton(
            MaterialIcon("notifications", icon_size=20),
            size=ComponentSize.MEDIUM,
            parent=self
        )
        
        # 设置按钮
        settings_btn = IconButton(
            MaterialIcon("settings", icon_size=20),
            size=ComponentSize.MEDIUM,
            parent=self
        )
        
        # 用户头像
        self._profile = IconButton(
            MaterialIcon("account_circle", icon_size=24),
            size=ComponentSize.MEDIUM,
            parent=self
        )
        
        self._actions.add_widget(notifications_btn)
        self._actions.add_widget(settings_btn)
        self._actions.add_widget(self._profile)
        
        # 添加到主布局
        self._layout.addWidget(logo_area)
        self._layout.addStretch()
        self._layout.addWidget(self._search)
        self._layout.addStretch()
        self._layout.addWidget(self._actions)
    
    def setup_connections(self):
        """设置信号连接"""
        if self._search:
            self._search.text_changed.connect(self.search_changed.emit)
        
        if self._profile:
            self._profile.clicked.connect(self.profile_clicked.emit)
    
    def update_style(self):
        """更新样式"""
        surface_color = design_tokens.get_color('surface', 'default')
        border_color = design_tokens.get_color('border', 'default')
        
        style = f"""
        ModernHeaderBar {{
            background-color: {surface_color};
            border-bottom: 1px solid {border_color};
        }}
        """
        
        self.setStyleSheet(style)


class ModernSidebar(BaseComponent):
    """现代化侧边栏"""
    
    # 信号
    item_selected = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(ComponentSize.LARGE, parent=parent)
        
        # 组件
        self._layout: Optional[QVBoxLayout] = None
        self._nav_items: list = []
        self._selected_item: Optional[str] = None
    
    def setup_ui(self):
        """设置UI"""
        # 主布局
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 16, 8, 16)
        self._layout.setSpacing(8)
        
        # 导航项目
        nav_items = [
            {"id": "dashboard", "icon": "dashboard", "text": "仪表板"},
            {"id": "automation", "icon": "smart_toy", "text": "自动化"},
            {"id": "windows", "icon": "window", "text": "窗口管理"},
            {"id": "scripts", "icon": "code", "text": "脚本管理"},
            {"id": "logs", "icon": "article", "text": "日志查看"},
            {"id": "settings", "icon": "settings", "text": "设置"},
        ]
        
        for item in nav_items:
            nav_button = self._create_nav_item(item)
            self._nav_items.append(nav_button)
            self._layout.addWidget(nav_button)
        
        # 添加弹性空间
        self._layout.addStretch()
        
        # 底部信息
        info_card = Card(
            variant="outlined",
            size=ComponentSize.SMALL,
            parent=self
        )
        
        info_layout = VBox(parent=info_card)
        info_layout.add_widget(Caption("版本信息", parent=info_card))
        info_layout.add_widget(Body("v2.0.0", size="small", parent=info_card))
        
        self._layout.addWidget(info_card)
    
    def _create_nav_item(self, item_data: dict) -> Button:
        """创建导航项"""
        button = Button(
            text=item_data["text"],
            variant="ghost",
            size=ComponentSize.MEDIUM,
            full_width=True,
            parent=self
        )
        
        # 添加图标
        icon = MaterialIcon(item_data["icon"], icon_size=20, parent=button)
        # 注意：这里需要在Button组件中添加图标支持
        
        # 连接点击事件
        button.clicked.connect(lambda: self._handle_nav_click(item_data["id"]))
        
        return button
    
    def _handle_nav_click(self, item_id: str):
        """处理导航点击"""
        # 更新选中状态
        if self._selected_item != item_id:
            self._selected_item = item_id
            self._update_selection()
            self.item_selected.emit(item_id)
    
    def _update_selection(self):
        """更新选中状态"""
        # 这里可以更新按钮的视觉状态
        pass
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_style(self):
        """更新样式"""
        surface_color = design_tokens.get_color('surface', 'default')
        border_color = design_tokens.get_color('border', 'default')
        
        style = f"""
        ModernSidebar {{
            background-color: {surface_color};
            border-right: 1px solid {border_color};
        }}
        """
        
        self.setStyleSheet(style)


class ModernDashboard(BaseComponent):
    """现代化仪表板"""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(ComponentSize.LARGE, parent=parent)
        
        # 组件
        self._layout: Optional[QVBoxLayout] = None
        self._stats_grid: Optional[Grid] = None
        self._content_area: Optional[VBox] = None
    
    def setup_ui(self):
        """设置UI"""
        # 主布局
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(24)
        
        # 页面标题
        title = Heading("仪表板", level=2, parent=self)
        subtitle = Body("游戏自动化工具概览", color="text.secondary", parent=self)
        
        self._layout.addWidget(title)
        self._layout.addWidget(subtitle)
        
        # 统计卡片网格
        self._stats_grid = Grid(columns=4, parent=self)
        self._stats_grid.set_spacing(16)
        
        # 创建统计卡片
        stats_data = [
            {"title": "活跃窗口", "value": "3", "icon": "window", "color": "semantic.info"},
            {"title": "运行脚本", "value": "2", "icon": "play_arrow", "color": "semantic.success"},
            {"title": "今日操作", "value": "156", "icon": "touch_app", "color": "semantic.warning"},
            {"title": "错误次数", "value": "0", "icon": "error", "color": "semantic.error"},
        ]
        
        for i, stat in enumerate(stats_data):
            card = self._create_stat_card(stat)
            self._stats_grid.add_widget(card, row=0, col=i)
        
        self._layout.addWidget(self._stats_grid)
        
        # 内容区域
        self._content_area = VBox(parent=self)
        self._content_area.set_spacing(16)
        
        # 快速操作卡片
        quick_actions_card = Card(
            title="快速操作",
            variant="elevated",
            size=ComponentSize.LARGE,
            parent=self
        )
        
        actions_layout = HBox(parent=quick_actions_card)
        actions_layout.set_spacing(12)
        
        # 添加快速操作按钮
        actions = [
            {"text": "启动自动化", "icon": "play_arrow", "variant": "primary"},
            {"text": "窗口检测", "icon": "search", "variant": "secondary"},
            {"text": "脚本编辑", "icon": "edit", "variant": "outline"},
            {"text": "查看日志", "icon": "article", "variant": "ghost"},
        ]
        
        for action in actions:
            btn = Button(
                text=action["text"],
                variant=action["variant"],
                size=ComponentSize.MEDIUM,
                parent=quick_actions_card
            )
            actions_layout.add_widget(btn)
        
        actions_layout.add_stretch()
        
        self._content_area.add_widget(quick_actions_card)
        
        # 最近活动卡片
        activity_card = Card(
            title="最近活动",
            variant="elevated",
            size=ComponentSize.LARGE,
            parent=self
        )
        
        activity_layout = VBox(parent=activity_card)
        
        # 添加活动项目
        activities = [
            "自动化脚本 'game_bot.py' 已启动",
            "检测到新窗口: 'Game Window'",
            "执行点击操作 (x: 100, y: 200)",
            "脚本执行完成，耗时 2.3 秒",
        ]
        
        for activity in activities:
            activity_item = HBox(parent=activity_card)
            activity_item.add_widget(MaterialIcon("circle", icon_size=8, color="semantic.info"))
            activity_item.add_widget(Body(activity, size="small"))
            activity_item.add_stretch()
            activity_item.add_widget(Caption("刚刚", color="text.secondary"))
            
            activity_layout.add_widget(activity_item)
        
        self._content_area.add_widget(activity_card)
        
        self._layout.addWidget(self._content_area)
        self._layout.addStretch()
    
    def _create_stat_card(self, stat_data: dict) -> Card:
        """创建统计卡片"""
        card = Card(
            variant="elevated",
            size=ComponentSize.MEDIUM,
            parent=self
        )
        
        layout = VBox(parent=card)
        layout.set_spacing(8)
        
        # 图标和数值行
        header = HBox(parent=card)
        header.add_widget(MaterialIcon(
            stat_data["icon"],
            size=24,
            color=stat_data["color"]
        ))
        header.add_stretch()
        header.add_widget(Heading(
            stat_data["value"],
            level=3,
            color=stat_data["color"]
        ))
        
        layout.add_widget(header)
        layout.add_widget(Body(stat_data["title"], color="text.secondary"))
        
        return card
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def update_style(self):
        """更新样式"""
        background_color = design_tokens.get_color('background', 'default')
        
        style = f"""
        ModernDashboard {{
            background-color: {background_color};
        }}
        """
        
        self.setStyleSheet(style)


class ModernMainWindowV2(QMainWindow):
    """现代化主窗口 v2.0"""
    
    def __init__(self):
        super().__init__()
        
        # 组件
        self._central_widget: Optional[QWidget] = None
        self._main_layout: Optional[QVBoxLayout] = None
        self._header: Optional[ModernHeaderBar] = None
        self._content_splitter: Optional[QSplitter] = None
        self._sidebar: Optional[ModernSidebar] = None
        self._content_area: Optional[QWidget] = None
        self._dashboard: Optional[ModernDashboard] = None
        
        # 样式生成器
        self._style_generator = StyleGenerator()
        
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()
    
    def setup_ui(self):
        """设置UI"""
        # 窗口设置
        self.setWindowTitle("游戏自动化工具 v2.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 中央组件
        self._central_widget = QWidget()
        self.setCentralWidget(self._central_widget)
        
        # 主布局
        self._main_layout = QVBoxLayout(self._central_widget)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        
        # 头部栏
        self._header = ModernHeaderBar(parent=self._central_widget)
        self._main_layout.addWidget(self._header)
        
        # 内容分割器
        self._content_splitter = QSplitter(Qt.Orientation.Horizontal, self._central_widget)
        
        # 侧边栏
        self._sidebar = ModernSidebar(parent=self._content_splitter)
        self._sidebar.setFixedWidth(250)
        self._content_splitter.addWidget(self._sidebar)
        
        # 内容区域
        self._content_area = QWidget(self._content_splitter)
        self._content_splitter.addWidget(self._content_area)
        
        # 设置分割器比例
        self._content_splitter.setSizes([250, 1150])
        self._content_splitter.setCollapsible(0, False)  # 侧边栏不可折叠
        
        self._main_layout.addWidget(self._content_splitter)
        
        # 默认显示仪表板
        self.show_dashboard()
    
    def setup_connections(self):
        """设置信号连接"""
        if self._sidebar:
            self._sidebar.item_selected.connect(self.handle_navigation)
        
        if self._header:
            self._header.search_changed.connect(self.handle_search)
            self._header.profile_clicked.connect(self.handle_profile_click)
    
    def apply_theme(self):
        """应用主题"""
        # 应用全局样式
        global_style = self._style_generator.generate_global_style()
        self.setStyleSheet(global_style)
    
    def show_dashboard(self):
        """显示仪表板"""
        # 清除现有内容
        if self._content_area.layout():
            while self._content_area.layout().count():
                child = self._content_area.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            layout = QVBoxLayout(self._content_area)
            layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建仪表板
        self._dashboard = ModernDashboard(parent=self._content_area)
        self._content_area.layout().addWidget(self._dashboard)
    
    def handle_navigation(self, item_id: str):
        """处理导航"""
        if item_id == "dashboard":
            self.show_dashboard()
        elif item_id == "automation":
            self.show_automation_page()
        elif item_id == "windows":
            self.show_windows_page()
        elif item_id == "scripts":
            self.show_scripts_page()
        elif item_id == "logs":
            self.show_logs_page()
        elif item_id == "settings":
            self.show_settings_page()
    
    def show_automation_page(self):
        """显示自动化页面"""
        # TODO: 实现自动化页面
        pass
    
    def show_windows_page(self):
        """显示窗口管理页面"""
        # TODO: 实现窗口管理页面
        pass
    
    def show_scripts_page(self):
        """显示脚本管理页面"""
        # TODO: 实现脚本管理页面
        pass
    
    def show_logs_page(self):
        """显示日志页面"""
        # TODO: 实现日志页面
        pass
    
    def show_settings_page(self):
        """显示设置页面"""
        # TODO: 实现设置页面
        pass
    
    def handle_search(self, query: str):
        """处理搜索"""
        # TODO: 实现搜索功能
        print(f"搜索: {query}")
    
    def handle_profile_click(self):
        """处理用户头像点击"""
        # TODO: 实现用户菜单
        print("用户菜单点击")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("游戏自动化工具")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Modern UI")
    
    # 创建主窗口
    window = ModernMainWindowV2()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()