from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt

class MessageBox(QMessageBox):
    """消息框组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        # 设置样式
        self.setStyleSheet("""
            QMessageBox {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QMessageBox QPushButton:hover {
                background-color: #505050;
            }
        """)
        
    def show_info(self, title: str, message: str):
        """
        显示信息消息
        
        Args:
            title: 标题
            message: 消息内容
        """
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Icon.Information)
        self.exec()
        
    def show_warning(self, title: str, message: str):
        """
        显示警告消息
        
        Args:
            title: 标题
            message: 消息内容
        """
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Icon.Warning)
        self.exec()
        
    def show_error(self, title: str, message: str):
        """
        显示错误消息
        
        Args:
            title: 标题
            message: 消息内容
        """
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Icon.Critical)
        self.exec()
        
    def show_question(self, title: str, message: str) -> bool:
        """
        显示问题消息
        
        Args:
            title: 标题
            message: 消息内容
            
        Returns:
            bool: 用户是否点击了"是"
        """
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(QMessageBox.Icon.Question)
        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return self.exec() == QMessageBox.StandardButton.Yes 