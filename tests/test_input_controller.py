"""InputController 单元测试"""
import pytest
from unittest.mock import patch, MagicMock
from src.input_controller import InputController


@pytest.fixture
def input_controller():
    """创建 InputController 实例"""
    return InputController()


def test_init(input_controller):
    """测试初始化"""
    assert input_controller.last_position == (0, 0)
    assert input_controller.is_pressed == {}


@patch("pyautogui.moveTo")
def test_move_mouse(mock_move, input_controller):
    """测试移动鼠标"""
    input_controller.move_mouse(100, 200)
    mock_move.assert_called_once_with(100, 200)
    assert input_controller.last_position == (100, 200)


@patch("pyautogui.click")
def test_click(mock_click, input_controller):
    """测试点击"""
    input_controller.click()
    mock_click.assert_called_once_with()


@patch("pyautogui.doubleClick")
def test_double_click(mock_double_click, input_controller):
    """测试双击"""
    input_controller.double_click()
    mock_double_click.assert_called_once_with()


@patch("pyautogui.rightClick")
def test_right_click(mock_right_click, input_controller):
    """测试右键点击"""
    input_controller.right_click()
    mock_right_click.assert_called_once_with()


@patch("pyautogui.dragTo")
def test_drag_mouse(mock_drag, input_controller):
    """测试拖拽鼠标"""
    input_controller.drag_mouse(100, 200)
    mock_drag.assert_called_once_with(100, 200)
    assert input_controller.last_position == (100, 200)


@patch("keyboard.press")
def test_press_key(mock_press, input_controller):
    """测试按下按键"""
    input_controller.press_key("a")
    mock_press.assert_called_once_with("a")
    assert input_controller.is_pressed["a"] is True


@patch("keyboard.release")
def test_release_key(mock_release, input_controller):
    """测试释放按键"""
    input_controller.is_pressed["a"] = True
    input_controller.release_key("a")
    mock_release.assert_called_once_with("a")
    assert "a" not in input_controller.is_pressed


@patch("keyboard.press")
@patch("keyboard.release")
def test_type_text(mock_release, mock_press, input_controller):
    """测试输入文本"""
    input_controller.type_text("hello")
    assert mock_press.call_count == 5
    assert mock_release.call_count == 5


@patch("keyboard.press")
@patch("keyboard.release")
def test_hotkey(mock_release, mock_press, input_controller):
    """测试组合键"""
    input_controller.hotkey(["ctrl", "a"])
    assert mock_press.call_count == 2
    assert mock_release.call_count == 2


@patch("pyautogui.scroll")
def test_scroll(mock_scroll, input_controller):
    """测试滚动"""
    input_controller.scroll(10)
    mock_scroll.assert_called_once_with(10)


def test_is_key_pressed(input_controller):
    """测试检查按键状态"""
    input_controller.is_pressed["a"] = True
    assert input_controller.is_key_pressed("a") is True
    assert input_controller.is_key_pressed("b") is False


def test_clear_pressed_keys(input_controller):
    """测试清除所有按键状态"""
    input_controller.is_pressed = {"a": True, "b": True}
    input_controller.clear_pressed_keys()
    assert len(input_controller.is_pressed) == 0
