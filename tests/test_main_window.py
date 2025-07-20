"""
主窗口单元测试
"""
import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ..src.gui.main_window import MainWindow


@pytest.fixture
def app():
    """创建QApplication实例"""
    app = QApplication(sys.argv)
    yield app
    app.quit()


@pytest.fixture
def window(app):
    """创建MainWindow实例"""
    window = MainWindow()
    yield window
    window.close()


def test_window_title(window):
    """测试窗口标题"""
    assert window.windowTitle() == "游戏自动化工具"


def test_window_size(window):
    """测试窗口大小"""
    assert window.minimumSize().width() >= 1200
    assert window.minimumSize().height() >= 800


def test_control_panel(window):
    """测试控制面板"""
    # 测试游戏选择下拉框
    assert window.game_combo is not None

    # 测试开始/停止按钮
    assert window.start_button is not None
    assert window.stop_button is not None

    # 测试宏录制/播放按钮
    assert window.record_button is not None
    assert window.play_button is not None


def test_edit_panel(window):
    """测试编辑面板"""
    # 测试脚本编辑器
    assert window.script_editor is not None

    # 测试宏编辑器
    assert window.macro_tree is not None
    assert window.macro_tree.columnCount() == 3

    # 测试配置编辑器
    assert window.config_editor is not None


def test_status_panel(window):
    """测试状态面板"""
    # 测试CPU标签
    assert window.cpu_label is not None
    assert window.cpu_label.text() == "CPU: 0%"

    # 测试内存标签
    assert window.memory_label is not None
    assert window.memory_label.text() == "内存: 0MB"

    # 测试FPS标签
    assert window.fps_label is not None
    assert window.fps_label.text() == "FPS: 0"


def test_project_browser(window):
    """测试项目浏览器"""
    browser = window.findChild(QTreeWidget)
    assert browser is not None
    assert browser.headerLabels() == ["项目文件"]


def test_macro_recording(window):
    """测试宏录制"""
    # 测试开始录制
    window.record_button.click()
    assert window.macro_recorder.is_recording
    assert window.record_button.text() == "停止录制"

    # 测试停止录制
    window.record_button.click()
    assert not window.macro_recorder.is_recording
    assert window.record_button.text() == "录制"


def test_code_formatting(window):
    """测试代码格式化"""
    # 设置测试代码
    test_code = "def test():\n  return True"
    window.script_editor.setPlainText(test_code)

    # 测试格式化
    window.code_formatter.format_code = lambda x: "def test():\n    return True"
    window._on_format_code()

    assert window.script_editor.toPlainText() == "def test():\n    return True"


def test_code_checking(window, qtbot):
    """测试代码检查"""
    # 设置测试代码
    test_code = "def test():\nreturn True"
    window.script_editor.setPlainText(test_code)

    # 模拟语法错误
    window.code_formatter.check_syntax = lambda x: [
        {"line": 2, "message": "IndentationError"}
    ]

    # 点击检查按钮并等待消息框
    with qtbot.waitSignal(window.findChild(QMessageBox).finished, timeout=1000):
        window._on_check_code()
