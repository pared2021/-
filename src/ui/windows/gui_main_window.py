"""
主窗口界面
使用PyQt6实现GUI界面
"""
import sys
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QProgressBar,
    QMessageBox,
    QSplitter,
    QToolBar,
    QStatusBar,
    QFileDialog,
    QDockWidget,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QAction
import logging
import json
import os
from pathlib import Path

from core.resource_manager import ResourceManager
from core.task_system import TaskScheduler, Task, TaskPriority, TaskStatus
from core.error_handler import ErrorHandler
from core.game_adapter import GameAdapter
from macro.macro_recorder import MacroRecorder
from macro.macro_player import MacroPlayer
from macro.macro_editor import MacroEditor
from editor.script_editor import ScriptEditor
from editor.code_formatter import CodeFormatter
from editor.project_manager import ProjectManager
from performance.performance_monitor import PerformanceMonitor
from performance.performance_view import PerformanceView


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("游戏自动化工具")
        self.setMinimumSize(1200, 800)

        # 初始化组件
        self.resource_manager = ResourceManager("config/resource.json")
        self.task_scheduler = TaskScheduler(self.resource_manager)
        self.error_handler = ErrorHandler("logs/snapshots")
        self.game_adapters: Dict[str, GameAdapter] = {}

        # 初始化新组件
        self.macro_recorder = MacroRecorder()
        self.macro_player = MacroPlayer()
        self.macro_editor = MacroEditor()
        self.code_formatter = CodeFormatter()
        self.project_manager = ProjectManager()
        self.performance_monitor = None  # 在选择游戏后初始化

        # 创建UI
        self._create_ui()
        self._create_toolbar()
        self._create_statusbar()
        self._create_docks()

        # 启动监控
        self.resource_manager.start_monitoring()
        self.task_scheduler.start()

        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_status)
        self.update_timer.start(1000)  # 每秒更新一次

    def _create_ui(self):
        """创建UI界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QHBoxLayout(central_widget)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧控制面板
        control_panel = self._create_control_panel()
        splitter.addWidget(control_panel)

        # 中间编辑区域
        edit_panel = self._create_edit_panel()
        splitter.addWidget(edit_panel)

        # 右侧状态面板
        status_panel = self._create_status_panel()
        splitter.addWidget(status_panel)

        # 设置分割比例
        splitter.setSizes([200, 600, 400])

        main_layout.addWidget(splitter)

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # 文件操作
        new_action = QAction("新建项目", self)
        new_action.triggered.connect(self._on_new_project)
        toolbar.addAction(new_action)

        open_action = QAction("打开项目", self)
        open_action.triggered.connect(self._on_open_project)
        toolbar.addAction(open_action)

        save_action = QAction("保存", self)
        save_action.triggered.connect(self._on_save)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # 宏操作
        record_action = QAction("录制宏", self)
        record_action.triggered.connect(self._on_record_macro)
        toolbar.addAction(record_action)

        play_action = QAction("播放宏", self)
        play_action.triggered.connect(self._on_play_macro)
        toolbar.addAction(play_action)

        toolbar.addSeparator()

        # 代码操作
        format_action = QAction("格式化代码", self)
        format_action.triggered.connect(self._on_format_code)
        toolbar.addAction(format_action)

        check_action = QAction("代码检查", self)
        check_action.triggered.connect(self._on_check_code)
        toolbar.addAction(check_action)

    def _create_statusbar(self):
        """创建状态栏"""
        statusbar = QStatusBar()
        self.setStatusBar(statusbar)

        # CPU使用率
        self.cpu_label = QLabel("CPU: 0%")
        statusbar.addPermanentWidget(self.cpu_label)

        # 内存使用
        self.memory_label = QLabel("内存: 0MB")
        statusbar.addPermanentWidget(self.memory_label)

        # FPS
        self.fps_label = QLabel("FPS: 0")
        statusbar.addPermanentWidget(self.fps_label)

    def _create_docks(self):
        """创建停靠窗口"""
        # 项目浏览器
        project_dock = QDockWidget("项目", self)
        project_dock.setWidget(self._create_project_browser())
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, project_dock)

        # 性能监控
        performance_dock = QDockWidget("性能监控", self)
        self.performance_view = PerformanceView()
        performance_dock.setWidget(self.performance_view)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, performance_dock)

    def _create_control_panel(self) -> QWidget:
        """创建控制面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 游戏选择
        game_group = QWidget()
        game_layout = QHBoxLayout(game_group)
        game_layout.addWidget(QLabel("选择游戏:"))
        self.game_combo = QComboBox()
        self.game_combo.currentTextChanged.connect(self._on_game_changed)
        game_layout.addWidget(self.game_combo)
        layout.addWidget(game_group)

        # 任务控制
        task_group = QWidget()
        task_layout = QHBoxLayout(task_group)
        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self._on_start_clicked)
        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self._on_stop_clicked)
        task_layout.addWidget(self.start_button)
        task_layout.addWidget(self.stop_button)
        layout.addWidget(task_group)

        # 宏控制
        macro_group = QWidget()
        macro_layout = QHBoxLayout(macro_group)
        self.record_button = QPushButton("录制")
        self.record_button.clicked.connect(self._on_record_macro)
        self.play_button = QPushButton("播放")
        self.play_button.clicked.connect(self._on_play_macro)
        macro_layout.addWidget(self.record_button)
        macro_layout.addWidget(self.play_button)
        layout.addWidget(macro_group)

        return panel

    def _create_edit_panel(self) -> QWidget:
        """创建编辑面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 创建标签页
        tabs = QTabWidget()

        # 脚本编辑器
        self.script_editor = ScriptEditor()
        tabs.addTab(self.script_editor, "脚本编辑器")

        # 宏编辑器
        macro_editor_widget = QWidget()
        macro_layout = QVBoxLayout(macro_editor_widget)
        self.macro_tree = QTreeWidget()
        self.macro_tree.setHeaderLabels(["时间", "类型", "数据"])
        macro_layout.addWidget(self.macro_tree)
        tabs.addTab(macro_editor_widget, "宏编辑器")

        # 配置编辑器
        self.config_editor = QTextEdit()
        self.config_editor.setFont(QFont("Consolas", 10))
        tabs.addTab(self.config_editor, "配置编辑器")

        layout.addWidget(tabs)
        return panel

    def _create_status_panel(self) -> QWidget:
        """创建状态面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # 创建标签页
        tabs = QTabWidget()

        # 资源监控标签页
        resource_tab = self._create_resource_tab()
        tabs.addTab(resource_tab, "资源监控")

        # 任务状态标签页
        task_tab = self._create_task_tab()
        tabs.addTab(task_tab, "任务状态")

        # 错误日志标签页
        log_tab = self._create_log_tab()
        tabs.addTab(log_tab, "错误日志")

        layout.addWidget(tabs)
        return panel

    def _create_project_browser(self) -> QWidget:
        """创建项目浏览器"""
        browser = QTreeWidget()
        browser.setHeaderLabels(["项目文件"])
        browser.itemDoubleClicked.connect(self._on_file_double_clicked)
        return browser

    def _update_status(self):
        """更新状态显示"""
        # 更新资源使用
        stats = self.resource_manager.get_resource_stats()

        if "cpu" in stats:
            cpu_value = int(stats["cpu"]["current"])
            self.cpu_bar.setValue(cpu_value)
            self.cpu_label.setText(f"CPU: {cpu_value}%")

        if "memory" in stats:
            memory_mb = stats["memory"]["current"]
            memory_percent = (
                memory_mb / self.resource_manager.resource_limit.max_memory_mb * 100
            )
            self.memory_bar.setValue(int(memory_percent))
            self.memory_label.setText(f"内存: {memory_mb:.1f}MB")

        # 更新性能监控
        if self.performance_monitor:
            metrics = self.performance_monitor.get_current_metrics()
            if metrics:
                self.fps_label.setText(f"FPS: {metrics.fps:.1f}")

        # 更新任务状态
        self._update_task_tree()

    def _update_task_tree(self):
        """更新任务树"""
        self.task_tree.clear()

        for task in self.task_scheduler.get_tasks():
            item = QTreeWidgetItem(
                [task.name, task.status.name, task.priority.name, str(task.retry_count)]
            )
            self.task_tree.addTopLevelItem(item)

    def _on_game_changed(self, game_name: str):
        """游戏选择改变"""
        if game_name in self.game_adapters:
            adapter = self.game_adapters[game_name]

            # 更新性能监控
            if self.performance_monitor:
                self.performance_monitor.stop()
            self.performance_monitor = PerformanceMonitor(adapter.window_title)
            self.performance_monitor.start()

            # 加载游戏配置
            self.config_editor.setPlainText(
                json.dumps(adapter.get_config(), indent=2, ensure_ascii=False)
            )

    def _on_new_project(self):
        """新建项目"""
        path, _ = QFileDialog.getSaveFileName(
            self, "新建项目", "", "Python Projects (*.pyproj);;All Files (*.*)"
        )

        if path:
            try:
                project_path = Path(path).parent
                project_name = Path(path).stem
                self.project_manager.create_project(project_path, project_name)
                self._update_project_tree()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建项目失败: {str(e)}")

    def _on_open_project(self):
        """打开项目"""
        path = QFileDialog.getExistingDirectory(self, "打开项目")

        if path:
            try:
                self.project_manager.open_project(Path(path))
                self._update_project_tree()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"打开项目失败: {str(e)}")

    def _update_project_tree(self):
        """更新项目树"""
        if not self.project_manager.current_project:
            return

        project_files = self.project_manager.get_project_files()

        # 清空树
        browser = self.findChild(QTreeWidget)
        if not browser:
            return
        browser.clear()

        # 创建根节点
        root = QTreeWidgetItem([self.project_manager.current_project.path.name])
        browser.addTopLevelItem(root)

        # 添加文件
        for file in project_files:
            rel_path = file.relative_to(self.project_manager.current_project.path)
            parts = rel_path.parts

            # 创建目录节点
            current = root
            for i, part in enumerate(parts[:-1]):
                # 查找是否已存在
                found = False
                for j in range(current.childCount()):
                    child = current.child(j)
                    if child.text(0) == part:
                        current = child
                        found = True
                        break

                if not found:
                    current = QTreeWidgetItem(current, [part])

            # 添加文件节点
            QTreeWidgetItem(current, [parts[-1]])

        # 展开根节点
        root.setExpanded(True)

    def _on_file_double_clicked(self, item: QTreeWidgetItem, column: int):
        """双击文件"""
        if not item.parent():  # 根节点
            return

        # 构建完整路径
        path_parts = []
        current = item
        while current:
            path_parts.insert(0, current.text(0))
            current = current.parent()

        file_path = self.project_manager.current_project.path.joinpath(*path_parts)

        if file_path.exists() and file_path.is_file():
            # 在脚本编辑器中打开
            self.script_editor.load_file(str(file_path))

            # 记录最近文件
            self.project_manager.add_recent_file(file_path)

    def _on_save(self):
        """保存当前文件"""
        self.script_editor.save_file()

    def _on_record_macro(self):
        """录制宏"""
        if self.macro_recorder.is_recording:
            # 停止录制
            self.macro_recorder.stop()
            self.record_button.setText("录制")

            # 更新宏编辑器
            self._update_macro_tree()
        else:
            # 开始录制
            self.macro_recorder.start()
            self.record_button.setText("停止录制")

    def _update_macro_tree(self):
        """更新宏树"""
        self.macro_tree.clear()

        for event in self.macro_recorder.events:
            item = QTreeWidgetItem(
                [f"{event.timestamp:.3f}", event.type.name, str(event.data)]
            )
            self.macro_tree.addTopLevelItem(item)

    def _on_play_macro(self):
        """播放宏"""
        if not self.macro_recorder.events:
            QMessageBox.warning(self, "警告", "没有可播放的宏")
            return

        if self.macro_player.status == "PLAYING":
            # 停止播放
            self.macro_player.stop()
            self.play_button.setText("播放")
        else:
            # 开始播放
            self.macro_player.load_events(self.macro_recorder.events)
            self.macro_player.start()
            self.play_button.setText("停止播放")

    def _on_format_code(self):
        """格式化代码"""
        code = self.script_editor.toPlainText()
        formatted_code = self.code_formatter.format_code(code)
        self.script_editor.setPlainText(formatted_code)

    def _on_check_code(self):
        """检查代码"""
        code = self.script_editor.toPlainText()

        # 语法检查
        syntax_errors = self.code_formatter.check_syntax(code)
        if syntax_errors:
            QMessageBox.warning(
                self,
                "语法错误",
                "\n".join(f"第{e['line']}行: {e['message']}" for e in syntax_errors),
            )
            return

        # 代码风格检查
        style_issues = self.code_formatter.lint_code(code)
        if style_issues:
            issues_text = "\n".join(
                f"第{i['line']}行: [{i['type']}] {i['message']}" for i in style_issues
            )

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("代码风格问题")
            msg.setText(f"发现{len(style_issues)}个代码风格问题:")
            msg.setDetailedText(issues_text)
            msg.exec()
