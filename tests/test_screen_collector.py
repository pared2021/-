"""Screen Collector 测试模块"""
import os
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from PIL import Image

from ..src.collector.screen_collector import ScreenCollector
from ..src.utils.image_recognition import ImageRecognition


class TestScreenCollector:
    """Screen Collector 测试类"""

    @pytest.fixture
    def screen_collector(self):
        """创建 ScreenCollector 实例"""
        return ScreenCollector()

    @pytest.fixture
    def mock_image(self):
        """创建模拟图像"""
        return Image.new("RGB", (100, 100), color="white")

    def test_capture(self, screen_collector):
        """测试屏幕截图功能"""
        with patch("PIL.ImageGrab.grab") as mock_grab:
            mock_grab.return_value = Image.new("RGB", (800, 600))
            image = screen_collector.capture()
            assert image is not None
            assert isinstance(image, Image.Image)
            mock_grab.assert_called_once()

    def test_capture_with_region(self, screen_collector):
        """测试指定区域的屏幕截图功能"""
        region = (0, 0, 100, 100)
        with patch("PIL.ImageGrab.grab") as mock_grab:
            mock_grab.return_value = Image.new("RGB", (100, 100))
            image = screen_collector.capture(region)
            assert image is not None
            assert isinstance(image, Image.Image)
            mock_grab.assert_called_once_with(bbox=region)

    def test_capture_with_invalid_region(self, screen_collector):
        """测试无效区域参数的处理"""
        invalid_regions = [
            (-1, 0, 100, 100),
            (0, -1, 100, 100),
            (0, 0, -1, 100),
            (0, 0, 100, -1),
            (100, 0, 0, 100),
            (0, 100, 100, 0),
        ]
        for region in invalid_regions:
            with pytest.raises(ValueError):
                screen_collector.capture(region)

    def test_analyze_screen_with_no_image(self, screen_collector):
        """测试无图像时的分析处理"""
        with pytest.raises(ValueError):
            screen_collector.analyze_screen()

    def test_analyze_screen_with_corrupted_image(self, screen_collector):
        """测试损坏图像的分析处理"""
        with patch("PIL.Image.open") as mock_open:
            mock_open.side_effect = IOError("Corrupted image")
            with pytest.raises(IOError):
                screen_collector.analyze_screen("corrupted.png")

    def test_detect_buttons(self, screen_collector, mock_image):
        """测试按钮检测功能"""
        with patch.object(ImageRecognition, "find_buttons") as mock_find:
            mock_find.return_value = [(10, 10, 50, 30)]
            buttons = screen_collector.detect_buttons(mock_image)
            assert len(buttons) == 1
            assert buttons[0] == (10, 10, 50, 30)

    def test_detect_icons(self, screen_collector, mock_image):
        """测试图标检测功能"""
        with patch.object(ImageRecognition, "find_icons") as mock_find:
            mock_find.return_value = [(20, 20, 40, 40)]
            icons = screen_collector.detect_icons(mock_image)
            assert len(icons) == 1
            assert icons[0] == (20, 20, 40, 40)

    def test_detect_icons_with_low_confidence(self, screen_collector, mock_image):
        """测试低置信度的图标检测"""
        with patch.object(ImageRecognition, "find_icons") as mock_find:
            mock_find.return_value = []
            icons = screen_collector.detect_icons(mock_image, confidence=0.1)
            assert len(icons) == 0

    def test_detect_progress_bars(self, screen_collector, mock_image):
        """测试进度条检测功能"""
        with patch.object(ImageRecognition, "find_progress_bars") as mock_find:
            mock_find.return_value = [(30, 30, 70, 35)]
            bars = screen_collector.detect_progress_bars(mock_image)
            assert len(bars) == 1
            assert bars[0] == (30, 30, 70, 35)

    def test_detect_progress_bars_with_noise(self, screen_collector, mock_image):
        """测试有噪声时的进度条检测"""
        noisy_image = Image.new("RGB", (100, 100))
        # 添加随机噪声
        pixels = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        noisy_image.putdata([tuple(p) for p in pixels.reshape(-1, 3)])

        with patch.object(ImageRecognition, "find_progress_bars") as mock_find:
            mock_find.return_value = []  # 在有噪声的情况下可能检测不到进度条
            bars = screen_collector.detect_progress_bars(noisy_image)
            assert len(bars) == 0

    def test_save_screenshot(self, screen_collector, mock_image, tmp_path):
        """测试截图保存功能"""
        filename = os.path.join(tmp_path, "test_screenshot.png")
        with patch("PIL.Image.Image.save") as mock_save:
            screen_collector.save_screenshot(mock_image, filename)
            mock_save.assert_called_once_with(filename)

    def test_load_template(self, screen_collector, tmp_path):
        """测试模板加载功能"""
        # 创建测试模板文件
        template_path = os.path.join(tmp_path, "test_template.png")
        test_image = Image.new("RGB", (50, 50))
        test_image.save(template_path)

        template = screen_collector.load_template(template_path)
        assert template is not None
        assert isinstance(template, Image.Image)
        assert template.size == (50, 50)

    def test_load_invalid_template(self, screen_collector):
        """测试加载无效模板的处理"""
        with pytest.raises(FileNotFoundError):
            screen_collector.load_template("nonexistent_template.png")

    def test_match_template(self, screen_collector, mock_image):
        """测试模板匹配功能"""
        template = Image.new("RGB", (20, 20))
        with patch.object(ImageRecognition, "match_template") as mock_match:
            mock_match.return_value = [(25, 25)]
            matches = screen_collector.match_template(mock_image, template)
            assert len(matches) == 1
            assert matches[0] == (25, 25)

    def test_match_template_with_threshold(self, screen_collector, mock_image):
        """测试带阈值的模板匹配"""
        template = Image.new("RGB", (20, 20))
        with patch.object(ImageRecognition, "match_template") as mock_match:
            mock_match.return_value = []  # 高阈值可能导致没有匹配
            matches = screen_collector.match_template(
                mock_image, template, threshold=0.9
            )
            assert len(matches) == 0

    def test_get_screen_text(self, screen_collector, mock_image):
        """测试屏幕文本识别功能"""
        with patch.object(ImageRecognition, "extract_text") as mock_extract:
            mock_extract.return_value = "Test Text"
            text = screen_collector.get_screen_text(mock_image)
            assert text == "Test Text"

    def test_get_screen_text_with_region(self, screen_collector, mock_image):
        """测试指定区域的文本识别"""
        region = (10, 10, 50, 50)
        with patch.object(ImageRecognition, "extract_text") as mock_extract:
            mock_extract.return_value = "Region Text"
            text = screen_collector.get_screen_text(mock_image, region)
            assert text == "Region Text"
            # 验证调用时使用了正确的区域
            mock_extract.assert_called_with(mock_image.crop(region))

    def test_get_screen_text_empty(self, screen_collector, mock_image):
        """测试空文本的识别处理"""
        with patch.object(ImageRecognition, "extract_text") as mock_extract:
            mock_extract.return_value = ""
            text = screen_collector.get_screen_text(mock_image)
            assert text == ""

    def test_get_pixel_color(self, screen_collector, mock_image):
        """测试像素颜色获取功能"""
        with patch.object(Image.Image, "getpixel") as mock_getpixel:
            mock_getpixel.return_value = (255, 255, 255)
            color = screen_collector.get_pixel_color(mock_image, 50, 50)
            assert color == (255, 255, 255)
            mock_getpixel.assert_called_with((50, 50))

    def test_get_pixel_color_invalid_coordinates(self, screen_collector, mock_image):
        """测试无效坐标的像素颜色获取"""
        invalid_coords = [(-1, 50), (50, -1), (100, 50), (50, 100)]
        for x, y in invalid_coords:
            with pytest.raises(ValueError):
                screen_collector.get_pixel_color(mock_image, x, y)

    def test_get_pixel_color_no_image(self, screen_collector):
        """测试无图像时的像素颜色获取"""
        with pytest.raises(ValueError):
            screen_collector.get_pixel_color(None, 50, 50)
