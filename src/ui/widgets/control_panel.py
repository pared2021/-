from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
                           QFrame, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt

class ControlPanel(QWidget):
    """控制面板组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.window_combo = QComboBox()
        self.window_combo.setObjectName("windowCombo")
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setObjectName("refreshButton")
        
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
        self.analyze_button = QPushButton("分析游戏状态")
        self.analyze_button.setObjectName("analyzeButton")
        self.start_button = QPushButton("开始自动化")
        self.start_button.setObjectName("startButton")
        self.stop_button = QPushButton("停止自动化")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.setEnabled(False)
        
        automation_layout.addWidget(automation_label)
        automation_layout.addWidget(self.analyze_button)
        automation_layout.addWidget(self.start_button)
        automation_layout.addWidget(self.stop_button)
        layout.addWidget(automation_group)
        
        # 添加弹性空间
        layout.addStretch()
        
    def set_window_list(self, windows):
        """设置窗口列表"""
        current_text = self.window_combo.currentText()
        self.window_combo.clear()
        
        for hwnd, title in windows:
            self.window_combo.addItem(title, hwnd)
            
        # 恢复之前的选择
        index = self.window_combo.findText(current_text)
        if index >= 0:
            self.window_combo.setCurrentIndex(index)
            
    def get_selected_window(self):
        """获取选中的窗口"""
        return self.window_combo.currentData()
        
    def set_automation_running(self, running):
        """设置自动化运行状态"""
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.window_combo.setEnabled(not running)
        self.refresh_button.setEnabled(not running)
        self.analyze_button.setEnabled(not running) 