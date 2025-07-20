"""现代化UI组件"""

import psutil
from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QComboBox, QProgressBar, QScrollArea, QGridLayout, QSpacerItem,
    QSizePolicy, QGraphicsDropShadowEffect, QStackedWidget, QGraphicsBlurEffect
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap, QColor, QPainter, QLinearGradient

from .modern_styles import GAME_THEME_COLORS, LAYOUT_CONSTANTS
from ...services.logger import GameLogger


class ModernCard(QFrame):
    """现代化卡片组件"""
    
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("modernCard")
        from ...services.config import Config
        config = Config()
        self.logger = GameLogger(config, "ModernCard")
        self.title = title
        self._setup_ui()
        self._apply_style()
        
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setObjectName("cardTitle")
            title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
            layout.addWidget(title_label)
            
        # 内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_widget)
        
    def _apply_style(self):
        """应用样式"""
        margin = LAYOUT_CONSTANTS['card_margin']
        radius = LAYOUT_CONSTANTS['border_radius']
        self.setStyleSheet(f"""
            QFrame#modernCard {{
                background: rgba(26, 26, 46, 0.95);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: {radius}px;
                padding: 5px;
                margin: {margin[0]}px {margin[1]}px {margin[2]}px {margin[3]}px;
            }}
            QFrame#modernCard:hover {{
                background: rgba(26, 26, 46, 0.98);
                border-color: rgba(74, 144, 226, 0.8);
            }}
            QLabel#cardTitle {{
                color: #ffffff;
                font-weight: bold;
                margin-bottom: 5px;
            }}
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(LAYOUT_CONSTANTS['shadow_blur'])
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(*LAYOUT_CONSTANTS['shadow_offset'])
        self.setGraphicsEffect(shadow)
        
    def add_content(self, widget: QWidget):
        """添加内容"""
        self.content_layout.addWidget(widget)
        
    def clear_content(self):
        """清空内容"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class ModernButton(QPushButton):
    """现代化按钮组件"""
    
    def __init__(self, text: str = "", button_type: str = "primary", parent=None):
        super().__init__(text, parent)
        from ...services.config import Config
        config = Config()
        self.logger = GameLogger(config, "ModernButton")
        self.button_type = button_type
        self._apply_style()
        self._apply_hover_effect()
        
    def _apply_style(self):
        """应用样式"""
        base_style = """
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 13px;
                min-height: 20px;
                color: white;
            }
            QPushButton:pressed {
                margin-top: 1px;
                margin-bottom: -1px;
            }
            QPushButton:disabled {
                background: rgba(60, 60, 80, 0.5);
                color: rgba(255, 255, 255, 0.4);
            }
        """
        
        type_styles = {
            "primary": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #4a90e2, stop:1 #357abd);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #5ba0f2, stop:1 #4080cd);
                }
            """,
            "success": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #51cf66, stop:1 #40c057);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #61df76, stop:1 #50d067);
                }
            """,
            "warning": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ffd43b, stop:1 #fab005);
                    color: #333;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ffe44b, stop:1 #fbc015);
                }
            """,
            "danger": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ff6b6b, stop:1 #ee5a52);
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ff7b7b, stop:1 #fe6a62);
                }
            """
        }
        
        style = base_style + type_styles.get(self.button_type, type_styles["primary"])
        self.setStyleSheet(style)
        
    def _apply_hover_effect(self):
        """应用悬浮效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
    def enterEvent(self, event):
        """鼠标进入事件"""
        super().enterEvent(event)
        if self.graphicsEffect():
            self.graphicsEffect().setBlurRadius(15)
            self.graphicsEffect().setOffset(0, 4)
            
    def leaveEvent(self, event):
        """鼠标离开事件"""
        super().leaveEvent(event)
        if self.graphicsEffect():
            self.graphicsEffect().setBlurRadius(10)
            self.graphicsEffect().setOffset(0, 2)


class ModernProgressBar(QProgressBar):
    """现代化进度条组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        from ...services.config import Config
        config = Config()
        self.logger = GameLogger(config, "ModernProgressBar")
        self._apply_style()
        self._apply_visual_effects()
        
    def _apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            QProgressBar {
                background: rgba(26, 26, 46, 0.8);
                border: 2px solid rgba(74, 144, 226, 0.3);
                border-radius: 10px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #4a90e2, stop:0.5 #74c0fc, stop:1 #4a90e2);
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
    def _apply_visual_effects(self):
        """应用视觉效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(74, 144, 226, 100))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class ModernControlPanel(QFrame):
    """现代化控制面板"""
    
    # 信号定义
    window_selected = pyqtSignal(str)
    refresh_clicked = pyqtSignal()
    analyze_clicked = pyqtSignal()
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    
    def __init__(self, container=None, parent=None):
        super().__init__(parent)
        self.container = container
        from ...services.config import Config
        config = Config()
        self.logger = GameLogger(config, "ModernControlPanel")
        self.setObjectName("modernControlPanel")
        
        # UI组件
        self.window_combo: Optional[QComboBox] = None
        self.start_button: Optional[ModernButton] = None
        self.stop_button: Optional[ModernButton] = None
        self.status_label: Optional[QLabel] = None
        
        self._setup_ui()
        self._apply_style()
        
    def _setup_ui(self):
        """设置UI布局"""
        layout = QVBoxLayout(self)
        margin = LAYOUT_CONSTANTS['content_margin']
        layout.setContentsMargins(*margin)
        layout.setSpacing(LAYOUT_CONSTANTS['card_spacing'])
        
        # 自动化控制卡片
        control_card = self._create_automation_control_card()
        layout.addWidget(control_card)
        
        # 窗口选择卡片
        window_card = self._create_window_selection_card()
        layout.addWidget(window_card)
        
        # 状态信息卡片
        status_card = self._create_status_info_card()
        layout.addWidget(status_card)
        
        # 参数设置卡片
        params_card = self._create_parameters_card()
        layout.addWidget(params_card)
        
        layout.addStretch()
        
    def _create_window_selection_card(self) -> ModernCard:
        """创建窗口选择卡片"""
        card = ModernCard("🎯 窗口选择")
        
        # 窗口下拉框
        self.window_combo = QComboBox()
        self.window_combo.setStyleSheet("""
            QComboBox {
                background: rgba(26, 26, 46, 0.8);
                border: 2px solid rgba(74, 144, 226, 0.3);
                border-radius: 8px;
                padding: 8px 12px;
                color: #ffffff;
                min-width: 200px;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #4a90e2;
                background: rgba(26, 26, 46, 0.9);
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background: rgba(26, 26, 46, 0.95);
                border: 2px solid rgba(74, 144, 226, 0.5);
                border-radius: 8px;
                color: #ffffff;
                selection-background-color: rgba(74, 144, 226, 0.8);
                padding: 5px;
            }
        """)
        self.window_combo.currentTextChanged.connect(self.window_selected.emit)
        card.add_content(self.window_combo)
        
        # 刷新按钮
        refresh_btn = ModernButton("🔄 刷新窗口列表", "primary")
        refresh_btn.clicked.connect(self.refresh_clicked.emit)
        card.add_content(refresh_btn)
        
        return card
        
    def _create_automation_control_card(self) -> ModernCard:
        """创建自动化控制卡片"""
        card = ModernCard("🤖 自动化控制")
        
        # 分析按钮
        analyze_btn = ModernButton("🔍 分析当前状态", "primary")
        analyze_btn.clicked.connect(self.analyze_clicked.emit)
        card.add_content(analyze_btn)
        
        # 控制按钮布局
        button_layout = QHBoxLayout()
        
        # 开始按钮
        self.start_button = ModernButton("▶️ 开始", "success")
        self.start_button.clicked.connect(self.start_clicked.emit)
        button_layout.addWidget(self.start_button)
        
        # 停止按钮
        self.stop_button = ModernButton("⏹️ 停止", "danger")
        self.stop_button.clicked.connect(self.stop_clicked.emit)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        card.add_content(button_widget)
        
        return card
        
    def _create_status_info_card(self) -> ModernCard:
        """创建状态信息卡片"""
        card = ModernCard("📊 状态信息")
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("""
            QLabel {
                background: rgba(81, 207, 102, 0.2);
                border: 1px solid rgba(81, 207, 102, 0.6);
                border-radius: 6px;
                padding: 8px 12px;
                color: #51cf66;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        card.add_content(self.status_label)
        
        # 统计信息
        stats_layout = QGridLayout()
        
        # 运行时间
        runtime_label = QLabel("运行时间:")
        runtime_value = QLabel("00:00:00")
        stats_layout.addWidget(runtime_label, 0, 0)
        stats_layout.addWidget(runtime_value, 0, 1)
        
        # 执行次数
        count_label = QLabel("执行次数:")
        count_value = QLabel("0")
        stats_layout.addWidget(count_label, 1, 0)
        stats_layout.addWidget(count_value, 1, 1)
        
        # 成功率
        success_label = QLabel("成功率:")
        success_value = QLabel("0%")
        stats_layout.addWidget(success_label, 2, 0)
        stats_layout.addWidget(success_value, 2, 1)
        
        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        card.add_content(stats_widget)
        
        return card
        
    def _create_parameters_card(self) -> ModernCard:
        """创建参数设置卡片"""
        card = ModernCard("⚙️ 参数设置")
        
        # 延迟设置
        delay_layout = QHBoxLayout()
        delay_label = QLabel("操作延迟:")
        delay_combo = QComboBox()
        delay_combo.addItems(["快速 (0.1s)", "正常 (0.5s)", "慢速 (1.0s)"])
        delay_combo.setCurrentIndex(1)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(delay_combo)
        
        delay_widget = QWidget()
        delay_widget.setLayout(delay_layout)
        card.add_content(delay_widget)
        
        # 重试次数
        retry_layout = QHBoxLayout()
        retry_label = QLabel("重试次数:")
        retry_combo = QComboBox()
        retry_combo.addItems(["1次", "3次", "5次", "10次"])
        retry_combo.setCurrentIndex(1)
        retry_layout.addWidget(retry_label)
        retry_layout.addWidget(retry_combo)
        
        retry_widget = QWidget()
        retry_widget.setLayout(retry_layout)
        card.add_content(retry_widget)
        
        return card
        
    def _apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            QFrame#modernControlPanel {
                background: rgba(26, 26, 46, 0.8);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 15px;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
        """)
        
    def set_window_list(self, windows: List[str]):
        """设置窗口列表"""
        if self.window_combo:
            self.window_combo.clear()
            self.window_combo.addItems(windows)
            
    def get_selected_window(self) -> Optional[str]:
        """获取选中的窗口"""
        if self.window_combo:
            return self.window_combo.currentText()
        return None
        
    def set_automation_running(self, running: bool):
        """设置自动化运行状态"""
        if self.start_button and self.stop_button:
            self.start_button.setEnabled(not running)
            self.stop_button.setEnabled(running)
            
        if self.status_label:
            if running:
                self.status_label.setText("运行中")
                self.status_label.setStyleSheet("""
                    QLabel {
                        background: rgba(255, 212, 59, 0.2);
                        border: 1px solid rgba(255, 212, 59, 0.6);
                        border-radius: 6px;
                        padding: 8px 12px;
                        color: #ffd43b;
                        font-weight: bold;
                        font-size: 13px;
                    }
                """)
            else:
                self.status_label.setText("就绪")
                self.status_label.setStyleSheet("""
                    QLabel {
                        background: rgba(81, 207, 102, 0.2);
                        border: 1px solid rgba(81, 207, 102, 0.6);
                        border-radius: 6px;
                        padding: 8px 12px;
                        color: #51cf66;
                        font-weight: bold;
                        font-size: 13px;
                    }
                """)


class ModernGameView(QLabel):
    """现代化游戏视图"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernGameView")
        self._setup_ui()
        self._apply_style()
        
    def _setup_ui(self):
        """设置UI"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setText("🎮\n\n等待游戏画面...")
        
        # 存储当前帧数据
        self._current_frame = None
        
    def _apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            QLabel#modernGameView {
                background: rgba(0, 0, 0, 0.8);
                border: 2px solid rgba(74, 144, 226, 0.5);
                border-radius: 15px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
    def update_frame(self, frame):
        """更新画面"""
        # 保存当前帧
        self._current_frame = frame
        
        if frame is None:
            self.setText("🎮\n\n等待游戏画面...")
            return
            
        # 如果收到布尔值或其他非数组类型，处理错误
        if not hasattr(frame, 'shape') or not hasattr(frame, 'size'):
            self.setText(f"🎮\n\n画面格式错误: {type(frame)}")
            return
            
        if frame.size == 0:
            self.setText("🎮\n\n画面数据为空")
            return
            
        try:
            import cv2
            import numpy as np
            from PyQt6.QtGui import QImage, QPixmap
            
            # 确保图像是RGB格式 (OpenCV使用BGR)
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # 转换BGR到RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                # 尝试处理其他类型的图像
                if len(frame.shape) == 2:  # 灰度图
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
                elif len(frame.shape) == 3 and frame.shape[2] == 4:  # BGRA
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                else:
                    rgb_frame = frame  # 直接使用，可能会出现颜色问题
                
            # 转换图像为Qt图像
            height, width = rgb_frame.shape[:2]
            bytes_per_line = 3 * width
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            
            # 缩放图像以适应标签大小
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
        except Exception as e:
            self.setText(f"❌\n\n画面更新错误:\n{str(e)}")
    
    def get_current_frame(self):
        """获取当前帧数据
        
        Returns:
            当前帧的numpy数组，如果没有则返回None
        """
        return self._current_frame
            
    def resizeEvent(self, event):
        """重写大小改变事件，保持图像比例
        
        Args:
            event: 大小改变事件
        """
        super().resizeEvent(event)
        if self.pixmap():
            scaled_pixmap = self.pixmap().scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)


class ModernStatusPanel(QFrame):
    """现代化状态面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("modernStatusPanel")
        from ...services.config import Config
        config = Config()
        self.logger = GameLogger(config, "ModernStatusPanel")
        
        # UI组件
        self.cpu_progress: Optional[ModernProgressBar] = None
        self.memory_progress: Optional[ModernProgressBar] = None
        self.fps_label: Optional[QLabel] = None
        
        self._setup_ui()
        self._apply_style()
        
    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        margin = LAYOUT_CONSTANTS['content_margin']
        layout.setContentsMargins(*margin)
        layout.setSpacing(LAYOUT_CONSTANTS['card_spacing'])
        
        # 系统性能卡片
        performance_card = self._create_performance_card()
        layout.addWidget(performance_card)
        
        # 游戏状态卡片
        game_status_card = self._create_game_status_card()
        layout.addWidget(game_status_card)
        
        # 日志卡片
        log_card = self._create_log_card()
        layout.addWidget(log_card)
        
        layout.addStretch()
        
    def _create_performance_card(self) -> ModernCard:
        """创建性能监控卡片"""
        card = ModernCard("📊 系统性能")
        
        # CPU使用率
        cpu_layout = QVBoxLayout()
        cpu_label = QLabel("CPU使用率")
        self.cpu_progress = ModernProgressBar()
        self.cpu_progress.setRange(0, 100)
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_progress)
        
        cpu_widget = QWidget()
        cpu_widget.setLayout(cpu_layout)
        card.add_content(cpu_widget)
        
        # 内存使用率
        memory_layout = QVBoxLayout()
        memory_label = QLabel("内存使用率")
        self.memory_progress = ModernProgressBar()
        self.memory_progress.setRange(0, 100)
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self.memory_progress)
        
        memory_widget = QWidget()
        memory_widget.setLayout(memory_layout)
        card.add_content(memory_widget)
        
        # FPS显示
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("""
            QLabel {
                background: rgba(116, 192, 252, 0.2);
                border: 1px solid rgba(116, 192, 252, 0.6);
                border-radius: 6px;
                padding: 8px 12px;
                color: #74c0fc;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
            }
        """)
        card.add_content(self.fps_label)
        
        return card
        
    def _create_game_status_card(self) -> ModernCard:
        """创建游戏状态卡片"""
        card = ModernCard("🎯 游戏状态")
        
        # 状态信息网格
        status_layout = QGridLayout()
        
        # 当前场景
        scene_label = QLabel("当前场景:")
        scene_value = QLabel("未知")
        status_layout.addWidget(scene_label, 0, 0)
        status_layout.addWidget(scene_value, 0, 1)
        
        # 角色状态
        character_label = QLabel("角色状态:")
        character_value = QLabel("正常")
        status_layout.addWidget(character_label, 1, 0)
        status_layout.addWidget(character_value, 1, 1)
        
        # 任务进度
        task_label = QLabel("任务进度:")
        task_value = QLabel("0/0")
        status_layout.addWidget(task_label, 2, 0)
        status_layout.addWidget(task_value, 2, 1)
        
        status_widget = QWidget()
        status_widget.setLayout(status_layout)
        card.add_content(status_widget)
        
        return card
        
    def _create_log_card(self) -> ModernCard:
        """创建日志卡片"""
        card = ModernCard("📝 运行日志")
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: rgba(26, 26, 46, 0.6);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 8px;
            }
        """)
        
        # 日志内容
        log_content = QLabel("系统启动完成\n等待用户操作...")
        log_content.setWordWrap(True)
        log_content.setAlignment(Qt.AlignmentFlag.AlignTop)
        log_content.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.9);
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 10px;
            }
        """)
        
        scroll_area.setWidget(log_content)
        card.add_content(scroll_area)
        
        return card
        
    def _apply_style(self):
        """应用样式"""
        self.setStyleSheet("""
            QFrame#modernStatusPanel {
                background: rgba(26, 26, 46, 0.85);
                border: 1px solid rgba(74, 144, 226, 0.3);
                border-radius: 15px;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
        """)
        
    def update_system_stats(self):
        """更新系统统计信息"""
        try:
            # 更新CPU使用率
            cpu_percent = psutil.cpu_percent(interval=None)
            if self.cpu_progress:
                self.cpu_progress.setValue(int(cpu_percent))
                
            # 更新内存使用率
            memory = psutil.virtual_memory()
            if self.memory_progress:
                self.memory_progress.setValue(int(memory.percent))
                
            # 更新FPS（模拟）
            if self.fps_label:
                self.fps_label.setText(f"FPS: {30}")
                
        except Exception as e:
            self.logger.error(f"Failed to update system stats: {e}")