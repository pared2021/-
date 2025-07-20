"""
控制面板组件
用于控制游戏自动化的各项功能
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
                           QFrame, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Tuple, Optional

class ControlPanel(QWidget):
    """控制面板组件
    
    用于控制游戏自动化的各项功能，包括：
    1. 窗口选择和管理
    2. 自动化控制
    3. 参数调整
    """
    
    # 信号
    window_selected = pyqtSignal(int)  # 窗口被选中时发出信号
    refresh_clicked = pyqtSignal()  # 刷新按钮被点击时发出信号
    analyze_clicked = pyqtSignal()  # 分析按钮被点击时发出信号
    start_clicked = pyqtSignal()  # 开始按钮被点击时发出信号
    stop_clicked = pyqtSignal()  # 停止按钮被点击时发出信号
    
    def __init__(self, parent=None):
        """初始化控制面板
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setObjectName("controlPanel")
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 窗口选择部分
        window_group = QFrame()
        window_group.setObjectName("windowGroup")
        window_layout = QVBoxLayout(window_group)
        window_layout.setSpacing(5)
        
        window_label = QLabel("游戏窗口:")
        window_label.setObjectName("windowLabel")
        self.window_combo = QComboBox()
        self.window_combo.setObjectName("windowCombo")
        self.window_combo.currentIndexChanged.connect(self._on_window_changed)
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.refresh_clicked)
        
        window_layout.addWidget(window_label)
        window_layout.addWidget(self.window_combo)
        window_layout.addWidget(self.refresh_button)
        layout.addWidget(window_group)
        
        # 自动化控制部分
        automation_group = QFrame()
        automation_group.setObjectName("automationGroup")
        automation_layout = QVBoxLayout(automation_group)
        automation_layout.setSpacing(5)
        
        automation_label = QLabel("自动化控制:")
        automation_label.setObjectName("automationLabel")
        self.analyze_button = QPushButton("分析游戏状态")
        self.analyze_button.setObjectName("analyzeButton")
        self.analyze_button.clicked.connect(self.analyze_clicked)
        
        self.start_button = QPushButton("开始自动化")
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self.start_clicked)
        
        self.stop_button = QPushButton("停止自动化")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.clicked.connect(self.stop_clicked)
        self.stop_button.setEnabled(False)
        
        automation_layout.addWidget(automation_label)
        automation_layout.addWidget(self.analyze_button)
        automation_layout.addWidget(self.start_button)
        automation_layout.addWidget(self.stop_button)
        layout.addWidget(automation_group)
        
        # 参数调整部分
        params_group = QFrame()
        params_group.setObjectName("paramsGroup")
        params_layout = QGridLayout(params_group)
        params_layout.setSpacing(5)
        
        # 速度控制
        speed_label = QLabel("速度:")
        speed_label.setObjectName("speedLabel")
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setObjectName("speedSpin")
        self.speed_spin.setRange(0.1, 10.0)
        self.speed_spin.setValue(1.0)
        self.speed_spin.setSingleStep(0.1)
        
        # 延迟控制
        delay_label = QLabel("延迟(ms):")
        delay_label.setObjectName("delayLabel")
        self.delay_spin = QSpinBox()
        self.delay_spin.setObjectName("delaySpin")
        self.delay_spin.setRange(0, 1000)
        self.delay_spin.setValue(100)
        self.delay_spin.setSingleStep(10)
        
        params_layout.addWidget(speed_label, 0, 0)
        params_layout.addWidget(self.speed_spin, 0, 1)
        params_layout.addWidget(delay_label, 1, 0)
        params_layout.addWidget(self.delay_spin, 1, 1)
        layout.addWidget(params_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 设置样式
        self.setStyleSheet("""
            QFrame#windowGroup, QFrame#automationGroup, QFrame#paramsGroup {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
            }
            QLabel {
                color: #212121;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        
    def _on_window_changed(self, index: int):
        """窗口选择改变事件
        
        Args:
            index: 选中的索引
        """
        if index >= 0:
            hwnd = self.window_combo.currentData()
            self.window_selected.emit(hwnd)
            
    def set_window_list(self, windows: List[Tuple[int, str]]):
        """设置窗口列表
        
        Args:
            windows: 窗口列表，每个元素为(句柄, 标题)的元组
        """
        current_text = self.window_combo.currentText()
        self.window_combo.clear()
        
        for hwnd, title in windows:
            self.window_combo.addItem(title, hwnd)
            
        # 恢复之前的选择
        index = self.window_combo.findText(current_text)
        if index >= 0:
            self.window_combo.setCurrentIndex(index)
            
    def get_selected_window(self) -> Optional[int]:
        """获取选中的窗口句柄
        
        Returns:
            Optional[int]: 窗口句柄，如果没有选中则返回None
        """
        return self.window_combo.currentData()
        
    def set_automation_running(self, running: bool):
        """设置自动化运行状态
        
        Args:
            running: 是否正在运行
        """
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.window_combo.setEnabled(not running)
        self.refresh_button.setEnabled(not running)
        self.analyze_button.setEnabled(not running)
        
    def get_speed(self) -> float:
        """获取速度设置
        
        Returns:
            float: 速度值
        """
        return self.speed_spin.value()
        
    def get_delay(self) -> int:
        """获取延迟设置
        
        Returns:
            int: 延迟值（毫秒）
        """
        return self.delay_spin.value() 