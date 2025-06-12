"""
游戏适配器测试
"""
import pytest
from unittest.mock import Mock, patch
import json
from pathlib import Path
from src.core.task_system import Task, TaskStatus
from src.games.game_base import GameBase


class TestGame(GameBase):
    """测试游戏类"""

    def __init__(self):
        super().__init__("TestGame", "test_window_title")
        self._window_handle = None
        self._config = {}

    def find_window(self):
        self._window_handle = 12345
        return True

    def get_window_rect(self):
        return {"left": 0, "top": 0, "width": 800, "height": 600}


@pytest.fixture
def game():
    """创建测试游戏实例"""
    return TestGame()


def test_game_basic(game):
    """测试游戏基本属性"""
    assert game.name == "TestGame"
    assert game.window_title == "test_window_title"


def test_game_window(game):
    """测试游戏窗口操作"""
    # 查找窗口
    assert game.find_window()
    assert game._window_handle == 12345

    # 获取窗口区域
    rect = game.get_window_rect()
    assert rect["width"] == 800
    assert rect["height"] == 600


def test_game_screenshot(game):
    """测试游戏截图"""
    with patch("PIL.ImageGrab.grab") as mock_grab:
        # 模拟截图
        mock_image = Mock()
        mock_image.size = (800, 600)
        mock_grab.return_value = mock_image

        # 获取截图
        screenshot = game.get_screenshot()
        assert screenshot.size == (800, 600)


def test_game_pixel_color(game):
    """测试获取像素颜色"""
    with patch("PIL.ImageGrab.grab") as mock_grab:
        # 模拟图像
        mock_image = Mock()
        mock_image.getpixel.return_value = (255, 0, 0)  # 红色
        mock_grab.return_value = mock_image

        # 获取像素颜色
        color = game.get_pixel_color(100, 100)
        assert color == (255, 0, 0)


def test_game_find_image(game, tmp_path):
    """测试图像查找"""
    # 创建测试图像
    test_image = tmp_path / "test.png"
    test_image.touch()

    with patch("cv2.matchTemplate") as mock_match:
        # 模拟匹配结果
        mock_match.return_value = Mock(max=0.95)  # 95%匹配度

        # 查找图像
        result = game.find_image(str(test_image))
        assert result["confidence"] > 0.9


def test_game_ocr(game):
    """测试文字识别"""
    with patch("easyocr.Reader") as mock_reader:
        # 模拟OCR结果
        mock_reader.return_value.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 30], [0, 30]], "测试文字", 0.95)
        ]

        # 识别文字
        text = game.ocr_text()
        assert "测试文字" in text


def test_game_click(game):
    """测试鼠标点击"""
    with patch("pyautogui.click") as mock_click:
        game.click(100, 100)
        mock_click.assert_called_once_with(x=100, y=100)


def test_game_key_press(game):
    """测试按键操作"""
    with patch("pyautogui.press") as mock_press:
        game.press_key("a")
        mock_press.assert_called_once_with("a")


def test_game_wait_color(game):
    """测试等待颜色"""
    with patch.object(game, "get_pixel_color") as mock_get_color:
        # 模拟颜色变化
        mock_get_color.side_effect = [
            (0, 0, 0),  # 黑色
            (0, 0, 0),  # 黑色
            (255, 0, 0),  # 红色
        ]

        # 等待红色出现
        result = game.wait_for_color(100, 100, (255, 0, 0), timeout=1)
        assert result


def test_game_wait_image(game, tmp_path):
    """测试等待图像"""
    # 创建测试图像
    test_image = tmp_path / "test.png"
    test_image.touch()

    with patch.object(game, "find_image") as mock_find:
        # 模拟图像查找结果
        mock_find.side_effect = [
            {"confidence": 0.5},  # 不匹配
            {"confidence": 0.5},  # 不匹配
            {"confidence": 0.95},  # 匹配
        ]

        # 等待图像出现
        result = game.wait_for_image(str(test_image), timeout=1)
        assert result


def test_game_wait_text(game):
    """测试等待文字"""
    with patch.object(game, "ocr_text") as mock_ocr:
        # 模拟OCR结果
        mock_ocr.side_effect = [
            "",  # 无文字
            "",  # 无文字
            "测试文字",  # 目标文字
        ]

        # 等待文字出现
        result = game.wait_for_text("测试文字", timeout=1)
        assert result


def test_game_task_execution(game):
    """测试游戏任务执行"""
    # 创建测试配置
    config = {
        "actions": [
            {"type": "click", "x": 100, "y": 100},
            {"type": "wait", "duration": 0.1},
            {"type": "key", "key": "space"},
        ]
    }

    # 创建任务
    task = game.create_task(config)
    assert isinstance(task, Task)

    # 执行任务
    with patch("pyautogui.click") as mock_click, patch("pyautogui.press") as mock_press:
        task.execute()

        mock_click.assert_called_once_with(x=100, y=100)
        mock_press.assert_called_once_with("space")
        assert task.status == TaskStatus.COMPLETED


def test_game_config(game, tmp_path):
    """测试游戏配置管理"""
    # 创建配置文件
    config_file = tmp_path / "test_game.json"
    test_config = {
        "resolution": {"width": 1920, "height": 1080},
        "actions": {"click_delay": 0.1, "key_delay": 0.05},
    }
    config_file.write_text(json.dumps(test_config))

    # 加载配置
    game.load_config(str(config_file))
    assert game.get_config() == test_config

    # 修改配置
    test_config["resolution"]["width"] = 1280
    game.save_config(test_config)

    # 验证保存的配置
    saved_config = json.loads(config_file.read_text())
    assert saved_config["resolution"]["width"] == 1280
