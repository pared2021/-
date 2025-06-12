from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class TemplateCollectorWidget(QWidget):
    """模板收集器组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 模板收集控制
        control_layout = QHBoxLayout()
        
        self.collect_button = QPushButton("开始收集")
        self.collect_button.setObjectName("collectButton")
        
        self.analyze_button = QPushButton("分析模板")
        self.analyze_button.setObjectName("analyzeButton")
        
        control_layout.addWidget(self.collect_button)
        control_layout.addWidget(self.analyze_button)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 模板预览区域
        preview_label = QLabel("模板预览")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(preview_label)
        
    def set_collecting(self, collecting: bool):
        """设置收集状态"""
        self.collect_button.setEnabled(not collecting)
        self.analyze_button.setEnabled(not collecting)
        
    def set_analyzing(self, analyzing: bool):
        """设置分析状态"""
        self.collect_button.setEnabled(not analyzing)
        self.analyze_button.setEnabled(not analyzing) 