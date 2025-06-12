from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar, QStatusBar
from PyQt6.QtCore import Qt

class StatusBar(QStatusBar):
    """状态栏组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        self.setObjectName("statusGroup")
        
        # 添加状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("statusLabel")
        self.addWidget(self.status_label, 1)  # 1表示可拉伸
        
        # 添加进度条
        self.template_progress = QProgressBar()
        self.template_progress.setObjectName("templateProgress")
        self.template_progress.setRange(0, 100)
        self.template_progress.setValue(0)
        self.template_progress.setFormat("模板收集进度: %p%")
        self.template_progress.setFixedWidth(200)
        self.addPermanentWidget(self.template_progress)
        
        self.model_progress = QProgressBar()
        self.model_progress.setObjectName("modelProgress")
        self.model_progress.setRange(0, 100)
        self.model_progress.setValue(0)
        self.model_progress.setFormat("模型训练进度: %p%")
        self.model_progress.setFixedWidth(200)
        self.addPermanentWidget(self.model_progress)
        
    def update_status(self, status: str):
        """更新状态信息"""
        self.status_label.setText(status)
        if "错误" in status:
            self.status_label.setProperty("state", "error")
        elif "成功" in status:
            self.status_label.setProperty("state", "success")
        elif "警告" in status:
            self.status_label.setProperty("state", "warning")
        else:
            self.status_label.setProperty("state", "normal")
            
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        
    def update_template_progress(self, progress: int):
        """更新模板收集进度"""
        self.template_progress.setValue(progress)
        
    def update_model_progress(self, progress: int):
        """更新模型训练进度"""
        self.model_progress.setValue(progress) 