from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QComboBox, QSpinBox, 
                            QDoubleSpinBox, QFileDialog, QFrame, QScrollArea,
                            QProgressBar, QGroupBox, QGridLayout, QMessageBox,
                            QTabWidget, QCheckBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QImage, QPixmap, QIcon
import cv2
import numpy as np
import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from src.services.logger import GameLogger
from src.services.window_manager import GameWindowManager
from src.services.game_analyzer import GameAnalyzer
from src.services.image_processor import ImageProcessor
from src.services.action_simulator import ActionSimulator
from src.services.game_state import GameState
from src.services.config import Config
from src.services.auto_operator import AutoOperator
from src.viewmodels.main_viewmodel import MainViewModel
from src.views.styles import APP_STYLE
from src.views.widgets import (GameView, ControlPanel, StatusBar,
                             GameStateWidget, ConfigWidget)
from src.views.state_history_view import StateHistoryView

class MainWindow(QMainWindow):
    """主窗口视图
    
    负责管理整个应用程序的UI界面，协调各个组件之间的交互。
    
    Attributes:
        logger (GameLogger): 日志记录器
        window_manager (GameWindowManager): 窗口管理器
        game_analyzer (GameAnalyzer): 游戏分析器
        auto_operator (AutoOperator): 自动操作器
        image_processor (ImageProcessor): 图像处理器
        action_simulator (ActionSimulator): 动作模拟器
        game_state (GameState): 游戏状态管理器
        config (Config): 配置管理器
        viewmodel (MainViewModel): 主视图模型
        state_history_view (StateHistoryView): 状态历史视图
        control_panel (ControlPanel): 控制面板
        game_view (GameView): 游戏画面显示
        status_bar (StatusBar): 状态栏
    """
    
    def __init__(self, 
                 logger: GameLogger,
                 window_manager: GameWindowManager,
                 game_analyzer: GameAnalyzer,
                 auto_operator: AutoOperator,
                 image_processor: ImageProcessor,
                 action_simulator: ActionSimulator,
                 game_state: GameState,
                 config: Config):
        """初始化主窗口
        
        Args:
            logger: 日志记录器
            window_manager: 窗口管理器
            game_analyzer: 游戏分析器
            auto_operator: 自动操作器
            image_processor: 图像处理器
            action_simulator: 动作模拟器
            game_state: 游戏状态管理器
            config: 配置管理器
        """
        super().__init__()
        
        # 保存注入的服务
        self.logger: GameLogger = logger
        self.window_manager: GameWindowManager = window_manager
        self.game_analyzer: GameAnalyzer = game_analyzer
        self.auto_operator: AutoOperator = auto_operator
        self.image_processor: ImageProcessor = image_processor
        self.action_simulator: ActionSimulator = action_simulator
        self.game_state: GameState = game_state
        self.config: Config = config
        
        # 创建视图模型
        self.viewmodel: MainViewModel = MainViewModel(
            logger=logger,
            window_manager=window_manager,
            game_analyzer=game_analyzer,
            auto_operator=auto_operator,
            image_processor=image_processor,
            action_simulator=action_simulator,
            game_state=game_state,
            config=config
        )
        
        self.state_history_view: StateHistoryView = StateHistoryView()
        self._init_ui()
        self._connect_signals()
        self._load_last_config()
        self.setStyleSheet(APP_STYLE)
        
    def _load_last_config(self):
        """加载上次的配置"""
        try:
            # 加载上次选择的窗口
            last_window = self.viewmodel.get_last_selected_window()
            if last_window:
                # 查找窗口标题
                for i in range(self.window_combo.count()):
                    if self.window_combo.itemData(i) == last_window:
                        self.window_combo.setCurrentIndex(i)
                        break
        except Exception as e:
            self.logger.error(f"加载配置失败: {str(e)}")
            self.status_bar.update_status(f"加载配置失败: {str(e)}")
        
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("游戏自动操作工具")
        self.setMinimumSize(1400, 900)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # 创建顶部控制栏
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setSpacing(10)
        
        # 游戏窗口选择
        window_label = QLabel("游戏窗口:")
        window_label.setObjectName("windowLabel")
        self.window_combo = QComboBox()
        self.window_combo.setMinimumWidth(200)
        self.refresh_button = QPushButton("刷新窗口")
        self.select_button = QPushButton("选择窗口")
        
        # 控制按钮
        self.start_button = QPushButton("开始")
        self.start_button.setObjectName("startButton")
        self.stop_button = QPushButton("停止")
        self.stop_button.setObjectName("stopButton")
        self.pause_button = QPushButton("暂停")
        self.pause_button.setObjectName("pauseButton")
        
        # 状态显示
        self.status_label = QLabel("状态: 未连接")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        top_layout.addWidget(window_label)
        top_layout.addWidget(self.window_combo)
        top_layout.addWidget(self.refresh_button)
        top_layout.addWidget(self.select_button)
        top_layout.addWidget(self.start_button)
        top_layout.addWidget(self.stop_button)
        top_layout.addWidget(self.pause_button)
        top_layout.addStretch()
        top_layout.addWidget(self.status_label)
        
        main_layout.addWidget(top_bar)
        
        # 创建中间区域
        middle_area = QWidget()
        middle_layout = QHBoxLayout(middle_area)
        middle_layout.setSpacing(5)
        
        # 游戏画面显示
        self.game_view = GameView()
        self.game_view.setObjectName("gameView")
        self.game_view.setText("等待选择游戏窗口...")
        middle_layout.addWidget(self.game_view, 2)  # 游戏画面占据2/3空间
        
        # 右侧功能面板
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_panel.setMinimumWidth(400)  # 设置最小宽度确保功能面板有足够空间
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        
        # 状态历史记录（完整功能）
        self.state_history_view = StateHistoryView()
        self.state_history_view.setObjectName("historyChart")
        right_layout.addWidget(self.state_history_view)
        
        # 统计信息面板
        stats_group = QGroupBox("统计信息")
        stats_layout = QGridLayout(stats_group)
        self.min_label = QLabel("最小值: --")
        self.max_label = QLabel("最大值: --")
        self.avg_label = QLabel("平均值: --")
        self.count_label = QLabel("记录数: --")
        stats_layout.addWidget(self.min_label, 0, 0)
        stats_layout.addWidget(self.max_label, 0, 1)
        stats_layout.addWidget(self.avg_label, 1, 0)
        stats_layout.addWidget(self.count_label, 1, 1)
        right_layout.addWidget(stats_group)
        
        # 控制面板
        control_group = QGroupBox("控制面板")
        control_layout = QGridLayout(control_group)
        
        # 速度控制
        speed_label = QLabel("速度:")
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(1, 10)
        self.speed_spin.setValue(5)
        control_layout.addWidget(speed_label, 0, 0)
        control_layout.addWidget(self.speed_spin, 0, 1)
        
        # 其他控制选项
        self.auto_analyze_check = QCheckBox("自动分析")
        self.auto_save_check = QCheckBox("自动保存")
        control_layout.addWidget(self.auto_analyze_check, 1, 0, 1, 2)
        control_layout.addWidget(self.auto_save_check, 2, 0, 1, 2)
        
        right_layout.addWidget(control_group)
        
        middle_layout.addWidget(right_panel, 1)  # 功能面板占据1/3空间
        
        main_layout.addWidget(middle_area, 1)
        
        # 创建底部状态栏
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)
        
        # 显示初始化状态
        self.status_bar.update_status("程序已启动，请选择游戏窗口")
        
    def _connect_signals(self):
        """连接信号和槽"""
        # 窗口列表更新
        self.viewmodel.window_list_updated.connect(self._update_window_list)
        
        # 画面更新
        self.viewmodel.frame_updated.connect(self.game_view.update_frame)
        
        # 状态更新
        self.viewmodel.status_updated.connect(self.status_bar.update_status)
        self.viewmodel.status_updated.connect(self.status_label.setText)
        
        # 错误处理
        self.viewmodel.error_occurred.connect(self.status_bar.update_status)
        
        # 自动化状态更新
        self.viewmodel.automation_started.connect(self._on_automation_started)
        self.viewmodel.automation_stopped.connect(self._on_automation_stopped)
        
        # 游戏状态更新
        self.viewmodel.game_state_updated.connect(self.state_history_view.add_record)
        
        # 按钮信号
        self.refresh_button.clicked.connect(self.viewmodel.refresh_windows)
        self.select_button.clicked.connect(self._on_select_window)
        self.start_button.clicked.connect(self._on_start_automation)
        self.stop_button.clicked.connect(self.viewmodel.stop_automation)
        self.pause_button.clicked.connect(self._on_pause_automation)
        
        # 速度控制
        self.speed_spin.valueChanged.connect(self._on_speed_changed)
        
        # 自动分析
        self.auto_analyze_check.stateChanged.connect(self._on_auto_analyze_changed)
        
        # 自动保存
        self.auto_save_check.stateChanged.connect(self._on_auto_save_changed)
        
        # 启动时自动刷新窗口列表
        QTimer.singleShot(1000, self.viewmodel.refresh_windows)
        
    def _update_window_list(self, windows: list):
        """更新窗口列表
        
        Args:
            windows: 窗口列表，每个元素是(handle, title)元组
        """
        self.window_combo.clear()
        for handle, title in windows:
            self.window_combo.addItem(title, handle)
            
    def _on_automation_started(self):
        """处理自动化开始事件"""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        self.status_label.setText("状态: 运行中")
        
    def _on_automation_stopped(self):
        """处理自动化停止事件"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.status_label.setText("状态: 已停止")
        
    def _on_select_window(self):
        """处理选择窗口事件"""
        window_handle = self.window_combo.currentData()
        if window_handle:
            self.viewmodel.select_window(window_handle)
            
    def _on_start_automation(self):
        """处理开始自动化事件"""
        self.viewmodel.start_automation()
        
    def _on_pause_automation(self):
        """处理暂停自动化事件"""
        if self.pause_button.text() == "暂停":
            self.viewmodel.pause_automation()
            self.pause_button.setText("继续")
            self.status_label.setText("状态: 已暂停")
        else:
            self.viewmodel.resume_automation()
            self.pause_button.setText("暂停")
            self.status_label.setText("状态: 运行中")
            
    def _on_speed_changed(self, value):
        """处理速度改变事件"""
        self.viewmodel.set_speed(value)
        
    def _on_auto_analyze_changed(self, state):
        """处理自动分析状态改变事件"""
        self.viewmodel.set_auto_analyze(state == Qt.CheckState.Checked)
        
    def _on_auto_save_changed(self, state):
        """处理自动保存状态改变事件"""
        self.viewmodel.set_auto_save(state == Qt.CheckState.Checked)
    
    def show_and_activate(self):
        """显示并激活窗口"""
        self.show()
        self.activateWindow()
        self.raise_()
    
    def refresh_windows(self):
        """刷新窗口列表"""
        self.viewmodel.refresh_windows()
    
    def update_frame(self):
        """更新画面"""
        self.viewmodel.update_frame() 