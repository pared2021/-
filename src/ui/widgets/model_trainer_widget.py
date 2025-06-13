from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import Qt

class ModelTrainerWidget(QWidget):
    """模型训练器组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 模型训练控制
        control_layout = QHBoxLayout()
        
        self.train_button = QPushButton("训练模型")
        self.train_button.setObjectName("trainButton")
        
        self.select_data_button = QPushButton("选择数据集")
        self.select_data_button.setObjectName("selectDataButton")
        
        control_layout.addWidget(self.train_button)
        control_layout.addWidget(self.select_data_button)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 训练信息显示
        info_label = QLabel("训练信息")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
    def set_training(self, training: bool):
        """设置训练状态"""
        self.train_button.setEnabled(not training)
        self.select_data_button.setEnabled(not training)
        
    def select_data_file(self) -> str:
        """选择数据集文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择数据集配置文件",
            "",
            "YAML Files (*.yaml)"
        )
        return file_path 