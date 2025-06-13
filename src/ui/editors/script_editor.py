"""
脚本编辑器
提供代码编辑和语法高亮功能
"""
import builtins
import keyword
import logging
import re
from typing import Dict, List, Optional, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QTextCharFormat,
    QSyntaxHighlighter,
    QKeySequence,
    QAction,
)
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QSplitter,
    QToolBar,
    QFileDialog,
    QMessageBox,
)

import jedi


class PythonHighlighter(QSyntaxHighlighter):
    """Python语法高亮器"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 语法高亮规则
        self.highlighting_rules = []

        # 关键字格式
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#FF6B8B"))
        keyword_format.setFontWeight(700)

        keywords = keyword.kwlist
        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((pattern, keyword_format))

        # 内置函数格式
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#66D9EF"))

        builtins_list = dir(builtins)
        for word in builtins_list:
            if not word.startswith("_"):
                pattern = r"\b" + word + r"\b"
                self.highlighting_rules.append((pattern, builtin_format))

        # 字符串格式
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#A6E22E"))
        self.highlighting_rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', string_format))
        self.highlighting_rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", string_format))

        # 注释格式
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#75715E"))
        self.highlighting_rules.append((r"#[^\n]*", comment_format))

        # 数字格式
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#AE81FF"))
        self.highlighting_rules.append((r"\b\d+\b", number_format))

        # 类名格式
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#A6E22E"))
        class_format.setFontWeight(700)
        self.highlighting_rules.append((r"\bclass\s+\w+\b", class_format))

        # 函数名格式
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#F92672"))
        self.highlighting_rules.append((r"\bdef\s+\w+\b", function_format))

    def highlightBlock(self, text: str):
        """高亮文本块"""
        for pattern, format in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), format)


class CodeEditor(QTextEdit):
    """代码编辑器"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置字体
        font = QFont("Consolas", 10)
        font.setFixedPitch(True)
        self.setFont(font)

        # 设置制表符宽度
        self.setTabStopDistance(40)

        # 语法高亮
        self.highlighter = PythonHighlighter(self.document())

        # 代码补全
        self.completer = None
        self.completion_prefix = ""

        # 当前文件
        self.current_file = None
        self.modified = False

        # 设置样式
        self.setStyleSheet(
            """
            QTextEdit {
                background-color: #272822;
                color: #F8F8F2;
                border: none;
            }
        """
        )

    def keyPressEvent(self, event):
        """按键事件处理"""
        # Tab键处理
        if event.key() == Qt.Key.Key_Tab:
            cursor = self.textCursor()
            cursor.insertText("    ")
            return

        # 自动缩进
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            indent = re.match(r"^\s*", text).group()

            # 检查是否需要增加缩进
            if text.strip().endswith(":"):
                indent += "    "

            super().keyPressEvent(event)
            cursor.insertText(indent)
            return

        super().keyPressEvent(event)

        # 触发代码补全
        if event.text().isalpha():
            self.show_completions()

    def show_completions(self):
        """显示代码补全"""
        cursor = self.textCursor()
        script = jedi.Script(code=self.toPlainText(), path="")
        completions = script.complete(cursor.blockNumber() + 1, cursor.columnNumber())

        if completions:
            # TODO: 显示补全列表
            pass

    def load_file(self, filename: str):
        """加载文件"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.setPlainText(f.read())
            self.current_file = filename
            self.modified = False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载文件失败: {str(e)}")

    def save_file(self, filename: Optional[str] = None):
        """保存文件"""
        if filename:
            self.current_file = filename

        if not self.current_file:
            return False

        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.toPlainText())
            self.modified = False
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存文件失败: {str(e)}")
            return False


class DebuggerWidget(QWidget):
    """调试器窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.breakpoints = set()
        self.current_line = -1
        self.variables = {}
        self.call_stack = []

        self._create_ui()

    def _create_ui(self):
        """创建UI"""
        layout = QVBoxLayout(self)

        # 工具栏
        toolbar = QToolBar()

        self.run_action = QAction("运行", self)
        self.run_action.setShortcut("F5")
        toolbar.addAction(self.run_action)

        self.step_over_action = QAction("单步跳过", self)
        self.step_over_action.setShortcut("F10")
        toolbar.addAction(self.step_over_action)

        self.step_into_action = QAction("单步进入", self)
        self.step_into_action.setShortcut("F11")
        toolbar.addAction(self.step_into_action)

        self.continue_action = QAction("继续", self)
        self.continue_action.setShortcut("F8")
        toolbar.addAction(self.continue_action)

        layout.addWidget(toolbar)

        # 调试信息面板
        debug_tabs = QTabWidget()

        # 变量面板
        self.variables_tree = QTreeWidget()
        self.variables_tree.setHeaderLabels(["变量", "值", "类型"])
        debug_tabs.addTab(self.variables_tree, "变量")

        # 调用栈面板
        self.call_stack_tree = QTreeWidget()
        self.call_stack_tree.setHeaderLabels(["函数", "文件", "行号"])
        debug_tabs.addTab(self.call_stack_tree, "调用栈")

        # 断点面板
        self.breakpoints_tree = QTreeWidget()
        self.breakpoints_tree.setHeaderLabels(["文件", "行号", "条件"])
        debug_tabs.addTab(self.breakpoints_tree, "断点")

        layout.addWidget(debug_tabs)

    def update_variables(self, variables: Dict[str, Any]):
        """更新变量"""
        self.variables_tree.clear()

        def add_variable(parent, name, value):
            item = QTreeWidgetItem(parent)
            item.setText(0, str(name))
            item.setText(1, str(value))
            item.setText(2, type(value).__name__)

            if isinstance(value, (dict, list, tuple)):
                if isinstance(value, dict):
                    for k, v in value.items():
                        add_variable(item, k, v)
                else:
                    for i, v in enumerate(value):
                        add_variable(item, i, v)

        for name, value in variables.items():
            add_variable(self.variables_tree.invisibleRootItem(), name, value)

    def update_call_stack(self, stack: List[Dict]):
        """更新调用栈"""
        self.call_stack_tree.clear()

        for frame in stack:
            item = QTreeWidgetItem(self.call_stack_tree)
            item.setText(0, frame["function"])
            item.setText(1, frame["file"])
            item.setText(2, str(frame["line"]))

    def update_breakpoints(self):
        """更新断点"""
        self.breakpoints_tree.clear()

        for bp in sorted(self.breakpoints):
            item = QTreeWidgetItem(self.breakpoints_tree)
            item.setText(0, bp[0])  # 文件
            item.setText(1, str(bp[1]))  # 行号
            item.setText(2, bp[2] if len(bp) > 2 else "")  # 条件


class ScriptEditor(QWidget):
    """脚本编辑器主窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.logger = logging.getLogger("ScriptEditor")
        self._create_ui()

    def _create_ui(self):
        """创建UI"""
        layout = QHBoxLayout(self)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 代码编辑器
        self.editor = CodeEditor()
        splitter.addWidget(self.editor)

        # 调试器
        self.debugger = DebuggerWidget()
        splitter.addWidget(self.debugger)

        # 设置分割器比例
        splitter.setSizes([700, 300])

        layout.addWidget(splitter)

        # 创建工具栏
        self._create_toolbar()

    def _create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar(self)

        # 文件操作
        new_action = QAction("新建", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)

        open_action = QAction("打开", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # 编辑操作
        undo_action = QAction("撤销", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.editor.undo)
        toolbar.addAction(undo_action)

        redo_action = QAction("重做", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        toolbar.addAction(redo_action)

        layout = self.layout()
        layout.setMenuBar(toolbar)

    def new_file(self):
        """新建文件"""
        if self.editor.modified:
            reply = QMessageBox.question(
                self,
                "保存更改",
                "是否保存更改？",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )

            if reply == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.editor.clear()
        self.editor.current_file = None
        self.editor.modified = False

    def open_file(self):
        """打开文件"""
        if self.editor.modified:
            reply = QMessageBox.question(
                self,
                "保存更改",
                "是否保存更改？",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )

            if reply == QMessageBox.StandardButton.Save:
                if not self.save_file():
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        filename, _ = QFileDialog.getOpenFileName(
            self, "打开文件", "", "Python Files (*.py);;All Files (*.*)"
        )

        if filename:
            self.editor.load_file(filename)

    def save_file(self) -> bool:
        """保存文件"""
        if not self.editor.current_file:
            filename, _ = QFileDialog.getSaveFileName(
                self, "保存文件", "", "Python Files (*.py);;All Files (*.*)"
            )

            if not filename:
                return False

            return self.editor.save_file(filename)

        return self.editor.save_file()
