"""
性能监控可视化界面
提供实时图表显示、历史数据查看和性能报告生成功能
"""
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QSpinBox,
    QGroupBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen
import pyqtgraph as pg
import numpy as np
from datetime import datetime
import json
import csv
import logging
from pathlib import Path

from .performance_monitor import PerformanceMonitor
from ..core.types import UnifiedPerformanceMetrics as PerformanceMetrics


class RealTimeChart(pg.PlotWidget):
    """实时图表"""

    def __init__(self, title: str, y_label: str, parent=None):
        super().__init__(parent)

        # 设置标题和标签
        self.setTitle(title)
        self.setLabel("left", y_label)
        self.setLabel("bottom", "时间 (秒)")

        # 设置图表样式
        self.setBackground("w")
        self.showGrid(x=True, y=True)

        # 数据
        self.times = []
        self.values = []

        # 曲线
        self.curve = self.plot(pen="b")

    def update_data(self, time: float, value: float):
        """更新数据"""
        self.times.append(time)
        self.values.append(value)

        # 保持最近10分钟的数据
        if len(self.times) > 6000:  # 10分钟 * 60秒 * 10采样
            self.times.pop(0)
            self.values.pop(0)

        # 更新曲线
        self.curve.setData(
            [t - self.times[-1] for t in self.times], self.values  # 相对时间
        )


class PerformanceView(QWidget):
    """性能监控视图"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.logger = logging.getLogger("PerformanceView")
        self.monitor: Optional[PerformanceMonitor] = None

        self._create_ui()

        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_charts)

    def _create_ui(self):
        """创建UI"""
        layout = QVBoxLayout(self)

        # 控制面板
        control_group = QGroupBox("控制")
        control_layout = QHBoxLayout(control_group)

        # 目标窗口
        self.window_input = QComboBox()
        self.window_input.setEditable(True)
        self.window_input.setMinimumWidth(200)
        control_layout.addWidget(QLabel("目标窗口:"))
        control_layout.addWidget(self.window_input)

        # 采样间隔
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 1000)
        self.interval_spin.setValue(100)
        self.interval_spin.setSuffix(" ms")
        control_layout.addWidget(QLabel("采样间隔:"))
        control_layout.addWidget(self.interval_spin)

        # 控制按钮
        self.start_button = QPushButton("开始监控")
        self.start_button.clicked.connect(self.start_monitoring)
        control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("停止监控")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)

        control_layout.addStretch()

        # 导出按钮
        self.export_button = QPushButton("导出报告")
        self.export_button.clicked.connect(self.export_report)
        self.export_button.setEnabled(False)
        control_layout.addWidget(self.export_button)

        layout.addWidget(control_group)

        # 图表面板
        charts_tab = QTabWidget()

        # 实时监控
        realtime_widget = QWidget()
        realtime_layout = QVBoxLayout(realtime_widget)

        # CPU使用率图表
        self.cpu_chart = RealTimeChart("CPU使用率", "使用率 (%)")
        realtime_layout.addWidget(self.cpu_chart)

        # 内存使用图表
        self.memory_chart = RealTimeChart("内存使用", "使用率 (%)")
        realtime_layout.addWidget(self.memory_chart)

        # FPS图表
        self.fps_chart = RealTimeChart("帧率", "FPS")
        realtime_layout.addWidget(self.fps_chart)

        # 响应时间图表
        self.response_chart = RealTimeChart("响应时间", "时间 (ms)")
        realtime_layout.addWidget(self.response_chart)

        charts_tab.addTab(realtime_widget, "实时监控")

        # 历史数据
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)

        # 时间范围选择
        range_layout = QHBoxLayout()

        self.range_combo = QComboBox()
        self.range_combo.addItems(["最近1分钟", "最近5分钟", "最近10分钟", "最近30分钟", "最近1小时"])
        self.range_combo.currentIndexChanged.connect(self._update_history)
        range_layout.addWidget(QLabel("时间范围:"))
        range_layout.addWidget(self.range_combo)
        range_layout.addStretch()

        history_layout.addLayout(range_layout)

        # 历史数据表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(
            ["时间", "CPU使用率", "内存使用率", "内存使用量", "FPS", "响应时间"]
        )
        history_layout.addWidget(self.history_table)

        charts_tab.addTab(history_widget, "历史数据")

        # 统计分析
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)

        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(5)
        self.stats_table.setRowCount(4)
        self.stats_table.setVerticalHeaderLabels(["CPU使用率", "内存使用率", "FPS", "响应时间"])
        self.stats_table.setHorizontalHeaderLabels(["最小值", "最大值", "平均值", "标准差", "单位"])
        stats_layout.addWidget(self.stats_table)

        charts_tab.addTab(stats_widget, "统计分析")

        layout.addWidget(charts_tab)

    def start_monitoring(self):
        """开始监控"""
        window_title = self.window_input.currentText()
        if not window_title:
            QMessageBox.warning(self, "错误", "请输入目标窗口标题")
            return

        # 创建监控器
        self.monitor = PerformanceMonitor(window_title)
        if not self.monitor.process:
            QMessageBox.warning(self, "错误", f"未找到标题包含 '{window_title}' 的窗口")
            return

        self.monitor.start()

        # 更新UI状态
        self.window_input.setEnabled(False)
        self.interval_spin.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.export_button.setEnabled(True)

        # 启动更新定时器
        self.update_timer.start(self.interval_spin.value())

    def stop_monitoring(self):
        """停止监控"""
        if self.monitor:
            self.monitor.stop()
            self.monitor = None

        # 停止更新定时器
        self.update_timer.stop()

        # 更新UI状态
        self.window_input.setEnabled(True)
        self.interval_spin.setEnabled(True)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _update_charts(self):
        """更新图表"""
        if not self.monitor:
            return

        metrics = self.monitor.get_current_metrics()
        if not metrics:
            return

        # 更新实时图表
        self.cpu_chart.update_data(metrics.timestamp, metrics.cpu_percent)
        self.memory_chart.update_data(metrics.timestamp, metrics.memory_percent)
        self.fps_chart.update_data(metrics.timestamp, metrics.fps)
        self.response_chart.update_data(metrics.timestamp, metrics.response_time * 1000)

        # 更新历史数据
        self._update_history()

        # 更新统计信息
        self._update_statistics()

    def _update_history(self):
        """更新历史数据"""
        if not self.monitor:
            return

        # 获取时间范围
        range_text = self.range_combo.currentText()
        if range_text == "最近1分钟":
            duration = 60
        elif range_text == "最近5分钟":
            duration = 300
        elif range_text == "最近10分钟":
            duration = 600
        elif range_text == "最近30分钟":
            duration = 1800
        else:  # 最近1小时
            duration = 3600

        metrics = self.monitor.get_metrics_history(duration)

        # 更新表格
        self.history_table.setRowCount(len(metrics))
        for i, m in enumerate(metrics):
            self.history_table.setItem(
                i,
                0,
                QTableWidgetItem(
                    datetime.fromtimestamp(m.timestamp).strftime("%H:%M:%S")
                ),
            )
            self.history_table.setItem(i, 1, QTableWidgetItem(f"{m.cpu_percent:.1f}%"))
            self.history_table.setItem(
                i, 2, QTableWidgetItem(f"{m.memory_percent:.1f}%")
            )
            self.history_table.setItem(
                i, 3, QTableWidgetItem(f"{m.memory_used / 1024 / 1024:.1f} MB")
            )
            self.history_table.setItem(i, 4, QTableWidgetItem(f"{m.fps:.1f}"))
            self.history_table.setItem(
                i, 5, QTableWidgetItem(f"{m.response_time * 1000:.1f} ms")
            )

    def _update_statistics(self):
        """更新统计信息"""
        if not self.monitor:
            return

        stats = self.monitor.get_statistics()

        # CPU使用率
        row = 0
        self.stats_table.setItem(row, 0, QTableWidgetItem(f"{stats['cpu']['min']:.1f}"))
        self.stats_table.setItem(row, 1, QTableWidgetItem(f"{stats['cpu']['max']:.1f}"))
        self.stats_table.setItem(row, 2, QTableWidgetItem(f"{stats['cpu']['avg']:.1f}"))
        self.stats_table.setItem(row, 3, QTableWidgetItem(f"{stats['cpu']['std']:.1f}"))
        self.stats_table.setItem(row, 4, QTableWidgetItem("%"))

        # 内存使用率
        row = 1
        self.stats_table.setItem(
            row, 0, QTableWidgetItem(f"{stats['memory']['min']:.1f}")
        )
        self.stats_table.setItem(
            row, 1, QTableWidgetItem(f"{stats['memory']['max']:.1f}")
        )
        self.stats_table.setItem(
            row, 2, QTableWidgetItem(f"{stats['memory']['avg']:.1f}")
        )
        self.stats_table.setItem(
            row, 3, QTableWidgetItem(f"{stats['memory']['std']:.1f}")
        )
        self.stats_table.setItem(row, 4, QTableWidgetItem("%"))

        # FPS
        row = 2
        self.stats_table.setItem(row, 0, QTableWidgetItem(f"{stats['fps']['min']:.1f}"))
        self.stats_table.setItem(row, 1, QTableWidgetItem(f"{stats['fps']['max']:.1f}"))
        self.stats_table.setItem(row, 2, QTableWidgetItem(f"{stats['fps']['avg']:.1f}"))
        self.stats_table.setItem(row, 3, QTableWidgetItem(f"{stats['fps']['std']:.1f}"))
        self.stats_table.setItem(row, 4, QTableWidgetItem("FPS"))

        # 响应时间
        row = 3
        self.stats_table.setItem(
            row, 0, QTableWidgetItem(f"{stats['response_time']['min']*1000:.1f}")
        )
        self.stats_table.setItem(
            row, 1, QTableWidgetItem(f"{stats['response_time']['max']*1000:.1f}")
        )
        self.stats_table.setItem(
            row, 2, QTableWidgetItem(f"{stats['response_time']['avg']*1000:.1f}")
        )
        self.stats_table.setItem(
            row, 3, QTableWidgetItem(f"{stats['response_time']['std']*1000:.1f}")
        )
        self.stats_table.setItem(row, 4, QTableWidgetItem("ms"))

    def export_report(self):
        """导出性能报告"""
        if not self.monitor:
            return

        # 选择保存位置
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "导出报告",
            "",
            "HTML Files (*.html);;CSV Files (*.csv);;JSON Files (*.json)",
        )

        if not filename:
            return

        try:
            # 获取性能数据
            metrics = self.monitor.get_metrics_history()
            stats = self.monitor.get_statistics()

            # 根据文件类型导出
            suffix = Path(filename).suffix.lower()
            if suffix == ".html":
                self._export_html(filename, metrics, stats)
            elif suffix == ".csv":
                self._export_csv(filename, metrics)
            else:  # .json
                self._export_json(filename, metrics, stats)

            QMessageBox.information(self, "成功", "报告导出成功")

        except Exception as e:
            self.logger.error(f"导出报告失败: {e}", exc_info=True)
            QMessageBox.critical(self, "错误", f"导出报告失败: {str(e)}")

    def _export_html(
        self, filename: str, metrics: List[PerformanceMetrics], stats: Dict[str, Any]
    ):
        """导出HTML报告"""
        # TODO: 使用模板生成HTML报告
        pass

    def _export_csv(self, filename: str, metrics: List[PerformanceMetrics]):
        """导出CSV报告"""
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["时间", "CPU使用率(%)", "内存使用率(%)", "内存使用量(MB)", "FPS", "响应时间(ms)"]
            )

            for m in metrics:
                writer.writerow(
                    [
                        datetime.fromtimestamp(m.timestamp).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        f"{m.cpu_percent:.1f}",
                        f"{m.memory_percent:.1f}",
                        f"{m.memory_used / 1024 / 1024:.1f}",
                        f"{m.fps:.1f}",
                        f"{m.response_time * 1000:.1f}",
                    ]
                )

    def _export_json(
        self, filename: str, metrics: List[PerformanceMetrics], stats: Dict[str, Any]
    ):
        """导出JSON报告"""
        data = {
            "metrics": [
                {
                    "timestamp": m.timestamp,
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "memory_used": m.memory_used,
                    "fps": m.fps,
                    "response_time": m.response_time,
                }
                for m in metrics
            ],
            "statistics": stats,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
