from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QPainter, QPixmap

class NavBar(QWidget):
    """导航栏"""
    
    panel_switched = pyqtSignal(int)  # 面板切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 设置导航栏基本样式
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 5px;
                padding: 8px;
                margin: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton:checked {
                background-color: #0078d7;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 20)
        
        # 创建按钮组
        self.button_group = QButtonGroup(self)
        self.button_group.buttonClicked.connect(self.on_button_clicked)
        
        # 创建导航按钮
        buttons = [
            ("窗口", "window.png"),
            ("区域", "region.png"),
            ("模板", "template.png"),
            ("设置", "settings.png")
        ]
        
        for i, (text, icon) in enumerate(buttons):
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setText(text)  # 直接设置按钮文字
            btn.setToolTip(text)  # 保留tooltip
            
            # 尝试加载图标，如果找不到，则只显示文本
            try:
                btn.setIcon(QIcon(f"resources/icons/{icon}"))
                btn.setIconSize(QSize(24, 24))
            except:
                pass  # 如果图标加载失败，只显示文本
            
            btn.setStyleSheet("""
                QPushButton {
                    color: white;
                    font-weight: bold;
                    text-align: center;
                    padding: 8px;
                    margin: 5px;
                    background-color: transparent;
                    border: none;
                    border-radius: 5px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #333333;
                }
                QPushButton:checked {
                    background-color: #0078d7;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
            """)
            
            btn.setFixedSize(80, 45)  # 增加按钮宽度
            layout.addWidget(btn)
            
            # 添加到按钮组
            self.button_group.addButton(btn, i)
            
            # 默认选中第一个按钮
            if i == 0:
                btn.setChecked(True)
        
        layout.addStretch()
        
        self.setLayout(layout)
        self.setFixedWidth(100)  # 增加导航栏宽度
        
    def on_button_clicked(self, button):
        """按钮点击回调"""
        if not button.isChecked():
            button.setChecked(True)
            return
            
        index = self.button_group.id(button)
        if index >= 0:
            self.panel_switched.emit(index) 