"""ActionExecutor 单元测试"""
import pytest
from unittest.mock import patch, MagicMock, Mock
import win32gui
import win32con
from src.executor.action_executor import ActionExecutor


@pytest.fixture
def executor():
    """创建 ActionExecutor 实例"""
    return ActionExecutor("Test Window")


def test_init(executor):
    """测试初始化"""
    assert executor.window_title == "Test Window"
    assert executor.window_handle is None


@patch("win32gui.FindWindow")
def test_find_window(mock_find_window, executor):
    """测试窗口查找"""
    mock_handle = 12345
    mock_find_window.return_value = mock_handle

    executor._find_window()

    assert executor.window_handle == mock_handle
    mock_find_window.assert_called_once_with(None, "Test Window")


@patch("win32gui.FindWindow")
def test_find_window_not_found(mock_find_window):
    """测试查找不存在的窗口"""
    mock_find_window.return_value = 0
    executor = ActionExecutor("Nonexistent Window")

    # 由于初始化时已经调用过一次，这里重置 mock
    mock_find_window.reset_mock()

    result = executor.find_window()

    assert result is None
    mock_find_window.assert_called_once_with(None, "Nonexistent Window")


@patch("win32gui.GetForegroundWindow")
@patch("win32gui.SetForegroundWindow")
def test_ensure_window_active(mock_set_foreground, mock_get_foreground, executor):
    """测试窗口激活"""
    executor.window_handle = 12345
    mock_get_foreground.return_value = 54321

    result = executor._ensure_window_active()

    assert result is True
    mock_set_foreground.assert_called_once_with(12345)


def test_execute_action_invalid_type(executor):
    """测试无效的动作类型"""
    with pytest.raises(ValueError):
        executor.execute_action("invalid_type", {})


@patch("pyautogui.click")
def test_handle_click(mock_click, executor):
    """测试点击操作"""
    params = {"x": 100, "y": 200}

    result = executor._handle_click(params)

    assert result is True
    mock_click.assert_called_once_with(x=100, y=200)


@patch("pyautogui.doubleClick")
def test_handle_double_click(mock_double_click, executor):
    """测试双击操作"""
    params = {"x": 100, "y": 200}

    result = executor._handle_double_click(params)

    assert result is True
    mock_double_click.assert_called_once_with(x=100, y=200)


@patch("pyautogui.rightClick")
def test_handle_right_click(mock_right_click, executor):
    """测试右键点击操作"""
    params = {"x": 100, "y": 200}

    result = executor._handle_right_click(params)

    assert result is True
    mock_right_click.assert_called_once_with(x=100, y=200)


@patch("pyautogui.moveTo")
def test_handle_move(mock_move_to, executor):
    """测试移动操作"""
    params = {"x": 100, "y": 200}

    result = executor._handle_move(params)

    assert result is True
    mock_move_to.assert_called_once_with(x=100, y=200)


@patch("pyautogui.moveTo")
@patch("pyautogui.dragTo")
def test_handle_drag(mock_drag_to, mock_move_to, executor):
    """测试拖拽操作"""
    params = {"start_x": 100, "start_y": 200, "end_x": 300, "end_y": 400}

    result = executor._handle_drag(params)

    assert result is True
    mock_move_to.assert_called_once_with(x=100, y=200)
    mock_drag_to.assert_called_once_with(x=300, y=400)


@patch("pyautogui.press")
def test_handle_key(mock_press, executor):
    """测试按键操作"""
    params = {"key": "enter"}

    result = executor._handle_key(params)

    assert result is True
    mock_press.assert_called_once_with("enter")


@patch("pyautogui.hotkey")
def test_handle_hotkey(mock_hotkey, executor):
    """测试组合键操作"""
    params = {"keys": ["ctrl", "c"]}

    result = executor._handle_hotkey(params)

    assert result is True
    mock_hotkey.assert_called_once_with("ctrl", "c")


@patch("pyautogui.write")
def test_handle_text(mock_write, executor):
    """测试文本输入操作"""
    params = {"text": "Hello World"}

    result = executor._handle_text(params)

    assert result is True
    mock_write.assert_called_once_with("Hello World")


@patch("win32gui.ShowWindow")
def test_handle_window(mock_show_window, executor):
    """测试窗口操作"""
    executor.window_handle = 12345
    params = {"operation": "maximize"}

    result = executor._handle_window(params)

    assert result is True
    mock_show_window.assert_called_once()


@patch("pyautogui.scroll")
def test_handle_scroll(mock_scroll, executor):
    """测试滚动操作"""
    params = {"clicks": 5}

    result = executor._handle_scroll(params)

    assert result is True
    mock_scroll.assert_called_once_with(5)


@patch("pyautogui.pixel")
def test_get_pixel_color(mock_pixel, executor):
    """测试获取像素颜色"""
    mock_pixel.return_value = (255, 0, 0)

    result = executor.get_pixel_color(100, 200)

    assert result == (255, 0, 0)
    mock_pixel.assert_called_once_with(100, 200)


@patch("pyautogui.screenshot")
def test_search_color(mock_screenshot, executor):
    """测试颜色搜索"""
    # 创建模拟截图
    mock_image = Mock()
    mock_image.size = (100, 100)
    mock_image.getpixel.return_value = (255, 0, 0)
    mock_screenshot.return_value = mock_image

    result = executor.search_color((255, 0, 0))

    assert isinstance(result, tuple)
    assert len(result) == 2
    mock_screenshot.assert_called_once()


def test_execute_action_with_delay(executor):
    """测试带延迟的动作执行"""
    action = {"type": "click", "x": 100, "y": 100, "delay": 0.1}

    with patch("time.sleep") as mock_sleep, patch(
        "win32gui.GetForegroundWindow", return_value=12345
    ), patch("pyautogui.click") as mock_click:
        executor.window_handle = 12345
        executor.execute_action("click", action)
        mock_sleep.assert_called_once_with(0.1)
        mock_click.assert_called_once()


def test_execute_action_with_invalid_delay(executor):
    """测试无效延迟的动作执行"""
    action = {"type": "click", "x": 100, "y": 100, "delay": "invalid"}
    with pytest.raises(ValueError):
        executor.execute_action("click", action)


def test_handle_click_with_error(executor):
    """测试点击操作出错的情况"""
    with patch("pyautogui.click", side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            executor._handle_click({"x": 100, "y": 100})


def test_handle_drag_with_error(executor):
    """测试拖拽操作出错的情况"""
    with patch("pyautogui.moveTo", side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            executor._handle_drag(
                {"start_x": 100, "start_y": 100, "end_x": 200, "end_y": 200}
            )


def test_handle_key_with_error(executor):
    """测试按键操作出错的情况"""
    with patch("pyautogui.press", side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            executor._handle_key({"key": "a"})


def test_handle_hotkey_with_error(executor):
    """测试热键操作出错的情况"""
    with patch("pyautogui.hotkey", side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            executor._handle_hotkey({"keys": ["ctrl", "a"]})


def test_handle_text_with_error(executor):
    """测试文本输入出错的情况"""
    with patch("pyautogui.write", side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            executor._handle_text({"text": "test"})


def test_handle_window_with_error(executor):
    """测试窗口操作出错的情况"""
    executor.window_handle = 12345
    with patch("win32gui.ShowWindow", side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            executor._handle_window({"operation": "minimize"})


def test_handle_scroll_with_error(executor):
    """测试滚动操作出错的情况"""
    with patch("pyautogui.scroll", side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            executor._handle_scroll({"clicks": 100})


def test_get_pixel_color_with_error(executor):
    """测试获取像素颜色出错的情况"""
    with patch("win32gui.GetDC", side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            executor.get_pixel_color(100, 100)


def test_search_color_with_error(executor):
    """测试搜索颜色出错的情况"""
    with patch("win32gui.GetDC", side_effect=Exception("Test error")):
        with pytest.raises(Exception):
            executor.search_color((255, 0, 0), (100, 100, 200, 200))


def test_find_window_with_partial_match(executor):
    """测试使用部分匹配查找窗口"""

    def mock_enum_windows(callback, extra):
        callback(1, extra)

    def mock_get_window_text(hwnd):
        return "Test Window Title"

    def mock_is_window_visible(hwnd):
        return True

    with patch("win32gui.EnumWindows", mock_enum_windows), patch(
        "win32gui.GetWindowText", mock_get_window_text
    ), patch("win32gui.IsWindowVisible", mock_is_window_visible):
        result = executor.find_window_with_partial_match()
        assert result == 1


def test_ensure_window_active_already_active(executor):
    """测试已经激活的窗口"""
    with patch("win32gui.GetForegroundWindow", return_value=123), patch(
        "win32gui.ShowWindow"
    ) as mock_show_window, patch("win32gui.SetForegroundWindow") as mock_set_foreground:
        executor._ensure_window_active()
        mock_show_window.assert_not_called()
        mock_set_foreground.assert_not_called()


def test_handle_window_maximize(executor):
    """测试窗口最大化操作"""
    executor.window_handle = 12345
    with patch("win32gui.ShowWindow") as mock_show_window:
        executor._handle_window({"operation": "maximize"})
        mock_show_window.assert_called_once_with(12345, win32con.SW_MAXIMIZE)


def test_handle_window_minimize(executor):
    """测试窗口最小化操作"""
    executor.window_handle = 12345
    with patch("win32gui.ShowWindow") as mock_show_window:
        executor._handle_window({"operation": "minimize"})
        mock_show_window.assert_called_once_with(12345, win32con.SW_MINIMIZE)


def test_handle_window_restore(executor):
    """测试窗口还原操作"""
    executor.window_handle = 12345
    with patch("win32gui.ShowWindow") as mock_show_window:
        executor._handle_window({"operation": "restore"})
        mock_show_window.assert_called_once_with(12345, win32con.SW_RESTORE)


def test_handle_window_invalid_action(executor):
    """测试无效的窗口操作"""
    with pytest.raises(ValueError):
        executor._handle_window({"operation": "invalid"})


def test_execute_action_with_retry(executor):
    """测试带重试的动作执行"""
    action = {"type": "click", "x": 100, "y": 100, "retry": 2, "retry_interval": 0.1}

    with patch("time.sleep") as mock_sleep, patch(
        "win32gui.GetForegroundWindow", return_value=12345
    ), patch(
        "pyautogui.click", side_effect=[Exception("Error"), Exception("Error"), None]
    ):
        executor.window_handle = 12345
        executor.execute_action("click", action)
        assert mock_sleep.call_count == 2


def test_execute_action_retry_exhausted(executor):
    """测试重试次数用尽的情况"""
    action = {"type": "click", "x": 100, "y": 100, "retry": 2, "retry_interval": 0.1}

    with patch("time.sleep"), patch(
        "win32gui.GetForegroundWindow", return_value=12345
    ), patch("pyautogui.click", side_effect=Exception("Test error")):
        executor.window_handle = 12345
        with pytest.raises(Exception):
            executor.execute_action("click", action)


def test_find_window_with_empty_title(executor):
    """测试空窗口标题的情况"""
    executor.window_title = ""
    with pytest.raises(ValueError):
        executor._find_window()


def test_find_window_with_special_chars(executor):
    """测试包含特殊字符的窗口标题"""
    executor.window_title = "Test!@#$%^&*()"
    with patch("win32gui.FindWindow", return_value=0):
        assert executor._find_window() is None


def test_ensure_window_active_with_invalid_handle(executor):
    """测试无效窗口句柄的激活"""
    executor.window_handle = -1
    assert not executor._ensure_window_active()


def test_ensure_window_active_with_minimized_window(executor):
    """测试最小化窗口的激活"""
    executor.window_handle = 12345
    with patch("win32gui.IsIconic", return_value=True), patch(
        "win32gui.ShowWindow"
    ) as mock_show_window, patch("win32gui.SetForegroundWindow"):
        executor._ensure_window_active()
        mock_show_window.assert_called_once_with(12345, win32con.SW_RESTORE)


def test_handle_click_with_negative_coordinates(executor):
    """测试负坐标点击"""
    with pytest.raises(ValueError):
        executor._handle_click({"x": -100, "y": -100})


def test_handle_click_with_out_of_bounds(executor):
    """测试超出屏幕范围的点击"""
    with patch("pyautogui.size", return_value=(1920, 1080)):
        with pytest.raises(ValueError):
            executor._handle_click({"x": 2000, "y": 2000})


def test_handle_drag_with_same_coordinates(executor):
    """测试起点终点相同的拖拽"""
    with pytest.raises(ValueError):
        executor._handle_drag(
            {"start_x": 100, "start_y": 100, "end_x": 100, "end_y": 100}
        )


def test_handle_hotkey_with_invalid_keys(executor):
    """测试无效的组合键"""
    with pytest.raises(ValueError):
        executor._handle_hotkey({"keys": []})
    with pytest.raises(ValueError):
        executor._handle_hotkey({"keys": ["invalid_key"]})


def test_handle_text_with_empty_string(executor):
    """测试空字符串输入"""
    with pytest.raises(ValueError):
        executor._handle_text({"text": ""})


def test_handle_window_with_hidden_window(executor):
    """测试隐藏窗口的操作"""
    executor.window_handle = 12345
    with patch("win32gui.IsWindowVisible", return_value=False):
        with pytest.raises(Exception):
            executor._handle_window({"operation": "maximize"})


def test_handle_window_multiple_operations(executor):
    """测试连续的窗口操作"""
    executor.window_handle = 12345
    with patch("win32gui.ShowWindow") as mock_show_window:
        executor._handle_window({"operation": "minimize"})
        executor._handle_window({"operation": "maximize"})
        executor._handle_window({"operation": "restore"})
        assert mock_show_window.call_count == 3


def test_execute_action_with_missing_params(executor):
    """测试缺少必要参数的动作执行"""
    with pytest.raises(ValueError):
        executor.execute_action("click", {})
    with pytest.raises(ValueError):
        executor.execute_action("drag", {"start_x": 100})


def test_execute_action_with_invalid_retry_params(executor):
    """测试无效的重试参数"""
    action = {"type": "click", "x": 100, "y": 100, "retry": -1, "retry_interval": -0.1}
    with pytest.raises(ValueError):
        executor.execute_action("click", action)


def test_execute_action_with_window_not_found(executor):
    """测试窗口未找到时的动作执行"""
    executor.window_handle = None
    with pytest.raises(Exception):
        executor.execute_action("click", {"x": 100, "y": 100})


def test_handle_scroll_with_zero_clicks(executor):
    """测试滚动值为0的情况"""
    with pytest.raises(ValueError):
        executor._handle_scroll({"clicks": 0})


def test_handle_scroll_with_large_value(executor):
    """测试超大滚动值"""
    with patch("pyautogui.scroll") as mock_scroll:
        executor._handle_scroll({"clicks": 1000})
        mock_scroll.assert_called_once_with(1000)
