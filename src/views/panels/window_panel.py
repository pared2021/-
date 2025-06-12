from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

class WindowPanel(QWidget):
    """窗口选择面板"""
    
    window_selected = pyqtSignal(int, str)  # 窗口句柄, 标题
    windows_changed = pyqtSignal(list)  # 窗口列表变化信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selecting = False  # 添加防止递归的标志
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout()
        
        # 窗口选择下拉框
        self.window_label = QLabel("选择游戏窗口:")
        self.window_combo = QComboBox()
        self.window_combo.currentIndexChanged.connect(self.on_window_selected)
        
        # 刷新按钮
        self.refresh_button = QPushButton("刷新窗口列表")
        self.refresh_button.clicked.connect(self.refresh_windows)
        
        # 添加到布局
        layout.addWidget(self.window_label)
        layout.addWidget(self.window_combo)
        layout.addWidget(self.refresh_button)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def update_windows(self, windows):
        """更新窗口列表"""
        # 设置标志，防止触发选择信号
        old_selecting = self._selecting
        self._selecting = True
        
        try:
            self.window_combo.clear()
            for hwnd, title in windows:
                self.window_combo.addItem(title, hwnd)
            self.windows_changed.emit(windows)  # 发送窗口列表变化信号
        finally:
            # 恢复原来的标志状态
            self._selecting = old_selecting
            
    def on_window_selected(self, index):
        """窗口选择回调"""
        # 如果是在程序内部更新窗口列表，不触发信号
        if self._selecting:
            return
            
        if index >= 0:
            hwnd = self.window_combo.itemData(index)
            title = self.window_combo.itemText(index)
            # 防止递归，避免同一窗口被重复选择
            # 设置标志表示正在选择
            self._selecting = True
            try:
                self.window_selected.emit(hwnd, title)
            finally:
                # 恢复标志
                self._selecting = False
            
    def refresh_windows(self):
        """刷新窗口列表"""
        # 找到主窗口对象
        main_window = None
        parent = self.parent()
        
        # 向上查找，直到找到MainWindow
        while parent:
            if parent.__class__.__name__ == 'MainWindow':
                main_window = parent
                break
            parent = parent.parent()
        
        if main_window and hasattr(main_window, 'refresh_windows'):
            main_window.refresh_windows() 