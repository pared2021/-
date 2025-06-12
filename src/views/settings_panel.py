from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QSpinBox, QCheckBox, QFileDialog
)
from PyQt6.QtCore import pyqtSignal
import json
import os

class SettingsPanel(QWidget):
    """设置面板"""
    
    settings_changed = pyqtSignal(dict)  # 设置变更信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = {}
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout()
        
        # 自动保存设置
        self.auto_save = QCheckBox("自动保存设置")
        self.auto_save.setChecked(True)
        
        # 模型设置
        model_layout = QHBoxLayout()
        self.model_label = QLabel("模型路径:")
        self.model_path = QLabel("未选择")
        self.select_model_button = QPushButton("选择模型")
        self.select_model_button.clicked.connect(self.select_model)
        model_layout.addWidget(self.model_label)
        model_layout.addWidget(self.model_path)
        model_layout.addWidget(self.select_model_button)
        
        # 置信度阈值设置
        confidence_layout = QHBoxLayout()
        self.confidence_label = QLabel("置信度阈值:")
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(1, 100)
        self.confidence_spin.setValue(70)
        self.confidence_spin.setSuffix("%")
        confidence_layout.addWidget(self.confidence_label)
        confidence_layout.addWidget(self.confidence_spin)
        
        # 保存和加载按钮
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存设置")
        self.save_button.clicked.connect(self.save_settings)
        self.load_button = QPushButton("加载设置")
        self.load_button.clicked.connect(self.load_settings)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        
        # 添加到布局
        layout.addWidget(self.auto_save)
        layout.addLayout(model_layout)
        layout.addLayout(confidence_layout)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def select_model(self):
        """选择模型文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择模型文件",
            "",
            "PyTorch模型 (*.pt *.pth);;所有文件 (*.*)"
        )
        
        if file_path:
            self.model_path.setText(file_path)
            self.settings['model_path'] = file_path
            if self.auto_save.isChecked():
                self.save_settings()
                
    def save_settings(self):
        """保存设置"""
        try:
            # 检查控件是否还存在
            if not self.auto_save or not self.model_path or not self.confidence_spin:
                return
                
            self.settings.update({
                'auto_save': self.auto_save.isChecked(),
                'model_path': self.model_path.text(),
                'confidence_threshold': self.confidence_spin.value() / 100.0
            })
            
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存设置失败: {e}")
            
    def load_settings(self):
        """加载设置"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                    
                self.auto_save.setChecked(self.settings.get('auto_save', True))
                self.model_path.setText(self.settings.get('model_path', '未选择'))
                self.confidence_spin.setValue(int(self.settings.get('confidence_threshold', 0.7) * 100))
                
        except Exception as e:
            print(f"加载设置失败: {e}")
            
    def get_settings(self):
        """获取当前设置"""
        return self.settings 