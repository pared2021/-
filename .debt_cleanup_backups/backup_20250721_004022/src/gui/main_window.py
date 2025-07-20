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
    QInputDialog,
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
import shutil
from pathlib import Path

from src.core.resource_manager import ResourceManager
from src.core.task_system import TaskScheduler, Task, TaskPriority, TaskStatus
from src.services.error_handler import ErrorHandler
from src.common.error_types import ErrorCode, ErrorContext
from src.core.game_adapter import GameAdapter
from src.macro.macro_recorder import MacroRecorder
from src.macro.macro_player import MacroPlayer
from src.macro.macro_editor import MacroEditor
from src.editor.script_editor import ScriptEditor
from src.editor.code_formatter import CodeFormatter
from src.editor.project_manager import ProjectManager
from src.performance.performance_monitor import PerformanceMonitor
from src.core.types import UnifiedPerformanceMetrics as PerformanceMetrics
from src.performance.performance_view import PerformanceView
from src.services.window_manager import GameWindowManager, WindowInfo
from src.infrastructure.adapters.legacy_window_adapter import LegacyWindowAdapter
from src.core.domain.window_models import WindowInfo as UnifiedWindowInfo
from src.services.image_processor import ImageProcessor
from src.core.types import UnifiedTemplateMatchResult as TemplateMatchResult
from src.services.auto_operator import AutoOperator, Action
from src.services.game_analyzer import GameAnalyzer as GameStateAnalyzer
from src.core.types import UnifiedGameState as GameState
from .state_history_view import StateHistoryView
from .widgets.game_view import GameView
from .widgets.control_panel import ControlPanel
from src.services.capture_engines import GameCaptureEngine as WindowCapture
from src.services.vision.template_matcher import TemplateMatcher
from src.services.vision.state_recognizer import StateRecognizer
from src.services.automation.auto_controller import AutoController
from .dialogs.template_manager_dialog import TemplateManagerDialog
from .dialogs.automation_manager_dialog import AutomationManagerDialog
from .dialogs.config_manager_dialog import ConfigManagerDialog


class MainWindow(QMainWindow):
    """主窗口 - 使用Clean Architecture和依赖注入"""

    def __init__(self, container=None):
        super().__init__()
        self.setWindowTitle("游戏自动化操作系统")
        self.setMinimumSize(1200, 800)

        # 保存容器实例
        self.container = container
        
        # 初始化统一窗口管理器
        self.unified_window_adapter = LegacyWindowAdapter()
        
        # 初始化组件 - 使用依赖注入
        if container:
            # 使用新的Clean Architecture架构
            self.game_analyzer_service = container.game_analyzer()
            self.automation_service = container.automation_service()
            self.state_manager_service = container.state_manager()
            self.config_repository = container.config_repository()
            self.template_repository = container.template_repository()
            self.window_adapter = self.unified_window_adapter  # 使用统一适配器
            self.input_adapter = container.input_adapter()
            
            # 获取配置
            self.config = self.config_repository.get_all_configs()
            
            # 创建错误处理器（临时解决方案）
            from src.services.error_handler import ErrorHandler
            from src.services.logger import GameLogger
            from src.services.config import config
            
            # 创建GameLogger实例，使用统一配置系统
            game_logger = GameLogger(config, "MainWindow_ErrorHandler")
            self.error_handler = ErrorHandler(game_logger)
            
            # 创建UI需要的组件
            self.auto_controller = AutoController(self.error_handler)
            self.state_recognizer = StateRecognizer(self.error_handler)
            
            # 状态管理
            self.current_state = None
            self.is_automation_running = False
        else:
            # 向后兼容的备选方案
            self._init_legacy_components()

        # 初始化UI组件
        self.state_history = StateHistoryView()  # 状态历史视图
        self.game_view = GameView()  # 游戏画面显示
        self.control_panel = ControlPanel()  # 控制面板

        # 初始化状态
        self.current_window: Optional[WindowInfo] = None
        self.current_frame = None
        
        # 创建UI
        self._create_ui()
        self._create_toolbar()
        self._create_statusbar()
        self._create_docks()
        self._connect_signals()

        # 初始化定时器
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self._on_capture_timeout)
        self.capture_timer.start(100)  # 10fps
        
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._on_monitor_timeout)
        self.monitor_timer.start(1000)  # 1fps

        # 初始化配置
        self._init_config_defaults()

    def _init_legacy_components(self):
        """初始化传统组件作为备选方案"""
        # 传统组件初始化
        self.resource_manager = ResourceManager("config/resource.json")
        self.task_scheduler = TaskScheduler(self.resource_manager)
        self.error_handler = ErrorHandler("logs/snapshots")
        
        # 创建GameWindowManager所需的依赖
        from src.services.logger import GameLogger
        from src.services.config import config
        
        # 使用统一配置实例
        self.config = config
        game_logger = GameLogger(self.config, "MainWindow")
        
        self.window_manager = GameWindowManager(game_logger, self.config, self.error_handler)
        self.image_processor = ImageProcessor(game_logger, self.config, self.error_handler)
        self.auto_operator = AutoOperator(self.error_handler, self.window_manager, self.image_processor)
        self.game_state_analyzer = GameStateAnalyzer(self.error_handler)
        self.game_adapters: Dict[str, GameAdapter] = {}

        # 初始化新组件
        self.macro_recorder = MacroRecorder()
        self.macro_player = MacroPlayer()
        self.macro_editor = MacroEditor()
        self.code_formatter = CodeFormatter()
        self.project_manager = ProjectManager()
        self.performance_monitor = PerformanceMonitor("游戏")
        self.window_capture = WindowCapture(game_logger)
        self.template_matcher = TemplateMatcher(self.error_handler)
        self.state_recognizer = StateRecognizer(self.error_handler)
        self.auto_controller = AutoController(self.error_handler)
        
        # 状态管理
        self.current_state: Optional[GameState] = None
        self.is_automation_running = False
        
        # 启动监控
        self.resource_manager.start_monitoring()
        self.task_scheduler.start()

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
        
        toolbar.addSeparator()
        
        # 性能监控
        performance_action = QAction("性能监控", self)
        performance_action.triggered.connect(self._on_show_performance)
        toolbar.addAction(performance_action)

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
        
        # 性能监控组件保留但不作为停靠窗口显示
        self.performance_view = PerformanceView()

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
            
        try:
            # 使用统一窗口适配器捕获
            frame = self.unified_window_adapter.capture_window(self.current_window.handle)
            if frame is None:
                return
                
            # 更新游戏视图
            self._update_game_view(frame)
            
            # 如果自动化正在运行，分析游戏状态
            if self.is_automation_running:
                if self.container:
                    self._analyze_game_state_with_use_case(frame)
                else:
                    self._analyze_game_state(frame)
        except Exception as e:
            logging.getLogger(__name__).error(f"捕获窗口失败: {e}")
            
    def _on_monitor_timeout(self):
        """监控定时器超时处理"""
        try:
            if self.container:
                # 使用新的Clean Architecture
                # 可以获取性能指标，但暂时使用简单的系统指标
                import psutil
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                
                # 更新性能显示
                self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
                self.memory_label.setText(f"内存: {memory_info.percent:.1f}%")
                self.fps_label.setText(f"FPS: {10}")  # 固定值，待改进
                
                # 更新状态栏性能标签
                self.performance_label.setText(
                    f"CPU: {cpu_percent:.1f}% | "
                    f"内存: {memory_info.percent:.1f}% | "
                    f"FPS: {10}"
                )
            else:
                # 传统架构
                metrics = self.performance_monitor.update()
                if metrics:
                    self._update_performance_display(metrics)
        except Exception as e:
            if self.container:
                logging.getLogger(__name__).error(f"更新性能监控失败: {e}")
            else:
                logging.getLogger(__name__).error(f"更新性能监控失败: {e}")
            
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
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "更新游戏视图失败",
                ErrorContext(
                    source="MainWindow._update_game_view",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
    def _analyze_game_state_with_use_case(self, frame):
        """使用Clean Architecture分析游戏状态
        
        Args:
            frame: 游戏画面
        """
        try:
            # 使用游戏分析用例
            result = self.game_analysis_use_case.execute(frame)
            if result:
                self.current_state = result
                self._update_state_display_modern(result)
                
                # 执行自动化
                if self.is_automation_running:
                    self.automation_service.execute_automation(result)
                
        except Exception as e:
            # 使用新的架构记录错误
            logging.getLogger(__name__).error(f"分析游戏状态失败: {e}")
            
    def _analyze_game_state(self, frame):
        """分析游戏状态 - 传统架构
        
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
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.STATE_ANALYSIS_ERROR,
                "分析游戏状态失败",
                ErrorContext(
                    source="MainWindow._analyze_game_state",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
    def _update_state_display_modern(self, result):
        """更新状态显示 - 现代架构
        
        Args:
            result: 游戏分析结果
        """
        # 更新状态标签
        if hasattr(result, 'state_name') and hasattr(result, 'confidence'):
            self.state_label.setText(f"当前状态: {result.state_name} (置信度: {result.confidence:.2f})")
            
            # 更新状态历史
            state_info = {
                'value': result.confidence,
                'description': f"状态: {result.state_name} (置信度: {result.confidence:.2f})"
            }
            self.state_history.add_state(state_info)
            
            # 限制历史记录数量
            while self.state_history.count() > 100:
                self.state_history.remove_state(0)
                
            # 使用状态管理器保存状态
            self.state_manager_service.save_state(result)
        else:
            # 兼容处理
            self.state_label.setText(f"当前状态: 已分析")
            
    def _update_state_display(self, state: GameState):
        """更新状态显示 - 传统架构
        
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
        try:
            if hwnd:
                # 使用统一窗口适配器
                window_info = self.unified_window_adapter.get_unified_window_info(hwnd)
                if window_info:
                    self.current_window = window_info
                    logging.getLogger(__name__).info(f"选择窗口: {window_info.title}")
                    
                    # 如果使用传统架构，启动捕获
                    if not self.container and hasattr(self, 'window_capture'):
                        self.window_capture.start_capture(hwnd, self._on_frame_captured)
                        
                        # 初始化性能监控
                        if hasattr(self, 'performance_monitor') and self.performance_monitor:
                            self.performance_monitor.stop()
                            self.performance_monitor.start()
                else:
                    logging.getLogger(__name__).warning(f"无法获取窗口信息: {hwnd}")
            else:
                logging.getLogger(__name__).warning("无效的窗口句柄")
        except Exception as e:
            logging.getLogger(__name__).error(f"选择窗口失败: {e}")
            QMessageBox.warning(self, "警告", f"选择窗口失败: {e}")

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
        try:
            # 使用统一窗口适配器
            window_list = self.unified_window_adapter.get_window_list()
            self.control_panel.set_window_list(window_list)
            logging.getLogger(__name__).info(f"刷新窗口列表成功，找到 {len(window_list)} 个窗口")
        except Exception as e:
            logging.getLogger(__name__).error(f"刷新窗口列表失败: {e}")
            QMessageBox.warning(self, "警告", f"刷新窗口列表失败: {e}")

    def _on_analyze_game(self):
        """分析游戏状态"""
        try:
            # 获取当前帧
            frame = self.game_view.get_current_frame()
            if frame is not None:
                if self.container:
                    # 使用新的Clean Architecture
                    self._analyze_game_state_with_use_case(frame)
                else:
                    # 传统架构
                    self._analyze_game_state(frame)
            else:
                QMessageBox.warning(self, "警告", "没有可分析的游戏画面")
        except Exception as e:
            if self.container:
                logging.getLogger(__name__).error(f"分析游戏状态失败: {e}")
                QMessageBox.critical(self, "错误", f"分析游戏状态失败: {e}")
            else:
                logging.getLogger(__name__).error(f"分析游戏状态失败: {e}")

    def _on_start_automation(self):
        """开始自动化"""
        try:
            if not self.current_window:
                QMessageBox.warning(self, "警告", "请先选择窗口")
                return
                
            if self.container:
                # 使用新的Clean Architecture
                # 使用自动化服务启动自动化
                if self.automation_service.start_automation():
                    self.control_panel.set_automation_running(True)
                    self.is_automation_running = True
                    QMessageBox.information(self, "信息", "自动化已启动")
                else:
                    QMessageBox.warning(self, "警告", "启动自动化失败")
            else:
                # 传统架构
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
            if self.container:
                logging.getLogger(__name__).error(f"开始自动化失败: {e}")
                QMessageBox.critical(self, "错误", f"开始自动化失败: {e}")
            else:
                from src.common.error_types import GameAutomationError
                error = GameAutomationError(
                    ErrorCode.AUTO_CONTROL_ERROR,
                    "开始自动化失败",
                    ErrorContext(
                        source="MainWindow._on_start_automation",
                        details={"error_info": str(e)}
                    )
                )
                self.error_handler.handle_error(error)

    def _on_stop_automation(self):
        """停止自动化"""
        try:
            if self.container:
                # 使用新的Clean Architecture
                self.automation_service.stop_automation()
                self.control_panel.set_automation_running(False)
                self.is_automation_running = False
                QMessageBox.information(self, "信息", "自动化已停止")
            else:
                # 传统架构
                self.auto_controller.stop()
                self.control_panel.set_automation_running(False)
                self.is_automation_running = False
        except Exception as e:
            if self.container:
                logging.getLogger(__name__).error(f"停止自动化失败: {e}")
                QMessageBox.critical(self, "错误", f"停止自动化失败: {e}")
            else:
                logging.getLogger(__name__).error(f"停止自动化失败: {e}")

    def _on_new_config(self):
        """新建配置"""
        try:
            # 确认是否创建新配置
            reply = QMessageBox.question(
                self,
                "新建配置",
                "确定要创建新配置吗？当前配置将被重置。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # 创建默认配置
                default_config = {
                    "system": {
                        "capture": {
                            "interval": 100,
                            "quality": 80
                        },
                        "performance": {
                            "interval": 1000,
                            "max_history": 1000
                        }
                    },
                    "game": {
                        "window": {
                            "title": "",
                            "class": ""
                        },
                        "state": {
                            "threshold": 80,
                            "auto_save": False
                        }
                    },
                    "automation": {
                        "action": {
                            "timeout": 5,
                            "retry": 3
                        },
                        "debug": {
                            "save_image": False,
                            "dir": "debug"
                        }
                    }
                }
                
                # 保存到默认配置文件
                import json
                import os
                config_dir = "config"
                os.makedirs(config_dir, exist_ok=True)
                config_path = os.path.join(config_dir, "config.json")
                
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                
                # 重新加载配置
                self._init_config_defaults()
                
                QMessageBox.information(self, "信息", "新配置已创建")
                
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.CONFIG_ERROR,
                "创建新配置失败",
                ErrorContext(
                    source="MainWindow._on_new_config",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            QMessageBox.critical(self, "错误", f"创建新配置失败: {e}")

    def _on_open_config(self):
        """打开配置"""
        try:
            # 选择配置文件
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "打开配置文件",
                "config",
                "配置文件 (*.json)"
            )
            
            if not file_path:
                return
                
            # 验证配置文件格式
            import json
            with open(file_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                
            # 检查必要的配置项
            required_sections = ["system", "game", "automation"]
            for section in required_sections:
                if section not in config:
                    QMessageBox.warning(self, "警告", f"配置文件缺少必要的 '{section}' 部分")
                    return
                    
            # 复制到默认配置位置
            config_dir = "config"
            os.makedirs(config_dir, exist_ok=True)
            default_config_path = os.path.join(config_dir, "config.json")
            shutil.copy2(file_path, default_config_path)
            
            # 重新加载配置
            self._init_config_defaults()
            
            QMessageBox.information(self, "信息", "配置文件已加载")
            
        except json.JSONDecodeError:
            QMessageBox.critical(self, "错误", "配置文件格式错误")
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.CONFIG_ERROR,
                "打开配置失败",
                ErrorContext(
                    source="MainWindow._on_open_config",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            QMessageBox.critical(self, "错误", f"打开配置失败: {e}")

    def _on_save_config(self):
        """保存配置"""
        try:
            # 选择保存位置
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存配置文件",
                "config/config.json",
                "配置文件 (*.json)"
            )
            
            if not file_path:
                return
                
            # 读取当前配置
            import json
            import os
            config_dir = "config"
            current_config_path = os.path.join(config_dir, "config.json")
            
            if os.path.exists(current_config_path):
                with open(current_config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            else:
                # 如果当前配置不存在，创建默认配置
                config = {
                    "system": {
                        "capture": {
                            "interval": self.capture_interval,
                            "quality": self.capture_quality
                        },
                        "performance": {
                            "interval": self.monitor_interval,
                            "max_history": self.max_history_size
                        }
                    },
                    "game": {
                        "window": {
                            "title": "",
                            "class": ""
                        },
                        "state": {
                            "threshold": self.state_threshold,
                            "auto_save": self.auto_save_state
                        }
                    },
                    "automation": {
                        "action": {
                            "timeout": self.default_timeout,
                            "retry": self.default_retry
                        },
                        "debug": {
                            "save_image": self.save_debug_image,
                            "dir": self.debug_dir
                        }
                    }
                }
                
            # 保存配置文件
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
                
            QMessageBox.information(self, "信息", "配置文件已保存")
            
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.CONFIG_ERROR,
                "保存配置失败",
                ErrorContext(
                    source="MainWindow._on_save_config",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            QMessageBox.critical(self, "错误", f"保存配置失败: {e}")

    def _on_add_state_template(self):
        """添加状态模板"""
        try:
            # 选择模板图片
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择状态模板图片",
                "",
                "图片文件 (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if not file_path:
                return
                
            # 输入状态名称
            state_name, ok = QInputDialog.getText(
                self,
                "添加状态模板",
                "请输入状态名称:"
            )
            
            if not ok or not state_name.strip():
                return
                
            state_name = state_name.strip()
            
            # 检查状态名称是否已存在
            if hasattr(self, 'state_recognizer') and self.state_recognizer:
                if state_name in self.state_recognizer.states:
                    QMessageBox.warning(self, "警告", f"状态模板 '{state_name}' 已存在")
                    return
                    
                # 加载模板
                if self.state_recognizer.load_state_template(state_name, file_path):
                    # 创建状态
                    from src.services.game_state import GameState
                    state = GameState(
                        name=state_name,
                        confidence=0.8,  # 默认阈值80%
                        features={},
                        regions=[],
                        matches=[]
                    )
                    
                    # 注册状态
                    self.state_recognizer.register_state(state)
                    
                    QMessageBox.information(self, "信息", f"状态模板 '{state_name}' 已添加")
                else:
                    QMessageBox.critical(self, "错误", "加载模板图片失败")
            else:
                QMessageBox.warning(self, "警告", "状态识别器未初始化")
                
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "添加状态模板失败",
                ErrorContext(
                    source="MainWindow._on_add_state_template",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            QMessageBox.critical(self, "错误", f"添加状态模板失败: {e}")

    def _on_edit_state_template(self):
        """编辑状态模板"""
        try:
            # 检查状态识别器
            if not hasattr(self, 'state_recognizer') or not self.state_recognizer:
                QMessageBox.warning(self, "警告", "状态识别器未初始化")
                return
                
            # 获取现有状态列表
            states = list(self.state_recognizer.states.keys())
            if not states:
                QMessageBox.information(self, "信息", "没有可编辑的状态模板")
                return
                
            # 选择要编辑的状态
            state_name, ok = QInputDialog.getItem(
                self,
                "编辑状态模板",
                "选择要编辑的状态模板:",
                states,
                0,
                False
            )
            
            if not ok or not state_name:
                return
                
            # 选择新的模板图片
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择新的模板图片",
                "",
                "图片文件 (*.png *.jpg *.jpeg *.bmp)"
            )
            
            if not file_path:
                return
                
            # 更新模板
            if self.state_recognizer.load_state_template(state_name, file_path):
                # 更新状态信息
                state = self.state_recognizer.states.get(state_name)
                if state:
                    # 可以在这里添加更多的编辑选项，比如修改阈值
                    threshold, ok = QInputDialog.getDouble(
                        self,
                        "设置阈值",
                        "请输入匹配阈值 (0.0-1.0):",
                        state.confidence,
                        0.0,
                        1.0,
                        2
                    )
                    
                    if ok:
                        state.confidence = threshold
                        
                QMessageBox.information(self, "信息", f"状态模板 '{state_name}' 已更新")
            else:
                QMessageBox.critical(self, "错误", "更新模板图片失败")
                
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "编辑状态模板失败",
                ErrorContext(
                    source="MainWindow._on_edit_state_template",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            QMessageBox.critical(self, "错误", f"编辑状态模板失败: {e}")

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
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 更新自动化状态
                if self.is_automation_running:
                    self._on_stop_automation()
                    
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "管理自动化失败",
                ErrorContext(
                    source="MainWindow._on_manage_automation",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)

    def _on_manage_templates(self):
        """管理状态模板处理"""
        try:
            # 创建模板管理对话框
            dialog = TemplateManagerDialog(self.state_recognizer, self.error_handler, self)
            
            # 显示对话框
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 更新状态显示
                if self.current_state:
                    self._update_state_display(self.current_state)
                    
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "管理状态模板失败",
                ErrorContext(
                    source="MainWindow._on_manage_templates",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)

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
            # 窗口服务 - 使用统一配置系统
            from src.services.logger import GameLogger
            
            # 使用统一配置实例
            game_logger = GameLogger(self.config, "MainWindow_Services")
            
            self.window_manager = GameWindowManager(game_logger, self.config, self.error_handler)
            self.window_capture = WindowCapture(game_logger)
            
            # 视觉服务
            self.image_processor = ImageProcessor(game_logger, self.config, self.error_handler)
            self.template_matcher = TemplateMatcher(self.error_handler)
            self.state_recognizer = StateRecognizer(self.error_handler)
            
            # 自动化服务
            self.auto_controller = AutoController(self.error_handler)
            
            # 监控服务
            self.performance_monitor = PerformanceMonitor("游戏")
            
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.INIT_ERROR,
                "初始化服务失败",
                ErrorContext(
                    source="MainWindow._init_services",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
    def _init_config_defaults(self):
        """初始化配置默认值（使用统一配置系统）"""
        try:
            if self.container:
                # 使用新架构的配置（字典格式）
                window_config = self.config.get('window', {})
                self.capture_interval = window_config.get('capture_interval', 100)
                self.capture_quality = window_config.get('capture_quality', 80)
                
                # 获取性能配置
                performance_config = self.config.get('performance', {})
                self.monitor_interval = performance_config.get('monitor_interval', 1000)
                self.max_history_size = performance_config.get('max_history', 1000)
                
                # 获取游戏状态配置
                game_state_config = self.config.get('game_state', {})
                self.state_threshold = game_state_config.get('threshold', 80)
                self.auto_save_state = game_state_config.get('auto_save', False)
                
                # 获取自动化配置
                automation_config = self.config.get('automation', {})
                self.default_timeout = automation_config.get('default_timeout', 5)
                self.default_retry = automation_config.get('default_retry', 3)
                
                # 获取调试配置
                self.save_debug_image = automation_config.get('save_debug_image', False)
                self.debug_dir = automation_config.get('debug_dir', 'debug')
            else:
                # 使用传统架构的配置对象
                window_config = self.config.get_window_config()
                self.capture_interval = window_config.get('capture_interval', 100)
                self.capture_quality = window_config.get('capture_quality', 80)
                
                # 获取性能配置
                performance_config = self.config.get_performance_config()
                self.monitor_interval = performance_config.get('monitor_interval', 1000)
                self.max_history_size = performance_config.get('max_history', 1000)
                
                # 获取游戏状态配置
                game_state_config = self.config.get_game_state_config()
                self.state_threshold = game_state_config.get('threshold', 80)
                self.auto_save_state = game_state_config.get('auto_save', False)
                
                # 获取自动化配置
                automation_config = self.config.get_automation_config()
                self.default_timeout = automation_config.get('default_timeout', 5)
                self.default_retry = automation_config.get('default_retry', 3)
                
                # 获取调试配置
                self.save_debug_image = automation_config.get('save_debug_image', False)
                self.debug_dir = automation_config.get('debug_dir', 'debug')
            
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.CONFIG_ERROR,
                "初始化配置默认值失败",
                ErrorContext(
                    source="MainWindow._init_config_defaults",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
    def _on_manage_config(self):
        """配置管理处理"""
        try:
            dialog = ConfigManagerDialog(self.error_handler, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 重新加载配置默认值
                self._init_config_defaults()
                self._update_timers()
                
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "配置管理失败",
                ErrorContext(
                    source="MainWindow._on_manage_config",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
    def _on_show_performance(self):
        """显示性能监控对话框"""
        try:
            # 创建性能监控对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("性能监控")
            dialog.setModal(False)  # 非模态对话框，允许同时操作主窗口
            dialog.resize(800, 600)
            
            # 设置对话框布局
            layout = QVBoxLayout(dialog)
            layout.addWidget(self.performance_view)
            
            # 显示对话框
            dialog.show()
            
        except Exception as e:
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.UI_ERROR,
                "显示性能监控失败",
                ErrorContext(
                    source="MainWindow._on_show_performance",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)
            
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
            from src.common.error_types import GameAutomationError
            error = GameAutomationError(
                ErrorCode.TIMER_ERROR,
                "更新定时器失败",
                ErrorContext(
                    source="MainWindow._update_timers",
                    details={"error_info": str(e)}
                )
            )
            self.error_handler.handle_error(error)

if __name__ == "__main__":
    # 直接运行GUI窗口（开发和调试用）
    # 建议使用: python main.py --gui
    import sys
    from PyQt6.QtWidgets import QApplication
    
    try:
        # 导入统一配置系统
        from src.common.app_config import init_application_metadata, setup_application_properties
        from src.services.config import config
        
        app = QApplication(sys.argv)
        
        # 初始化应用元数据
        init_application_metadata()
        
        # 获取应用配置
        app_config = config.get_application_config()
        
        # 设置应用属性
        setup_application_properties(
            window_title=app_config.get('window_title', '游戏自动操作工具'),
            window_size=tuple(app_config.get('window_size', [800, 600])),
            theme=app_config.get('theme', 'default')
        )
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"GUI窗口启动失败: {e}")
        print("建议使用统一启动器: python main.py --gui")
        sys.exit(1)
