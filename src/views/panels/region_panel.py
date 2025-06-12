from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

class RegionPanel(QWidget):
    """区域选择面板"""
    
    region_selected = pyqtSignal(str)  # 区域名称
    region_added = pyqtSignal(str)  # 区域添加信号
    region_removed = pyqtSignal(str)  # 区域移除信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout()
        
        # 区域选择下拉框
        self.region_label = QLabel("选择区域:")
        self.region_combo = QComboBox()
        self.region_combo.currentTextChanged.connect(self.on_region_selected)
        
        # 添加区域按钮
        self.add_button = QPushButton("添加区域")
        self.add_button.clicked.connect(self.start_region_selection)
        
        # 删除区域按钮
        self.remove_button = QPushButton("删除区域")
        self.remove_button.clicked.connect(self.remove_selected_region)
        
        # 添加到布局
        layout.addWidget(self.region_label)
        layout.addWidget(self.region_combo)
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def refresh_regions(self, regions):
        """刷新区域列表"""
        current_regions = set([self.region_combo.itemText(i) for i in range(self.region_combo.count())])
        new_regions = set(regions)
        
        # 检测添加的区域
        for region in new_regions - current_regions:
            self.region_added.emit(region)
            
        # 检测移除的区域
        for region in current_regions - new_regions:
            self.region_removed.emit(region)
            
        self.region_combo.clear()
        self.region_combo.addItems(regions)
        
    def on_region_selected(self, name):
        """区域选择回调"""
        if name:
            self.region_selected.emit(name)
            
    def start_region_selection(self):
        """开始区域选择"""
        if self.parent():
            self.parent().start_region_selection()
            
    def remove_selected_region(self):
        """删除选中的区域"""
        if self.parent():
            self.parent().remove_selected_region() 