"""
状态历史视图
用于显示游戏状态的历史记录
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen
import numpy as np
from typing import List, Dict, Any
import time

class StateHistoryView(QFrame):
    """状态历史视图
    
    用于显示游戏状态的历史记录，包括：
    1. 状态变化趋势图
    2. 状态详细信息
    3. 状态统计信息
    """
    
    # 信号
    state_selected = pyqtSignal(dict)  # 状态被选中时发出信号
    
    def __init__(self, parent=None):
        """初始化状态历史视图
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setObjectName("stateHistoryView")
        self.setMinimumHeight(200)
        
        # 状态历史数据
        self.states: List[Dict[str, Any]] = []
        self.max_states = 100  # 最大显示状态数
        
        # 创建UI
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建标题
        title = QLabel("状态历史")
        title.setObjectName("historyTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 创建状态图表
        self.chart = StateChart(self)
        layout.addWidget(self.chart)
        
        # 创建状态列表
        self.state_list = StateList(self)
        layout.addWidget(self.state_list)
        
    def add_state(self, state: Dict[str, Any]):
        """添加新状态
        
        Args:
            state: 状态数据
        """
        # 添加时间戳
        state['timestamp'] = time.time()
        
        # 添加到历史记录
        self.states.append(state)
        
        # 限制历史记录数量
        if len(self.states) > self.max_states:
            self.states.pop(0)
            
        # 更新图表和列表
        self.chart.update_states(self.states)
        self.state_list.update_states(self.states)
        
    def clear_states(self):
        """清空状态历史"""
        self.states.clear()
        self.chart.update_states([])
        self.state_list.update_states([])
        
    def get_statistics(self) -> Dict[str, float]:
        """获取状态统计信息
        
        Returns:
            Dict[str, float]: 统计信息
        """
        if not self.states:
            return {
                'min': 0,
                'max': 0,
                'avg': 0,
                'count': 0
            }
            
        # 提取状态值
        values = [state.get('value', 0) for state in self.states]
        
        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }


class StateChart(QFrame):
    """状态图表
    
    用于绘制状态变化趋势图
    """
    
    def __init__(self, parent=None):
        """初始化状态图表
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setObjectName("stateChart")
        self.setMinimumHeight(100)
        
        # 状态数据
        self.states: List[Dict[str, Any]] = []
        
    def update_states(self, states: List[Dict[str, Any]]):
        """更新状态数据
        
        Args:
            states: 状态数据列表
        """
        self.states = states
        self.update()
        
    def paintEvent(self, event):
        """绘制事件
        
        Args:
            event: 绘制事件
        """
        super().paintEvent(event)
        
        if not self.states:
            return
            
        # 创建画笔
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置画笔
        pen = QPen(QColor("#2196F3"))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # 获取绘图区域
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        # 计算数据范围
        values = [state.get('value', 0) for state in self.states]
        min_value = min(values)
        max_value = max(values)
        value_range = max_value - min_value if max_value > min_value else 1
        
        # 绘制曲线
        points = []
        for i, state in enumerate(self.states):
            x = i * width / (len(self.states) - 1) if len(self.states) > 1 else width / 2
            y = height - (state.get('value', 0) - min_value) * height / value_range
            points.append((x, y))
            
        # 绘制连线
        for i in range(len(points) - 1):
            painter.drawLine(
                int(points[i][0]), int(points[i][1]),
                int(points[i + 1][0]), int(points[i + 1][1])
            )


class StateList(QScrollArea):
    """状态列表
    
    用于显示状态详细信息
    """
    
    def __init__(self, parent=None):
        """初始化状态列表
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.setObjectName("stateList")
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 创建内容窗口
        self.content = QWidget()
        self.setWidget(self.content)
        
        # 创建布局
        self.layout = QVBoxLayout(self.content)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(2, 2, 2, 2)
        
        # 状态数据
        self.states: List[Dict[str, Any]] = []
        
    def update_states(self, states: List[Dict[str, Any]]):
        """更新状态数据
        
        Args:
            states: 状态数据列表
        """
        self.states = states
        
        # 清空现有项目
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # 添加新项目
        for state in reversed(self.states):  # 最新的状态显示在最上面
            item = StateItem(state, self)
            self.layout.addWidget(item)
            
        # 添加弹性空间
        self.layout.addStretch() 