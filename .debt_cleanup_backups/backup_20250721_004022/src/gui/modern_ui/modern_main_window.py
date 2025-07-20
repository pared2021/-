"""现代化主窗口 - 基于游戏界面设计"""

import sys
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QFrame, QLabel, QPushButton, QStatusBar, QToolBar, QDockWidget,
    QApplication, QGraphicsDropShadowEffect, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QEvent, QPoint
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QLinearGradient, QMouseEvent

from .modern_styles import MODERN_APP_STYLE, GAME_THEME_COLORS, LAYOUT_CONSTANTS
from .modern_widgets import ModernControlPanel, ModernGameView, ModernStatusPanel
from ...core.interfaces.adapters import IWindowAdapter
from ...services.logger import GameLogger


class ModernMainWindow(QMainWindow):
    """现代化主窗口类"""
    
    # 信号定义
    window_selected = pyqtSignal(str)
    automation_started = pyqtSignal()
    automation_stopped = pyqtSignal()
    
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        from ...services.config import Config
        config = Config()
        self.logger = GameLogger(config, "ModernMainWindow")
        
        # 组件引用
        self.control_panel: Optional[ModernControlPanel] = None
        self.game_view: Optional[ModernGameView] = None
        self.status_panel: Optional[ModernStatusPanel] = None
        self.window_adapter: Optional[IWindowAdapter] = None
        self.title_bar: Optional[QFrame] = None
        
        # 拖拽相关
        self.drag_position = None
        
        # 定时器
        self.capture_timer = QTimer()
        self.monitor_timer = QTimer()
        
        # 动画
        self.animations = []
        
        self._init_services()
        self._init_ui()
        self._setup_animations()
        self._connect_signals()
        self._start_timers()
        
    def _init_services(self):
        """初始化服务"""
        if self.container:
            try:
                # 使用dependency-injector的方式获取服务
                self.window_adapter = self.container.window_adapter()
            except Exception as e:
                self.logger.error(f"Failed to get window_adapter: {e}")
                
    def _init_ui(self):
        """初始化现代化UI"""
        self.setWindowTitle("游戏自动化工具 - 现代化界面")
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)
        
        # 应用现代化样式
        self.setStyleSheet(MODERN_APP_STYLE)
        
        # 设置窗口属性 - 完全移除系统标题栏
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        # Windows特定设置 - 确保完全移除标题栏
        import platform
        if platform.system() == "Windows":
            import ctypes
            from ctypes import wintypes
            # 获取窗口句柄
            hwnd = int(self.winId())
            # 移除窗口标题栏和边框
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -16)  # GWL_STYLE
            style &= ~0x00C00000  # 移除 WS_CAPTION
            style &= ~0x00800000  # 移除 WS_BORDER
            style &= ~0x00400000  # 移除 WS_DLGFRAME
            ctypes.windll.user32.SetWindowLongW(hwnd, -16, style)
            # 刷新窗口
            ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0027)
        
        # 创建中央部件
        self._create_central_widget()
        
        # 创建工具栏
        self._create_modern_toolbar()
        
        # 创建状态栏
        self._create_modern_statusbar()
        
        # 添加阴影效果
        self._add_shadow_effects()
        
    def _create_central_widget(self):
        """创建中央部件"""
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 4)  # 顶部边距为0，让标题栏贴到最顶部
        main_layout.setSpacing(0)
        
        # 创建合并的标题栏（包含窗口控制按钮）
        self.title_bar = self._create_unified_title_bar()
        main_layout.addWidget(self.title_bar)
        
        # 创建内容区域
        content_splitter = self._create_content_area()
        main_layout.addWidget(content_splitter, 1)
        
    def _create_unified_title_bar(self) -> QFrame:
        """创建统一的标题栏（包含标题和窗口控制按钮）"""
        title_bar = QFrame()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet("""
            QFrame#titleBar {
                background: rgba(26, 26, 46, 1.0);
                border: none;
                border-bottom: 1px solid rgba(74, 144, 226, 0.3);
                padding: 0px;
                margin: 0px;
            }
        """)
        
        # 安装事件过滤器以处理拖拽
        title_bar.installEventFilter(self)
        
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(8, 6, 8, 6)
        
        # 应用图标和标题
        icon_label = QLabel("🎮")
        icon_label.setFont(QFont("Arial", 20))
        layout.addWidget(icon_label)
        
        title_label = QLabel("游戏自动化工具")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff; margin-left: 10px;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # 窗口控制按钮
        self._create_window_controls(layout)
        
        return title_bar
        

        
    def _create_window_controls(self, layout: QHBoxLayout):
        """创建窗口控制按钮卡片"""
        # 创建窗口控制卡片容器
        controls_card = QFrame()
        controls_card.setObjectName("windowControlsCard")
        controls_card.setStyleSheet("""
            QFrame#windowControlsCard {
                background: rgba(26, 26, 46, 0.9);
                border: 1px solid rgba(74, 144, 226, 0.4);
                border-radius: 18px;
                padding: 4px;
                margin: 2px;
            }
            QFrame#windowControlsCard:hover {
                border-color: rgba(74, 144, 226, 0.6);
                background: rgba(26, 26, 46, 0.95);
            }
        """)
        
        # 卡片内部布局
        controls_layout = QHBoxLayout(controls_card)
        controls_layout.setContentsMargins(6, 4, 6, 4)
        controls_layout.setSpacing(4)
        
        # 最小化按钮
        min_btn = QPushButton("−")
        min_btn.setFixedSize(32, 26)
        min_btn.setStyleSheet("""
            QPushButton {
                background: rgba(74, 144, 226, 0.8);
                border: 1px solid rgba(74, 144, 226, 0.8);
                border-radius: 13px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(74, 144, 226, 1.0);
                border: 1px solid rgba(74, 144, 226, 1.0);
            }
        """)
        min_btn.clicked.connect(self.showMinimized)
        controls_layout.addWidget(min_btn)
        
        # 最大化按钮
        max_btn = QPushButton("□")
        max_btn.setFixedSize(32, 26)
        max_btn.setStyleSheet(min_btn.styleSheet())
        max_btn.clicked.connect(self._toggle_maximize)
        controls_layout.addWidget(max_btn)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(32, 26)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 107, 107, 0.9);
                border: 1px solid rgba(255, 107, 107, 0.9);
                border-radius: 13px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 80, 80, 1.0);
                border: 1px solid rgba(255, 80, 80, 1.0);
            }
        """)
        close_btn.clicked.connect(self.close)
        controls_layout.addWidget(close_btn)
        
        # 将卡片添加到主布局
        layout.addWidget(controls_card)
        
    def _toggle_maximize(self):
        """切换最大化状态"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
            
    def _create_content_area(self) -> QWidget:
        """创建内容区域"""
        # 创建整体容器
        content_container = QWidget()
        content_container.setStyleSheet("""
            QWidget {
                background: rgba(20, 20, 35, 0.95);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-top: none;
                border-radius: 0px 0px 15px 15px;
                padding: 8px;
                margin: 0px;
            }
        """)
        
        # 主布局
        container_layout = QHBoxLayout(content_container)
        margin = LAYOUT_CONSTANTS['content_margin']
        container_layout.setContentsMargins(*margin)
        container_layout.setSpacing(LAYOUT_CONSTANTS['panel_spacing'])
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter {
                background: transparent;
                border: none;
            }
            QSplitter::handle {
                background: rgba(74, 144, 226, 0.4);
                border-radius: 2px;
                margin: 2px;
                width: 3px;
            }
            QSplitter::handle:hover {
                background: rgba(74, 144, 226, 0.7);
            }
        """)
        
        # 左侧控制面板
        self.control_panel = ModernControlPanel(self.container)
        self.control_panel.setMinimumWidth(350)
        self.control_panel.setMaximumWidth(450)
        # 为控制面板添加卡片样式
        radius = LAYOUT_CONSTANTS['border_radius']
        margin = LAYOUT_CONSTANTS['card_margin']
        self.control_panel.setStyleSheet(self.control_panel.styleSheet() + f"""
            ModernControlPanel {{
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(74, 144, 226, 0.4);
                border-radius: {radius}px;
                margin: {margin[0]}px {margin[1]}px {margin[2]}px {margin[3]}px;
            }}
        """)
        splitter.addWidget(self.control_panel)
        
        # 中央游戏视图
        self.game_view = ModernGameView()
        # 为游戏视图添加卡片样式
        self.game_view.setStyleSheet(self.game_view.styleSheet() + f"""
            ModernGameView {{
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(74, 144, 226, 0.4);
                border-radius: {radius}px;
                margin: {margin[0]}px {margin[1]}px {margin[2]}px {margin[3]}px;
            }}
        """)
        splitter.addWidget(self.game_view)
        
        # 右侧状态面板
        self.status_panel = ModernStatusPanel()
        self.status_panel.setMinimumWidth(300)
        self.status_panel.setMaximumWidth(400)
        # 为状态面板添加卡片样式
        self.status_panel.setStyleSheet(self.status_panel.styleSheet() + f"""
            ModernStatusPanel {{
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(74, 144, 226, 0.4);
                border-radius: {radius}px;
                margin: {margin[0]}px {margin[1]}px {margin[2]}px {margin[3]}px;
            }}
        """)
        splitter.addWidget(self.status_panel)
        
        # 设置分割比例
        splitter.setSizes([350, 900, 350])
        
        # 将分割器添加到容器布局
        container_layout.addWidget(splitter)
        
        return content_container
        
    def _create_modern_toolbar(self):
        """创建现代化工具栏"""
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: rgba(26, 26, 46, 0.9);
                border: none;
                border-radius: 10px;
                padding: 6px;
                margin: 3px;
                spacing: 5px;
            }
            QToolBar QToolButton {
                background: rgba(74, 144, 226, 0.7);
                border: 2px solid rgba(74, 144, 226, 0.7);
                border-radius: 8px;
                padding: 8px 12px;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QToolBar QToolButton:hover {
                background: rgba(74, 144, 226, 0.9);
                border-color: rgba(74, 144, 226, 1.0);
            }
            QToolBar QToolButton:pressed {
                background: rgba(74, 144, 226, 1.0);
                color: #ffffff;
            }
        """)
        
        # 添加工具栏动作 - 合并相关功能到组合按钮
        # 检测与分析组合
        toolbar.addAction("🎯 窗口检测", self._on_capture_action)
        toolbar.addAction("🔍 状态分析", self._on_analyze_action)
        toolbar.addSeparator()
        
        # 自动化控制组合
        toolbar.addAction("▶️ 开始自动化", self._on_start_action)
        toolbar.addAction("⏹️ 停止自动化", self._on_stop_action)
        toolbar.addSeparator()
        
        # 监控与设置组合
        toolbar.addAction("📊 性能监控", self._on_monitor_action)
        toolbar.addAction("⚙️ 设置", self._on_settings_action)
        
        self.addToolBar(toolbar)
        
    def _create_modern_statusbar(self):
        """创建现代化状态栏"""
        statusbar = QStatusBar()
        statusbar.setStyleSheet("""
            QStatusBar {
                background: rgba(26, 26, 46, 0.9);
                border-top: 2px solid rgba(74, 144, 226, 0.3);
                color: #ffffff;
                padding: 6px;
            }
            QStatusBar QLabel {
                background: rgba(74, 144, 226, 0.6);
                border: 2px solid rgba(74, 144, 226, 0.6);
                border-radius: 6px;
                padding: 3px 8px;
                margin: 1px 3px;
                font-size: 11px;
                font-weight: bold;
                color: #ffffff;
            }
        """)
        
        # 状态信息标签
        self.status_label = QLabel("就绪")
        self.cpu_label = QLabel("CPU: 0%")
        self.memory_label = QLabel("内存: 0%")
        self.fps_label = QLabel("FPS: 0")
        
        statusbar.addWidget(self.status_label)
        statusbar.addPermanentWidget(self.fps_label)
        statusbar.addPermanentWidget(self.memory_label)
        statusbar.addPermanentWidget(self.cpu_label)
        
        self.setStatusBar(statusbar)
        
    def _add_shadow_effects(self):
        """添加阴影效果"""
        # 为主要组件添加阴影
        components = [self.control_panel, self.game_view, self.status_panel]
        
        for component in components:
            if component:
                shadow = QGraphicsDropShadowEffect()
                shadow.setBlurRadius(20)
                shadow.setColor(QColor(0, 0, 0, 80))
                shadow.setOffset(0, 5)
                component.setGraphicsEffect(shadow)
                
    def _setup_animations(self):
        """设置动画效果"""
        # 这里可以添加更多动画效果
        pass
        
    def _connect_signals(self):
        """连接信号"""
        if self.control_panel:
            self.control_panel.window_selected.connect(self.window_selected.emit)
            self.control_panel.start_clicked.connect(self.automation_started.emit)
            self.control_panel.stop_clicked.connect(self.automation_stopped.emit)
            
        # 定时器信号
        self.capture_timer.timeout.connect(self._on_capture_timeout)
        self.monitor_timer.timeout.connect(self._on_monitor_timeout)
        
    def _start_timers(self):
        """启动定时器"""
        self.capture_timer.start(33)  # ~30 FPS
        self.monitor_timer.start(1000)  # 1秒更新一次
        
    def _on_capture_timeout(self):
        """捕获超时处理"""
        if self.window_adapter and self.game_view and self.control_panel:
            try:
                # 获取选中的窗口
                selected_window = self.control_panel.get_selected_window()
                if selected_window:
                    # 查找窗口信息
                    window_info = self.window_adapter.find_window(selected_window)
                    if window_info:
                        # 捕获窗口画面
                        frame = self.window_adapter.capture_window(window_info)
                        if frame is not None:
                            self.game_view.update_frame(frame)
            except Exception as e:
                self.logger.error(f"Capture error: {e}")
                
    def _on_monitor_timeout(self):
        """监控超时处理"""
        if self.status_panel:
            self.status_panel.update_system_stats()
            
    # 工具栏动作处理
    def _on_capture_action(self):
        """窗口捕获动作"""
        self.logger.info("Window capture action triggered")
        
    def _on_analyze_action(self):
        """状态分析动作"""
        self.logger.info("State analysis action triggered")
        
    def _on_start_action(self):
        """开始自动化动作"""
        self.automation_started.emit()
        
    def _on_stop_action(self):
        """停止自动化动作"""
        self.automation_stopped.emit()
        
    def _on_monitor_action(self):
        """性能监控动作"""
        self.logger.info("Performance monitor action triggered")
        
    def _on_settings_action(self):
        """设置动作"""
        self.logger.info("Settings action triggered")
        
    def update_status(self, message: str):
        """更新状态信息"""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
            
    def set_automation_running(self, running: bool):
        """设置自动化运行状态"""
        if self.control_panel:
            self.control_panel.set_automation_running(running)
            
    def get_selected_window(self) -> Optional[str]:
        """获取选中的窗口"""
        if self.control_panel:
            return self.control_panel.get_selected_window()
        return None
        
    def set_window_list(self, windows: list):
        """设置窗口列表"""
        if self.control_panel:
            self.control_panel.set_window_list(windows)
            
    def eventFilter(self, obj, event):
        """事件过滤器 - 处理标题栏拖拽"""
        if obj == self.title_bar:
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    event.accept()
                    return True
            elif event.type() == QEvent.Type.MouseMove:
                if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
                    self.move(event.globalPosition().toPoint() - self.drag_position)
                    event.accept()
                    return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if event.button() == Qt.MouseButton.LeftButton:
                    self.drag_position = None
                    event.accept()
                    return True
        return super().eventFilter(obj, event)
        
    def closeEvent(self, event):
        """关闭事件处理"""
        self.capture_timer.stop()
        self.monitor_timer.stop()
        super().closeEvent(event)


def main():
    """测试现代化主窗口"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("游戏自动化工具")
    app.setApplicationVersion("2.0")
    
    window = ModernMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()