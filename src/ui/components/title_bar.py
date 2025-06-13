from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class TitleBar(QFrame):
    """标题栏组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # 图标
        icon_label = QLabel()
        icon_pixmap = QPixmap(":/resources/icon.png")
        icon_label.setPixmap(icon_pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(icon_label)
        
        # 标题
        title = QLabel("游戏自动化工具")
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        layout.addWidget(title)
        layout.addStretch()
        
        # 控制按钮
        button_data = [
            ("—", self.parent.showMinimized, "minimizeButton", "最小化"),
            ("□", self.parent.toggle_maximize, "maximizeButton", "最大化"),
            ("×", self.parent.close, "closeButton", "关闭")
        ]
        
        for text, slot, obj_name, tooltip in button_data:
            btn = QPushButton(text)
            btn.setObjectName(obj_name)
            btn.setFixedSize(30, 30)
            btn.setToolTip(tooltip)
            btn.clicked.connect(slot)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #ffffff;
                    border: none;
                    font-size: 16px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
                #closeButton:hover {
                    background-color: #e81123;
                }
            """)
            layout.addWidget(btn)
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        self.mousePressEvent = self.parent.title_bar_mouse_press
        self.mouseMoveEvent = self.parent.title_bar_mouse_move
        self.mouseDoubleClickEvent = self.parent.title_bar_double_click 