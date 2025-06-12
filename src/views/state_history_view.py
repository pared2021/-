from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QComboBox, QFrame,
                            QTabWidget, QDateTimeEdit)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from src.models.state_history_model import StateHistoryModel
from PyQt6.QtCore import QDateTime

class StateHistoryView(QWidget):
    """状态历史记录视图"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_model = StateHistoryModel()
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 控制面板
        control_panel = QFrame()
        control_panel.setObjectName("controlPanel")
        control_layout = QHBoxLayout(control_panel)
        control_layout.setSpacing(10)
        
        # 时间范围选择
        time_label = QLabel("时间范围:")
        self.start_time_edit = QDateTimeEdit()
        self.start_time_edit.setDateTime(QDateTime.currentDateTime().addSecs(-3600))
        self.start_time_edit.setCalendarPopup(True)
        
        self.end_time_edit = QDateTimeEdit()
        self.end_time_edit.setDateTime(QDateTime.currentDateTime())
        self.end_time_edit.setCalendarPopup(True)
        
        # 状态选择
        state_label = QLabel("状态:")
        self.state_combo = QComboBox()
        self.state_combo.addItems([
            "生命值", "魔法值", "体力值", "等级", "经验值", 
            "金币", "位置", "状态", "目标", "动作"
        ])
        
        # 查询按钮
        self.query_button = QPushButton("查询")
        self.query_button.setObjectName("queryButton")
        self.query_button.clicked.connect(self._on_query)
        
        # 导出按钮
        self.export_button = QPushButton("导出")
        self.export_button.setObjectName("exportButton")
        self.export_button.clicked.connect(self._on_export)
        
        control_layout.addWidget(time_label)
        control_layout.addWidget(self.start_time_edit)
        control_layout.addWidget(QLabel("至"))
        control_layout.addWidget(self.end_time_edit)
        control_layout.addWidget(state_label)
        control_layout.addWidget(self.state_combo)
        control_layout.addWidget(self.query_button)
        control_layout.addWidget(self.export_button)
        control_layout.addStretch()
        
        layout.addWidget(control_panel)
        
        # 统计信息面板
        stats_panel = QFrame()
        stats_panel.setObjectName("statsPanel")
        stats_layout = QHBoxLayout(stats_panel)
        stats_layout.setSpacing(20)
        
        self.min_label = QLabel("最小值: --")
        self.max_label = QLabel("最大值: --")
        self.avg_label = QLabel("平均值: --")
        self.count_label = QLabel("记录数: --")
        
        stats_layout.addWidget(self.min_label)
        stats_layout.addWidget(self.max_label)
        stats_layout.addWidget(self.avg_label)
        stats_layout.addWidget(self.count_label)
        stats_layout.addStretch()
        
        layout.addWidget(stats_panel)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("historyTabs")
        
        # 表格标签页
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        
        self.table = QTableWidget()
        self.table.setObjectName("historyTable")
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["时间", "状态", "数值"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setAlternatingRowColors(True)
        
        table_layout.addWidget(self.table)
        self.tab_widget.addTab(table_tab, "表格视图")
        
        # 图表标签页
        chart_tab = QWidget()
        chart_layout = QVBoxLayout(chart_tab)
        
        # 创建图表
        self.figure = Figure(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        
        self.tab_widget.addTab(chart_tab, "图表视图")
        
        layout.addWidget(self.tab_widget)
        
    def add_record(self, state: dict):
        """添加状态记录"""
        self.history_model.add_record(state)
        
    def _on_query(self):
        """处理查询请求"""
        state_name = self.state_combo.currentText()
        
        # 获取记录
        records = self.history_model.get_records_by_time_range(self.start_time_edit.dateTime().toPython(), self.end_time_edit.dateTime().toPython())
        filtered_records = [
            record for record in records
            if state_name in record["state"]
        ]
        
        # 更新表格
        self.table.setRowCount(len(filtered_records))
        for i, record in enumerate(filtered_records):
            timestamp = datetime.fromisoformat(record["timestamp"])
            value = record["state"][state_name]
            
            self.table.setItem(i, 0, QTableWidgetItem(str(timestamp)))
            self.table.setItem(i, 1, QTableWidgetItem(state_name))
            self.table.setItem(i, 2, QTableWidgetItem(str(value)))
            
        # 更新图表
        self._update_chart(filtered_records, state_name)
            
    def _update_chart(self, records: list, state_name: str):
        """更新图表"""
        if not records:
            return
            
        # 准备数据
        timestamps = []
        values = []
        for record in records:
            timestamps.append(datetime.fromisoformat(record["timestamp"]))
            try:
                value = float(record["state"][state_name])
                values.append(value)
            except (ValueError, TypeError):
                values.append(0)
                
        # 清除旧图表
        self.figure.clear()
        
        # 创建新图表
        ax = self.figure.add_subplot(111)
        
        # 绘制折线图
        ax.plot(timestamps, values, 'b-', label=state_name)
        
        # 设置图表样式
        ax.set_title(f"{state_name} 变化趋势")
        ax.set_xlabel("时间")
        ax.set_ylabel("数值")
        ax.grid(True)
        ax.legend()
        
        # 自动调整日期显示
        plt.xticks(rotation=45)
        self.figure.tight_layout()
        
        # 刷新画布
        self.canvas.draw()
            
    def _on_export(self):
        """处理导出请求"""
        self.history_model.save_to_file() 