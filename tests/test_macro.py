"""
宏录制和播放测试
"""
import pytest
from unittest.mock import Mock, patch
from ..src.macro.macro_recorder import MacroRecorder
from ..src.macro.macro_player import MacroPlayer
from ..src.macro.macro_editor import MacroEditor


@pytest.fixture
def recorder():
    """创建宏录制器实例"""
    return MacroRecorder()


@pytest.fixture
def player():
    """创建宏播放器实例"""
    return MacroPlayer()


@pytest.fixture
def editor():
    """创建宏编辑器实例"""
    return MacroEditor()


def test_recorder_start_stop(recorder):
    """测试宏录制器的开始和停止"""
    assert not recorder.is_recording

    recorder.start()
    assert recorder.is_recording

    recorder.stop()
    assert not recorder.is_recording


def test_recorder_events(recorder):
    """测试宏事件记录"""
    recorder.start()

    # 模拟鼠标事件
    recorder._on_mouse_event(100, 200, "click")
    # 模拟键盘事件
    recorder._on_keyboard_event("a", "press")

    recorder.stop()

    events = recorder.events
    assert len(events) == 2

    mouse_event = events[0]
    assert mouse_event.type == "MOUSE"
    assert mouse_event.data["x"] == 100
    assert mouse_event.data["y"] == 200
    assert mouse_event.data["action"] == "click"

    keyboard_event = events[1]
    assert keyboard_event.type == "KEYBOARD"
    assert keyboard_event.data["key"] == "a"
    assert keyboard_event.data["action"] == "press"


def test_player_load_events(player):
    """测试宏事件加载"""
    events = [
        Mock(type="MOUSE", data={"x": 100, "y": 200, "action": "click"}),
        Mock(type="KEYBOARD", data={"key": "a", "action": "press"}),
    ]

    player.load_events(events)
    assert len(player.events) == 2


def test_player_start_stop(player):
    """测试宏播放器的开始和停止"""
    events = [Mock(type="MOUSE", data={"x": 100, "y": 200, "action": "click"})]
    player.load_events(events)

    assert player.status == "STOPPED"

    player.start()
    assert player.status == "PLAYING"

    player.stop()
    assert player.status == "STOPPED"


def test_player_speed(player):
    """测试宏播放速度调整"""
    player.set_speed(2.0)
    assert player.speed == 2.0

    player.set_speed(0.5)
    assert player.speed == 0.5


def test_editor_load_save(editor, tmp_path):
    """测试宏编辑器的加载和保存"""
    # 创建测试宏文件
    macro_file = tmp_path / "test.macro"
    macro_file.write_text(
        '{"events": [{"type": "MOUSE", "data": {"x": 100, "y": 200}}]}'
    )

    # 加载宏
    editor.load_macro(str(macro_file))
    assert len(editor.events) == 1

    # 修改事件
    editor.events[0].data["x"] = 300

    # 保存宏
    save_file = tmp_path / "save.macro"
    editor.save_macro(str(save_file))

    # 验证保存的内容
    saved_content = save_file.read_text()
    assert '"x": 300' in saved_content


def test_editor_insert_event(editor):
    """测试插入事件"""
    event = Mock(type="MOUSE", data={"x": 100, "y": 200})
    editor.insert_event(0, event)
    assert len(editor.events) == 1
    assert editor.events[0] == event


def test_editor_delete_event(editor):
    """测试删除事件"""
    event1 = Mock(type="MOUSE", data={"x": 100, "y": 200})
    event2 = Mock(type="KEYBOARD", data={"key": "a"})

    editor.insert_event(0, event1)
    editor.insert_event(1, event2)

    editor.delete_event(0)
    assert len(editor.events) == 1
    assert editor.events[0] == event2


def test_editor_modify_event(editor):
    """测试修改事件"""
    event = Mock(type="MOUSE", data={"x": 100, "y": 200})
    editor.insert_event(0, event)

    editor.modify_event(0, {"x": 300, "y": 400})
    assert editor.events[0].data["x"] == 300
    assert editor.events[0].data["y"] == 400
