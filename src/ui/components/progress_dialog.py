from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class ProgressDialog(QDialog):
    """进度对话框组件"""
    
    # 定义信号
    progress_updated = pyqtSignal(float)  # 进度更新信号
    operation_cancelled = pyqtSignal()  # 操作取消信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        # 设置窗口属性
        self.setWindowTitle("进度")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        self.setFixedSize(300, 150)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QProgressBar {
                border: 1px solid #333333;
                border-radius: 3px;
                text-align: center;
                background-color: #252525;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                border-radius: 2px;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        
        # 创建布局
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标签
        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 创建取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.cancel)
        layout.addWidget(self.cancel_button)
        
        self.setLayout(layout)
        
    def set_message(self, message: str):
        """
        设置消息
        
        Args:
            message: 消息内容
        """
        self.message_label.setText(message)
        
    def set_progress(self, progress: float):
        """
        设置进度
        
        Args:
            progress: 进度值(0-100)
        """
        self.progress_bar.setValue(int(progress))
        self.progress_updated.emit(progress)
        
    def cancel(self):
        """取消操作"""
        self.operation_cancelled.emit()
        self.close()
        
    def closeEvent(self, event):
        """关闭事件"""
        self.operation_cancelled.emit()
        event.accept() 