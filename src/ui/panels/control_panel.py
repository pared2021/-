from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSpinBox, QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import cv2
import numpy as np
import os

class ControlPanel(QWidget):
    """控制面板"""
    
    # 定义信号
    start_automation = pyqtSignal()
    stop_automation = pyqtSignal()
    template_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.is_running = False
        self.selected_template = None
        
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 模板选择区域
        template_layout = QHBoxLayout()
        self.template_label = QLabel("选择模板:")
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(self.on_template_selected)
        template_layout.addWidget(self.template_label)
        template_layout.addWidget(self.template_combo)
        layout.addLayout(template_layout)
        
        # 点击间隔设置
        interval_layout = QHBoxLayout()
        self.interval_label = QLabel("点击间隔(秒):")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(5)
        interval_layout.addWidget(self.interval_label)
        interval_layout.addWidget(self.interval_spin)
        layout.addLayout(interval_layout)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("开始")
        self.stop_button = QPushButton("停止")
        self.start_button.clicked.connect(self.on_start_clicked)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # 状态显示
        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
    def on_template_selected(self, template_name):
        """模板选择回调"""
        self.selected_template = template_name
        self.template_selected.emit(template_name)
        
    def on_start_clicked(self):
        """开始按钮点击回调"""
        if not self.selected_template:
            self.status_label.setText("请先选择模板")
            return
            
        self.is_running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("运行中...")
        self.start_automation.emit()
        
    def on_stop_clicked(self):
        """停止按钮点击回调"""
        self.is_running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("已停止")
        self.stop_automation.emit()
        
    def update_templates(self, templates):
        """更新模板列表"""
        self.template_combo.clear()
        for template in templates:
            self.template_combo.addItem(template)
            
    def get_interval(self):
        """获取点击间隔"""
        return self.interval_spin.value()
        
    def update_status(self, status):
        """更新状态显示"""
        self.status_label.setText(status) 