from PyQt6.QtWidgets import QGroupBox, QGridLayout, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

class GameStateWidget(QGroupBox):
    """游戏状态组件"""
    
    def __init__(self, parent=None):
        super().__init__("游戏状态", parent)
        self.state_labels = {}
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        self.setObjectName("gameState")
        state_layout = QGridLayout()
        state_layout.setSpacing(5)
        
        states = {
            "生命值": {"unit": "%", "critical": 20, "warning": 50, "icon": "❤️"},
            "魔法值": {"unit": "%", "critical": 10, "warning": 30, "icon": "🔮"},
            "体力值": {"unit": "%", "critical": 15, "warning": 40, "icon": "⚡"},
            "等级": {"unit": "", "critical": None, "warning": None, "icon": "⭐"},
            "经验值": {"unit": "%", "critical": None, "warning": None, "icon": "📈"},
            "金币": {"unit": "", "critical": None, "warning": None, "icon": "💰"},
            "位置": {"unit": "", "critical": None, "warning": None, "icon": "📍"},
            "状态": {"unit": "", "critical": None, "warning": None, "icon": "🎯"},
            "目标": {"unit": "", "critical": None, "warning": None, "icon": "🎯"},
            "动作": {"unit": "", "critical": None, "warning": None, "icon": "🎮"},
            "战斗状态": {"unit": "", "critical": None, "warning": None, "icon": "⚔️"},
            "增益效果": {"unit": "", "critical": None, "warning": None, "icon": "✨"},
            "减益效果": {"unit": "", "critical": None, "warning": None, "icon": "💀"},
            "背包空间": {"unit": "%", "critical": 90, "warning": 70, "icon": "🎒"},
            "任务进度": {"unit": "%", "critical": None, "warning": None, "icon": "📋"}
        }
        
        for i, (state, config) in enumerate(states.items()):
            # 创建状态标签容器
            state_container = QWidget()
            state_container.setObjectName("stateContainer")
            state_container_layout = QHBoxLayout(state_container)
            state_container_layout.setContentsMargins(0, 0, 0, 0)
            state_container_layout.setSpacing(5)
            
            # 添加图标标签
            icon_label = QLabel(config["icon"])
            icon_label.setObjectName("stateIcon")
            state_container_layout.addWidget(icon_label)
            
            # 添加状态名称标签
            name_label = QLabel(f"{state}:")
            name_label.setObjectName("stateName")
            state_container_layout.addWidget(name_label)
            
            # 添加状态值标签
            value_label = QLabel("未知")
            value_label.setObjectName("stateValue")
            state_container_layout.addWidget(value_label)
            
            # 保存状态信息
            self.state_labels[state] = {
                "container": state_container,
                "value_label": value_label,
                "unit": config["unit"],
                "critical": config["critical"],
                "warning": config["warning"],
                "icon": config["icon"]
            }
            
            # 计算行和列
            row = i // 2
            col = i % 2
            state_layout.addWidget(state_container, row, col)
            
        self.setLayout(state_layout)
        
    def update_state(self, state: dict):
        """更新游戏状态"""
        for key, value in state.items():
            if key in self.state_labels:
                label_info = self.state_labels[key]
                value_label = label_info["value_label"]
                unit = label_info["unit"]
                container = label_info["container"]
                
                # 尝试将值转换为浮点数
                try:
                    float_value = float(value)
                    self._update_state_label_style(key, float_value)
                    value_label.setText(f"{value}{unit}")
                except (ValueError, TypeError):
                    value_label.setText(str(value))
                    
    def _update_state_label_style(self, state_name: str, value: float):
        """更新状态标签样式"""
        if state_name in self.state_labels:
            label_info = self.state_labels[state_name]
            container = label_info["container"]
            critical = label_info["critical"]
            warning = label_info["warning"]
            
            # 设置状态样式
            if critical is not None and value <= critical:
                container.setProperty("state", "critical")
            elif warning is not None and value <= warning:
                container.setProperty("state", "warning")
            else:
                container.setProperty("state", "good")
                
            # 更新样式
            container.style().unpolish(container)
            container.style().polish(container) 