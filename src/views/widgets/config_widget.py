from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QDoubleSpinBox
from PyQt6.QtCore import Qt

class ConfigWidget(QWidget):
    """配置组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 窗口配置
        window_group = QWidget()
        window_layout = QVBoxLayout(window_group)
        window_layout.setSpacing(5)
        
        window_label = QLabel("窗口配置")
        window_layout.addWidget(window_label)
        
        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(QLabel("刷新间隔(ms):"))
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(100, 5000)
        self.refresh_interval_spin.setValue(1000)
        refresh_layout.addWidget(self.refresh_interval_spin)
        window_layout.addLayout(refresh_layout)
        
        layout.addWidget(window_group)
        
        # 模板配置
        template_group = QWidget()
        template_layout = QVBoxLayout(template_group)
        template_layout.setSpacing(5)
        
        template_label = QLabel("模板配置")
        template_layout.addWidget(template_label)
        
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("收集时间(秒):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(10, 3600)
        self.duration_spin.setValue(300)
        duration_layout.addWidget(self.duration_spin)
        template_layout.addLayout(duration_layout)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("间隔(秒):"))
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 5.0)
        self.interval_spin.setValue(1.0)
        interval_layout.addWidget(self.interval_spin)
        template_layout.addLayout(interval_layout)
        
        layout.addWidget(template_group)
        
        # 游戏状态配置
        state_group = QWidget()
        state_layout = QVBoxLayout(state_group)
        state_layout.setSpacing(5)
        
        state_label = QLabel("游戏状态配置")
        state_layout.addWidget(state_label)
        
        analysis_layout = QHBoxLayout()
        analysis_layout.addWidget(QLabel("分析间隔(ms):"))
        self.analysis_interval_spin = QSpinBox()
        self.analysis_interval_spin.setRange(100, 5000)
        self.analysis_interval_spin.setValue(1000)
        analysis_layout.addWidget(self.analysis_interval_spin)
        state_layout.addLayout(analysis_layout)
        
        layout.addWidget(state_group)
        
        # 保存按钮
        save_button = QPushButton("保存配置")
        save_button.setObjectName("saveButton")
        layout.addWidget(save_button)
        
    def get_window_config(self) -> dict:
        """获取窗口配置"""
        return {
            'refresh_interval': self.refresh_interval_spin.value()
        }
        
    def get_template_config(self) -> dict:
        """获取模板配置"""
        return {
            'duration': self.duration_spin.value(),
            'interval': self.interval_spin.value()
        }
        
    def get_game_state_config(self) -> dict:
        """获取游戏状态配置"""
        return {
            'analysis_interval': self.analysis_interval_spin.value()
        }
        
    def set_window_config(self, config: dict):
        """设置窗口配置"""
        if 'refresh_interval' in config:
            self.refresh_interval_spin.setValue(config['refresh_interval'])
            
    def set_template_config(self, config: dict):
        """设置模板配置"""
        if 'duration' in config:
            self.duration_spin.setValue(config['duration'])
        if 'interval' in config:
            self.interval_spin.setValue(config['interval'])
            
    def set_game_state_config(self, config: dict):
        """设置游戏状态配置"""
        if 'analysis_interval' in config:
            self.analysis_interval_spin.setValue(config['analysis_interval']) 