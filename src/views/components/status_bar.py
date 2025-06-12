from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

class StatusBar(QStatusBar):
    """状态栏组件"""
    
    # 定义信号
    status_changed = pyqtSignal(str)  # 状态变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        # 设置样式
        self.setStyleSheet("""
            QStatusBar {
                background-color: #252525;
                color: #ffffff;
                border-top: 1px solid #333333;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
        """)
        
        # 创建状态标签
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.addWidget(self.status_label)
        
        # 创建进度标签
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.addPermanentWidget(self.progress_label)
        
    def set_status(self, message: str, timeout: int = 0):
        """
        设置状态消息
        
        Args:
            message: 状态消息
            timeout: 显示时间(毫秒)
        """
        self.status_label.setText(message)
        self.status_changed.emit(message)
        if timeout > 0:
            self.showMessage(message, timeout)
            
    def set_progress(self, progress: float):
        """
        设置进度
        
        Args:
            progress: 进度值(0-100)
        """
        self.progress_label.setText(f"进度: {progress:.1f}%")
        
    def clear_status(self):
        """清除状态消息"""
        self.status_label.clear()
        self.status_changed.emit("")
        
    def clear_progress(self):
        """清除进度"""
        self.progress_label.clear() 