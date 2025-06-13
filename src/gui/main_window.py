"""
主窗口界面
使用PyQt6实现GUI界面
"""
import sys
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QProgressBar,
    QMessageBox,
    QSplitter,
    QToolBar,
    QStatusBar,
    QFileDialog,
    QDockWidget,
    QGroupBox,
    QListWidget,
    QDialog,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QAction, QImage, QPixmap
import logging
import json
import os
from pathlib import Path

from core.resource_manager import ResourceManager
from core.task_system import TaskScheduler, Task, TaskPriority, TaskStatus
from src.services.error_handler import ErrorHandler
from src.common.error_types import ErrorCode, ErrorContext
from core.game_adapter import GameAdapter
from macro.macro_recorder import MacroRecorder
from macro.macro_player import MacroPlayer
from macro.macro_editor import MacroEditor
from editor.script_editor import ScriptEditor
from editor.code_formatter import CodeFormatter
from editor.project_manager import ProjectManager
from performance.performance_monitor import PerformanceMonitor, PerformanceMetrics
from performance.performance_view import PerformanceView
from services.window_manager import WindowManager, WindowInfo
from services.image_processor import ImageProcessor, TemplateMatchResult
from services.auto_operator import AutoOperator, Action
from services.game_state_analyzer import GameStateAnalyzer, GameState
from .state_history_view import StateHistoryView
from .widgets.game_view import GameView
from .widgets.control_panel import ControlPanel
from services.window.window_capture import WindowCapture
from services.vision.template_matcher import TemplateMatcher
from services.vision.state_recognizer import StateRecognizer
from services.automation.auto_controller import AutoController
from .dialogs.template_manager_dialog import TemplateManagerDialog
from .dialogs.automation_manager_dialog import AutomationManagerDialog
from .dialogs.config_manager_dialog import ConfigManagerDialog


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("游戏自动化操作系统")
        self.setMinimumSize(1200, 800)

        # 初始化组件
        self.resource_manager = ResourceManager("config/resource.json")
        self.task_scheduler = TaskScheduler(self.resource_manager)
        self.error_handler = ErrorHandler("logs/snapshots")
        self.window_manager = WindowManager(self.error_handler)
        self.image_processor = ImageProcessor(self.error_handler)
        self.auto_operator = AutoOperator(self.error_handler, self.window_manager, self.image_processor)
        self.game_state_analyzer = GameStateAnalyzer(self.error_handler)
        self.game_adapters: Dict[str, GameAdapter] = {}

        # 初始化新组件
        self.macro_recorder = MacroRecorder()
        self.macro_player = MacroPlayer()
        self.macro_editor = MacroEditor()
        self.code_formatter = CodeFormatter()
        self.project_manager = ProjectManager()
        self.performance_monitor = PerformanceMonitor(self.error_handler)
        self.state_history = StateHistoryView()  # 状态历史视图
        self.game_view = GameView()  # 游戏画面显示
        self.control_panel = ControlPanel()  # 控制面板
        self.window_capture = WindowCapture(self.error_handler)
        self.template_matcher = TemplateMatcher(self.error_handler)
        self.state_recognizer = StateRecognizer(self.error_handler)
        self.auto_controller = AutoController(self.error_handler)

        # 初始化状态
        self.current_window: Optional[WindowInfo] = None
        self.current_frame = None
        self.current_state: Optional[GameState] = None
        self.is_automation_running = False

        # 创建UI
        self._create_ui()
        self._create_toolbar()
        self._create_statusbar()
        self._create_docks()
        self._connect_signals()

        # 启动监控
        self.resource_manager.start_monitoring()
        self.task_scheduler.start()

        # 初始化定时器
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self._on_capture_timeout)
        self.capture_timer.start(100)  # 10fps
        
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._on_monitor_timeout)
        self.monitor_timer.start(1000)  # 1fps

        self.error_handler = ErrorHandler()
        self.config_dir = "config"
        self.config_file = "config.json"
        
        self._init_services()
        self._load_config()
        self._init_timers()

    def _create_ui(self):
        """创建UI界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧控制面板
        splitter.addWidget(self.control_panel)

        # 中间游戏画面
        splitter.addWidget(self.game_view)

        # 右侧状态面板
        splitter.addWidget(self.state_history)

        # 设置分割比例
        splitter.setSizes([200, 600, 400])

        main_layout.addWidget(splitter)

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # 文件操作
        new_action = QAction("新建配置", self)
        new_action.triggered.connect(self._on_new_config)
        toolbar.addAction(new_action)

        open_action = QAction("打开配置", self)
        open_action.triggered.connect(self._on_open_config)
        toolbar.addAction(open_action)

        save_action = QAction("保存配置", self)
        save_action.triggered.connect(self._on_save_config)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # 状态模板操作
        add_template_action = QAction("添加状态模板", self)
        add_template_action.triggered.connect(self._on_add_state_template)
        toolbar.addAction(add_template_action)

        edit_template_action = QAction("编辑状态模板", self)
        edit_template_action.triggered.connect(self._on_edit_state_template)
        toolbar.addAction(edit_template_action)

        # 自动化操作
        automation_action = QAction("自动化", self)
        automation_action.triggered.connect(self._on_manage_automation)
        toolbar.addAction(automation_action)

    def _create_statusbar(self):
        """创建状态栏"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        # CPU使用率
        self.cpu_label = QLabel("CPU: 0%")
        statusbar.addPermanentWidget(self.cpu_label)

        # 内存使用
        self.memory_label = QLabel("内存: 0MB")
        statusbar.addPermanentWidget(self.memory_label)

        # FPS
        self.fps_label = QLabel("FPS: 0")
        statusbar.addPermanentWidget(self.fps_label)

        # 当前状态
        self.state_label = QLabel("状态: 未知")
        statusbar.addPermanentWidget(self.state_label)

        # 性能标签
        self.performance_label = QLabel()
        statusbar.addPermanentWidget(self.performance_label)

    def _create_docks(self):
        """创建停靠窗口"""
        # 项目浏览器
        project_dock = QDockWidget("项目", self)
        project_dock.setWidget(self._create_project_browser())
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, project_dock)

        # 性能监控
        performance_dock = QDockWidget("性能监控", self)
        self.performance_view = PerformanceView()
        performance_dock.setWidget(self.performance_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, performance_dock)

    def _connect_signals(self):
        """连接信号"""
        # 控制面板信号
        self.control_panel.window_selected.connect(self._on_window_selected)
        self.control_panel.refresh_clicked.connect(self._on_refresh_windows)
        self.control_panel.analyze_clicked.connect(self._on_analyze_game)
        self.control_panel.start_clicked.connect(self._on_start_automation)
        self.control_panel.stop_clicked.connect(self._on_stop_automation)

    def _on_capture_timeout(self):
        """捕获定时器超时处理"""
        if not self.current_window:
            return
            
        # 捕获窗口
        frame = self.window_capture.capture_window(self.current_window.hwnd)
        if frame is None:
            return
            
        # 更新游戏视图
        self._update_game_view(frame)
        
        # 如果自动化正在运行，分析游戏状态
        if self.is_automation_running:
            self._analyze_game_state(frame)
            
    def _on_monitor_timeout(self):
        """监控定时器超时处理"""
        # 更新性能指标
        metrics = self.performance_monitor.update()
        if metrics:
            self._update_performance_display(metrics)
            
    def _update_game_view(self, frame):
        """更新游戏视图
        
        Args:
            frame: 游戏画面
        """
        try:
            # 转换图像格式
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # 缩放图像
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(self.game_view.size(), 
                                        Qt.KeepAspectRatio,
                                        Qt.SmoothTransformation)
            
            # 显示图像
            self.game_view.update_frame(scaled_pixmap)
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.UI_ERROR,
                "更新游戏视图失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="MainWindow._update_game_view"
                )
            )
            
    def _analyze_game_state(self, frame):
        """分析游戏状态
        
        Args:
            frame: 游戏画面
        """
        try:
            # 分析游戏状态
            state = self.state_recognizer.analyze_frame(frame)
            if state:
                self.current_state = state
                self._update_state_display(state)
                
                # 执行自动化
                self.auto_controller.execute(state)
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.STATE_ANALYSIS_ERROR,
                "分析游戏状态失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="MainWindow._analyze_game_state"
                )
            )
            
    def _update_state_display(self, state: GameState):
        """更新状态显示
        
        Args:
            state: 游戏状态
        """
        # 更新状态标签
        self.state_label.setText(f"当前状态: {state.name} (置信度: {state.confidence:.2f})")
        
        # 更新状态历史
        state_info = {
            'value': state.confidence,
            'description': f"状态: {state.name} (置信度: {state.confidence:.2f})"
        }
        self.state_history.add_state(state_info)
        
        # 限制历史记录数量
        while self.state_history.count() > 100:
            self.state_history.remove_state(0)
            
    def _update_performance_display(self, metrics: PerformanceMetrics):
        """更新性能显示
        
        Args:
            metrics: 性能指标
        """
        # 更新性能标签
        self.cpu_label.setText(f"CPU: {metrics.cpu_percent:.1f}%")
        self.memory_label.setText(f"内存: {metrics.memory_percent:.1f}MB")
        self.fps_label.setText(f"FPS: {metrics.fps:.1f}")
        
        # 更新状态栏性能标签
        self.performance_label.setText(
            f"CPU: {metrics.cpu_percent:.1f}% | "
            f"内存: {metrics.memory_percent:.1f}MB | "
            f"FPS: {metrics.fps:.1f}"
        )
        
    def _on_window_selected(self, hwnd: int):
        """窗口选择事件
        
        Args:
            hwnd: 窗口句柄
        """
        if hwnd:
            # 获取窗口信息
            window_info = self.window_manager.get_window_info(hwnd)
            if window_info:
                # 更新游戏画面
                self.window_capture.start_capture(hwnd, self._on_frame_captured)
                
                # 初始化性能监控
                if self.performance_monitor:
                    self.performance_monitor.stop()
                self.performance_monitor.start()

    def _on_frame_captured(self, frame):
        """帧捕获回调
        
        Args:
            frame: 捕获的帧
        """
        # 更新游戏画面
        self._update_game_view(frame)
        
        # 分析游戏状态
        if self.control_panel.is_automation_running():
            self._analyze_game_state(frame)

    def _on_refresh_windows(self):
        """刷新窗口列表"""
        # 获取窗口列表
        windows = self.window_manager.get_window_list()
        
        # 更新控制面板
        window_titles = [w.title for w in windows]
        self.control_panel.set_window_list(window_titles)

    def _on_analyze_game(self):
        """分析游戏状态"""
        # 获取当前帧
        frame = self.game_view.get_current_frame()
        if frame is not None:
            self._analyze_game_state(frame)

    def _on_start_automation(self):
        """开始自动化"""
        try:
            if not self.current_window:
                QMessageBox.warning(self, "警告", "请先选择窗口")
                return
                
            # 创建自动化动作
            actions = [
                Action(
                    name="等待游戏加载",
                    type="wait",
                    params={"duration": 2.0}
                ),
                Action(
                    name="点击开始按钮",
                    type="click",
                    params={"x": 100, "y": 100}
                ),
                Action(
                    name="检查游戏开始",
                    type="condition",
                    params={"state": "game_started"}
                )
            ]
            
            # 添加动作
            self.auto_controller.clear_actions()
            for action in actions:
                self.auto_controller.add_action(action)
                
            # 开始自动化
            if self.auto_controller.start():
                self.control_panel.set_automation_running(True)
                self.is_automation_running = True
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.AUTO_CONTROL_ERROR,
                "开始自动化失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="MainWindow._on_start_automation"
                )
            )

    def _on_stop_automation(self):
        """停止自动化"""
        self.auto_controller.stop()
        self.control_panel.set_automation_running(False)
        self.is_automation_running = False

    def _on_new_config(self):
        """新建配置"""
        # TODO: 实现新建配置
        pass

    def _on_open_config(self):
        """打开配置"""
        # TODO: 实现打开配置
        pass

    def _on_save_config(self):
        """保存配置"""
        # TODO: 实现保存配置
        pass

    def _on_add_state_template(self):
        """添加状态模板"""
        # TODO: 实现添加状态模板
        pass

    def _on_edit_state_template(self):
        """编辑状态模板"""
        # TODO: 实现编辑状态模板
        pass

    def _on_manage_automation(self):
        """管理自动化处理"""
        try:
            # 创建自动化管理对话框
            dialog = AutomationManagerDialog(
                self.auto_controller,
                self.state_recognizer,
                self.error_handler,
                self
            )
            
            # 显示对话框
            if dialog.exec_() == QDialog.Accepted:
                # 更新自动化状态
                if self.is_automation_running:
                    self._on_stop_automation()
                    
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.UI_ERROR,
                "管理自动化失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="MainWindow._on_manage_automation"
                )
            )

    def _on_manage_templates(self):
        """管理状态模板处理"""
        try:
            # 创建模板管理对话框
            dialog = TemplateManagerDialog(self.state_recognizer, self.error_handler, self)
            
            # 显示对话框
            if dialog.exec_() == QDialog.Accepted:
                # 更新状态显示
                if self.current_state:
                    self._update_state_display(self.current_state)
                    
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.UI_ERROR,
                "管理状态模板失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="MainWindow._on_manage_templates"
                )
            )

    def _create_project_browser(self) -> QTreeWidget:
        """创建项目浏览器
        
        Returns:
            QTreeWidget: 项目浏览器
        """
        tree = QTreeWidget()
        tree.setHeaderLabels(["项目文件"])
        tree.setColumnCount(1)
        return tree

    def _init_services(self):
        """初始化服务"""
        try:
            # 窗口服务
            self.window_manager = WindowManager(self.error_handler)
            self.window_capture = WindowCapture(self.error_handler)
            
            # 视觉服务
            self.image_processor = ImageProcessor(self.error_handler)
            self.template_matcher = TemplateMatcher(self.error_handler)
            self.state_recognizer = StateRecognizer(self.error_handler)
            
            # 自动化服务
            self.auto_controller = AutoController(self.error_handler)
            
            # 监控服务
            self.performance_monitor = PerformanceMonitor(self.error_handler)
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.INIT_ERROR,
                "初始化服务失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="MainWindow._init_services"
                )
            )
            
    def _load_config(self):
        """加载配置"""
        try:
            # 创建配置目录
            os.makedirs(self.config_dir, exist_ok=True)
            
            # 加载配置文件
            config_path = os.path.join(self.config_dir, self.config_file)
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    
                # 系统配置
                if "system" in config:
                    system = config["system"]
                    if "capture" in system:
                        capture = system["capture"]
                        self.capture_interval = capture.get("interval", 100)
                        self.capture_quality = capture.get("quality", 80)
                        
                    if "performance" in system:
                        performance = system["performance"]
                        self.monitor_interval = performance.get("interval", 1000)
                        self.max_history_size = performance.get("max_history", 1000)
                        self.performance_monitor.set_max_history_size(self.max_history_size)
                        
                # 游戏配置
                if "game" in config:
                    game = config["game"]
                    if "window" in game:
                        window = game["window"]
                        self.window_title = window.get("title", "")
                        self.window_class = window.get("class", "")
                        
                    if "state" in game:
                        state = game["state"]
                        self.state_threshold = state.get("threshold", 80)
                        self.auto_save_state = state.get("auto_save", False)
                        
                # 自动化配置
                if "automation" in config:
                    auto = config["automation"]
                    if "action" in auto:
                        action = auto["action"]
                        self.default_timeout = action.get("timeout", 5)
                        self.default_retry = action.get("retry", 3)
                        
                    if "debug" in auto:
                        debug = auto["debug"]
                        self.save_debug_image = debug.get("save_image", False)
                        self.debug_dir = debug.get("dir", "debug")
                        
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.CONFIG_ERROR,
                "加载配置失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="MainWindow._load_config"
                )
            )
            
    def _on_manage_config(self):
        """配置管理处理"""
        try:
            dialog = ConfigManagerDialog(self.error_handler, self)
            if dialog.exec_() == QDialog.Accepted:
                self._load_config()
                self._update_timers()
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.UI_ERROR,
                "配置管理失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="MainWindow._on_manage_config"
                )
            )
            
    def _update_timers(self):
        """更新定时器"""
        try:
            # 更新捕获定时器
            if hasattr(self, "capture_timer"):
                self.capture_timer.setInterval(self.capture_interval)
                
            # 更新监控定时器
            if hasattr(self, "monitor_timer"):
                self.monitor_timer.setInterval(self.monitor_interval)
                
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.TIMER_ERROR,
                "更新定时器失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="MainWindow._update_timers"
                )
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
