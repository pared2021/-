from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSpinBox, QListWidget, QFileDialog
)
from PyQt6.QtCore import pyqtSignal

class TemplatePanel(QWidget):
    """模板管理面板"""
    
    template_selected = pyqtSignal(str)  # 模板名称
    start_automation = pyqtSignal()  # 开始自动化信号
    stop_automation = pyqtSignal()  # 停止自动化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.is_running = False  # 是否正在运行
        self.selected_template = None  # 当前选择的模板
        self.status_text = ""  # 状态文本
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout()
        
        # 模板列表
        self.template_label = QLabel("模板列表:")
        self.template_list = QListWidget()
        self.template_list.currentTextChanged.connect(self.on_template_selected)
        
        # 收集设置
        settings_layout = QHBoxLayout()
        
        # 收集时长
        duration_layout = QVBoxLayout()
        self.duration_label = QLabel("收集时长(秒):")
        self.collect_duration = QSpinBox()
        self.collect_duration.setRange(1, 3600)
        self.collect_duration.setValue(60)
        duration_layout.addWidget(self.duration_label)
        duration_layout.addWidget(self.collect_duration)
        
        # 收集间隔
        interval_layout = QVBoxLayout()
        self.interval_label = QLabel("收集间隔(秒):")
        self.collect_interval = QSpinBox()
        self.collect_interval.setRange(1, 60)
        self.collect_interval.setValue(5)
        interval_layout.addWidget(self.interval_label)
        interval_layout.addWidget(self.collect_interval)
        
        settings_layout.addLayout(duration_layout)
        settings_layout.addLayout(interval_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        # 收集按钮
        self.collect_button = QPushButton("开始收集")
        self.collect_button.clicked.connect(self.start_collect_templates)
        
        # 停止收集按钮
        self.stop_collect_button = QPushButton("停止收集")
        self.stop_collect_button.clicked.connect(self.stop_collect_templates)
        self.stop_collect_button.setEnabled(False)
        
        # 分析按钮
        self.analyze_button = QPushButton("分析模板")
        self.analyze_button.clicked.connect(self.analyze_templates)
        
        # 训练按钮
        self.train_button = QPushButton("训练模型")
        self.train_button.clicked.connect(self.train_model)
        
        # 自动化按钮
        self.start_button = QPushButton("开始自动化")
        self.start_button.clicked.connect(self.on_start_clicked)
        self.stop_button = QPushButton("停止自动化")
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.collect_button)
        button_layout.addWidget(self.stop_collect_button)
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.train_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        # 状态标签
        self.status_label = QLabel()
        
        # 添加到布局
        layout.addWidget(self.template_label)
        layout.addWidget(self.template_list)
        layout.addLayout(settings_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def update_templates(self, templates):
        """更新模板列表"""
        self.template_list.clear()
        self.template_list.addItems(templates)
        
    def on_template_selected(self, name):
        """模板选择回调"""
        if name:
            self.selected_template = name
            self.template_selected.emit(name)
            
    def start_collect_templates(self):
        """开始收集模板"""
        if self.parent():
            self.collect_button.setEnabled(False)
            self.stop_collect_button.setEnabled(True)
            self.parent().start_collect_templates()
            
    def stop_collect_templates(self):
        """停止收集模板"""
        if self.parent():
            self.collect_button.setEnabled(True)
            self.stop_collect_button.setEnabled(False)
            self.parent().stop_collect_templates()
            
    def analyze_templates(self):
        """分析模板"""
        if self.parent():
            self.parent().analyze_templates()
            
    def train_model(self):
        """训练模型"""
        if self.parent():
            self.parent().train_model()
            
    def on_start_clicked(self):
        """开始自动化"""
        self.is_running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.start_automation.emit()
        
    def on_stop_clicked(self):
        """停止自动化"""
        self.is_running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stop_automation.emit()
        
    def get_interval(self):
        """获取间隔时间"""
        return self.collect_interval.value()
        
    def update_status(self, text):
        """更新状态文本"""
        if text != self.status_text:
            self.status_text = text
            self.status_label.setText(text) 