"""
配置管理对话框
"""
from typing import Optional, Dict
import json
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QTabWidget, QWidget, QFormLayout,
                           QSpinBox, QLineEdit, QCheckBox, QGroupBox,
                           QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt

from src.services.error_handler import ErrorHandler
from src.common.error_types import ErrorCode, ErrorContext

class ConfigManagerDialog(QDialog):
    """配置管理对话框"""
    
    def __init__(self, error_handler: ErrorHandler, parent=None):
        """初始化
        
        Args:
            error_handler: 错误处理器
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.error_handler = error_handler
        self.config_dir = "config"
        self.config_file = "config.json"
        
        self._init_ui()
        self._load_config()
        
    def _init_ui(self):
        """初始化UI"""
        # 设置窗口属性
        self.setWindowTitle("配置管理")
        self.setMinimumSize(600, 400)
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 系统配置
        system_tab = QWidget()
        system_layout = QFormLayout(system_tab)
        
        # 捕获设置
        capture_group = QGroupBox("捕获设置")
        capture_layout = QFormLayout(capture_group)
        
        self.capture_interval = QSpinBox()
        self.capture_interval.setRange(10, 1000)
        self.capture_interval.setValue(100)
        self.capture_interval.setSuffix(" ms")
        capture_layout.addRow("捕获间隔:", self.capture_interval)
        
        self.capture_quality = QSpinBox()
        self.capture_quality.setRange(1, 100)
        self.capture_quality.setValue(80)
        self.capture_quality.setSuffix("%")
        capture_layout.addRow("图像质量:", self.capture_quality)
        
        system_layout.addRow(capture_group)
        
        # 性能设置
        performance_group = QGroupBox("性能设置")
        performance_layout = QFormLayout(performance_group)
        
        self.monitor_interval = QSpinBox()
        self.monitor_interval.setRange(100, 10000)
        self.monitor_interval.setValue(1000)
        self.monitor_interval.setSuffix(" ms")
        performance_layout.addRow("监控间隔:", self.monitor_interval)
        
        self.max_history_size = QSpinBox()
        self.max_history_size.setRange(100, 10000)
        self.max_history_size.setValue(1000)
        performance_layout.addRow("最大历史记录:", self.max_history_size)
        
        system_layout.addRow(performance_group)
        
        tab_widget.addTab(system_tab, "系统配置")
        
        # 游戏配置
        game_tab = QWidget()
        game_layout = QFormLayout(game_tab)
        
        # 窗口设置
        window_group = QGroupBox("窗口设置")
        window_layout = QFormLayout(window_group)
        
        self.window_title = QLineEdit()
        window_layout.addRow("窗口标题:", self.window_title)
        
        self.window_class = QLineEdit()
        window_layout.addRow("窗口类名:", self.window_class)
        
        game_layout.addRow(window_group)
        
        # 状态设置
        state_group = QGroupBox("状态设置")
        state_layout = QFormLayout(state_group)
        
        self.state_threshold = QSpinBox()
        self.state_threshold.setRange(0, 100)
        self.state_threshold.setValue(80)
        self.state_threshold.setSuffix("%")
        state_layout.addRow("状态阈值:", self.state_threshold)
        
        self.auto_save_state = QCheckBox()
        state_layout.addRow("自动保存状态:", self.auto_save_state)
        
        game_layout.addRow(state_group)
        
        tab_widget.addTab(game_tab, "游戏配置")
        
        # 自动化配置
        auto_tab = QWidget()
        auto_layout = QFormLayout(auto_tab)
        
        # 动作设置
        action_group = QGroupBox("动作设置")
        action_layout = QFormLayout(action_group)
        
        self.default_timeout = QSpinBox()
        self.default_timeout.setRange(1, 100)
        self.default_timeout.setValue(5)
        self.default_timeout.setSuffix(" s")
        action_layout.addRow("默认超时:", self.default_timeout)
        
        self.default_retry = QSpinBox()
        self.default_retry.setRange(0, 100)
        self.default_retry.setValue(3)
        action_layout.addRow("默认重试:", self.default_retry)
        
        auto_layout.addRow(action_group)
        
        # 调试设置
        debug_group = QGroupBox("调试设置")
        debug_layout = QFormLayout(debug_group)
        
        self.save_debug_image = QCheckBox()
        debug_layout.addRow("保存调试图像:", self.save_debug_image)
        
        self.debug_dir = QLineEdit()
        self.debug_dir.setText("debug")
        debug_layout.addRow("调试目录:", self.debug_dir)
        
        auto_layout.addRow(debug_group)
        
        tab_widget.addTab(auto_tab, "自动化配置")
        
        # 创建对话框按钮
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self._on_save_config)
        button_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
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
                        self.capture_interval.setValue(capture.get("interval", 100))
                        self.capture_quality.setValue(capture.get("quality", 80))
                        
                    if "performance" in system:
                        performance = system["performance"]
                        self.monitor_interval.setValue(performance.get("interval", 1000))
                        self.max_history_size.setValue(performance.get("max_history", 1000))
                        
                # 游戏配置
                if "game" in config:
                    game = config["game"]
                    if "window" in game:
                        window = game["window"]
                        self.window_title.setText(window.get("title", ""))
                        self.window_class.setText(window.get("class", ""))
                        
                    if "state" in game:
                        state = game["state"]
                        self.state_threshold.setValue(state.get("threshold", 80))
                        self.auto_save_state.setChecked(state.get("auto_save", False))
                        
                # 自动化配置
                if "automation" in config:
                    auto = config["automation"]
                    if "action" in auto:
                        action = auto["action"]
                        self.default_timeout.setValue(action.get("timeout", 5))
                        self.default_retry.setValue(action.get("retry", 3))
                        
                    if "debug" in auto:
                        debug = auto["debug"]
                        self.save_debug_image.setChecked(debug.get("save_image", False))
                        self.debug_dir.setText(debug.get("dir", "debug"))
                        
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.CONFIG_ERROR,
                "加载配置失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="ConfigManagerDialog._load_config"
                )
            )
            
    def _on_save_config(self):
        """保存配置处理"""
        try:
            # 创建配置
            config = {
                "system": {
                    "capture": {
                        "interval": self.capture_interval.value(),
                        "quality": self.capture_quality.value()
                    },
                    "performance": {
                        "interval": self.monitor_interval.value(),
                        "max_history": self.max_history_size.value()
                    }
                },
                "game": {
                    "window": {
                        "title": self.window_title.text(),
                        "class": self.window_class.text()
                    },
                    "state": {
                        "threshold": self.state_threshold.value(),
                        "auto_save": self.auto_save_state.isChecked()
                    }
                },
                "automation": {
                    "action": {
                        "timeout": self.default_timeout.value(),
                        "retry": self.default_retry.value()
                    },
                    "debug": {
                        "save_image": self.save_debug_image.isChecked(),
                        "dir": self.debug_dir.text()
                    }
                }
            }
            
            # 保存配置
            config_path = os.path.join(self.config_dir, self.config_file)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
                
            # 关闭对话框
            self.accept()
            
        except Exception as e:
            self.error_handler.handle_error(
                ErrorCode.CONFIG_ERROR,
                "保存配置失败",
                ErrorContext(
                    error_info=str(e),
                    error_location="ConfigManagerDialog._on_save_config"
                )
            ) 