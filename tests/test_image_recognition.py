"""ImageRecognition 单元测试"""
import pytest
import numpy as np
import cv2
from PIL import Image
from unittest.mock import patch, MagicMock
from ..src.image_recognition import (
    load_image,
    find_template,
    find_text,
    find_color,
    find_motion,
    ImageRecognition,
)


@pytest.fixture
def image_recognition():
    """创建 ImageRecognition 实例"""
    return ImageRecognition()


@pytest.fixture
def sample_image():
    """创建示例图像"""
    # 创建一个 100x100 的黑色图像，中间有一个白色方块
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[40:60, 40:60] = [255, 255, 255]  # 白色方块
    return img


@pytest.fixture
def mock_image():
    """创建模拟图像"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[30:70, 30:70] = [255, 255, 255]  # 白色方块
    return Image.fromarray(img)


@pytest.fixture
def mock_template():
    """创建模拟模板图像"""
    img = np.zeros((20, 20, 3), dtype=np.uint8)
    img[:, :] = [255, 255, 255]  # 全白色
    return Image.fromarray(img)


def test_init(image_recognition):
    """测试初始化"""
    assert image_recognition.last_image is None
    assert image_recognition.templates == {}


def test_load_template(image_recognition, sample_image):
    """测试加载模板"""
    image_recognition.load_template("test", sample_image)
    assert "test" in image_recognition.templates
    assert isinstance(image_recognition.templates["test"], np.ndarray)


def test_find_template(image_recognition, sample_image):
    """测试查找模板"""
    # 创建一个包含目标的大图
    large_image = np.zeros((200, 200, 3), dtype=np.uint8)
    large_image[50:150, 50:150] = sample_image

    # 加载模板
    image_recognition.load_template("test", sample_image)

    # 查找模板
    result = image_recognition.find_template("test", large_image)
    assert result is not None
    x, y = result
    assert 45 <= x <= 55
    assert 45 <= y <= 55


def test_find_template_not_found(image_recognition, sample_image):
    """测试找不到模板的情况"""
    # 创建一个不包含目标的图像
    different_image = np.zeros((200, 200, 3), dtype=np.uint8)

    # 加载模板
    image_recognition.load_template("test", sample_image)

    # 查找模板
    result = image_recognition.find_template("test", different_image)
    assert result is None


def test_find_template_invalid_name(image_recognition, sample_image):
    """测试使用无效的模板名称"""
    result = image_recognition.find_template("nonexistent", sample_image)
    assert result is None


def test_remove_template(image_recognition, sample_image):
    """测试移除模板"""
    image_recognition.load_template("test", sample_image)
    assert "test" in image_recognition.templates

    image_recognition.remove_template("test")
    assert "test" not in image_recognition.templates


def test_clear_templates(image_recognition, sample_image):
    """测试清空所有模板"""
    image_recognition.load_template("test1", sample_image)
    image_recognition.load_template("test2", sample_image)
    assert len(image_recognition.templates) == 2

    image_recognition.clear_templates()
    assert len(image_recognition.templates) == 0


@pytest.mark.skip(reason="需要安装 Tesseract OCR")
def test_find_text(image_recognition, sample_image):
    """测试文字识别"""
    # 创建一个包含文字的图像
    text_image = np.zeros((100, 300, 3), dtype=np.uint8)
    cv2.putText(
        text_image, "Hello", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )

    result = image_recognition.find_text(text_image)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.skip(reason="需要安装 Tesseract OCR")
def test_find_text_no_text(image_recognition):
    """测试在没有文字的图像中识别"""
    # 创建一个空白图像
    blank_image = np.zeros((100, 100, 3), dtype=np.uint8)

    result = image_recognition.find_text(blank_image)
    assert isinstance(result, list)
    assert len(result) == 0


@pytest.mark.skip(reason="需要安装 Tesseract OCR")
def test_find_text_with_region(image_recognition, sample_image):
    """测试在指定区域内识别文字"""
    # 创建一个包含文字的图像
    text_image = np.zeros((200, 200, 3), dtype=np.uint8)
    cv2.putText(
        text_image, "Hello", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )
    cv2.putText(
        text_image, "World", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )

    # 只在上半部分识别
    result = image_recognition.find_text(text_image, region=(0, 0, 200, 100))
    assert isinstance(result, list)
    assert any("hello" in text.lower() for text in result)
    assert not any("world" in text.lower() for text in result)


def test_load_image_success():
    """测试成功加载图像"""
    with patch("PIL.Image.open") as mock_open:
        mock_open.return_value = Image.new("RGB", (100, 100))
        result = load_image("test.png")
        assert result is not None
        mock_open.assert_called_once_with("test.png")


def test_load_image_file_not_found():
    """测试加载不存在的图像"""
    with patch("PIL.Image.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            load_image("nonexistent.png")


def test_load_image_invalid_format():
    """测试加载无效格式的图像"""
    with patch("PIL.Image.open", side_effect=IOError):
        with pytest.raises(IOError):
            load_image("invalid.xyz")


def test_find_template_exact_match(mock_image, mock_template):
    """测试完全匹配的模板"""
    result = find_template(mock_image, mock_template, threshold=0.8)
    assert result is not None
    assert len(result) == 2
    assert isinstance(result[0], int)
    assert isinstance(result[1], int)


def test_find_template_no_match(mock_image):
    """测试没有匹配的模板"""
    black_template = Image.fromarray(np.zeros((20, 20, 3), dtype=np.uint8))
    result = find_template(mock_image, black_template, threshold=0.9)
    assert result is None


def test_find_template_multiple_matches(mock_image):
    """测试多个匹配的情况"""
    # 创建一个包含多个白色方块的图像
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    img[30:70, 30:70] = [255, 255, 255]
    img[30:70, 130:170] = [255, 255, 255]
    source = Image.fromarray(img)

    template = Image.fromarray(np.ones((20, 20, 3), dtype=np.uint8) * 255)
    result = find_template(source, template, threshold=0.8)
    assert result is not None


def test_find_text_success():
    """测试成功识别文本"""
    with patch("pytesseract.image_to_string") as mock_ocr:
        mock_ocr.return_value = "Test Text"
        result = find_text(Image.new("RGB", (100, 100)))
        assert result == "Test Text"


def test_find_text_empty():
    """测试空白图像的文本识别"""
    with patch("pytesseract.image_to_string") as mock_ocr:
        mock_ocr.return_value = ""
        result = find_text(Image.new("RGB", (100, 100)))
        assert result == ""


def test_find_text_error():
    """测试文本识别错误"""
    with patch("pytesseract.image_to_string", side_effect=Exception("OCR Error")):
        with pytest.raises(Exception):
            find_text(Image.new("RGB", (100, 100)))


def test_find_color_exact_match(mock_image):
    """测试精确的颜色匹配"""
    result = find_color(mock_image, (255, 255, 255), tolerance=0)
    assert result is not None
    assert len(result) == 2
    assert result[0] >= 30 and result[0] < 70
    assert result[1] >= 30 and result[1] < 70


def test_find_color_with_tolerance(mock_image):
    """测试带容差的颜色匹配"""
    result = find_color(mock_image, (250, 250, 250), tolerance=10)
    assert result is not None
    assert len(result) == 2


def test_find_color_no_match(mock_image):
    """测试没有匹配颜色"""
    result = find_color(mock_image, (0, 255, 0), tolerance=0)
    assert result is None


def test_find_color_invalid_color():
    """测试无效的颜色值"""
    with pytest.raises(ValueError):
        find_color(Image.new("RGB", (100, 100)), (256, 0, 0))
    with pytest.raises(ValueError):
        find_color(Image.new("RGB", (100, 100)), (-1, 0, 0))


def test_find_motion_significant_change():
    """测试显著的运动变化"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2[40:60, 40:60] = 255  # 添加一个运动区域

    result = find_motion(Image.fromarray(img1), Image.fromarray(img2), threshold=0.1)
    assert result is not None
    assert len(result) == 4


def test_find_motion_no_change():
    """测试没有运动变化"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    result = find_motion(Image.fromarray(img), Image.fromarray(img), threshold=0.1)
    assert result is None


def test_find_motion_size_mismatch():
    """测试图像尺寸不匹配"""
    img1 = Image.new("RGB", (100, 100))
    img2 = Image.new("RGB", (200, 200))
    with pytest.raises(ValueError):
        find_motion(img1, img2, threshold=0.1)


def test_find_motion_invalid_threshold():
    """测试无效的阈值"""
    img = Image.new("RGB", (100, 100))
    with pytest.raises(ValueError):
        find_motion(img, img, threshold=-0.1)
    with pytest.raises(ValueError):
        find_motion(img, img, threshold=1.1)
