"""图像处理器(ImageProcessor)单元测试"""
import unittest
import sys
import os
import numpy as np
import cv2
from unittest.mock import MagicMock, patch, mock_open

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.services.image_processor import ImageProcessor
from src.services.logger import GameLogger
from src.services.config import Config

class TestImageProcessor(unittest.TestCase):
    """图像处理器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟对象
        self.logger = MagicMock(spec=GameLogger)
        self.config = MagicMock(spec=Config)
        
        # 配置模拟对象
        self.config.image_processor = MagicMock()
        self.config.image_processor.template_match_threshold = 0.8
        
        # 创建测试对象
        self.image_processor = ImageProcessor(self.logger, self.config)
        
        # 创建测试图像
        self.test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        # 画一个白色矩形
        cv2.rectangle(self.test_image, (10, 10), (90, 90), (255, 255, 255), -1)
        
        # 创建测试模板
        self.test_template = np.zeros((30, 30, 3), dtype=np.uint8)
        # 画一个白色矩形
        cv2.rectangle(self.test_template, (5, 5), (25, 25), (255, 255, 255), -1)
    
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('cv2.imread')
    def test_load_templates(self, mock_imread, mock_listdir, mock_exists):
        """测试加载模板图像"""
        # 设置模拟行为
        mock_exists.return_value = True
        mock_listdir.return_value = ['template1.png', 'template2.jpg', 'not_image.txt']
        mock_imread.return_value = self.test_template
        
        # 调用方法
        self.image_processor.load_templates('templates_path')
        
        # 验证结果
        self.assertEqual(len(self.image_processor.templates), 2)
        self.assertIn('template1', self.image_processor.templates)
        self.assertIn('template2', self.image_processor.templates)
        self.assertNotIn('not_image', self.image_processor.templates)
        mock_imread.assert_called()
        self.assertEqual(mock_imread.call_count, 2)
        
    @patch('os.path.exists')
    def test_load_templates_dir_not_exists(self, mock_exists):
        """测试加载不存在的模板路径"""
        # 设置模拟行为
        mock_exists.return_value = False
        
        # 验证异常
        with self.assertRaises(FileNotFoundError):
            self.image_processor.load_templates('non_existent_path')
            
    @patch('cv2.matchTemplate')
    def test_match_template(self, mock_match_template):
        """测试模板匹配"""
        # 设置模拟行为
        self.image_processor.templates = {'test_template': self.test_template}
        
        # 模拟匹配结果
        result = np.zeros((71, 71), dtype=np.float32)
        result[30, 30] = 0.9  # 模拟匹配点
        mock_match_template.return_value = result
        
        # 调用方法
        matches = self.image_processor.match_template(self.test_image, 'test_template')
        
        # 验证结果
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], (30, 30))
        mock_match_template.assert_called_once()
        
    def test_match_template_not_found(self):
        """测试模板不存在"""
        # 调用方法
        matches = self.image_processor.match_template(self.test_image, 'non_existent_template')
        
        # 验证结果
        self.assertEqual(len(matches), 0)
        
    @patch('cv2.cvtColor')
    @patch('cv2.inRange')
    @patch('cv2.findContours')
    def test_color_detect(self, mock_find_contours, mock_in_range, mock_cvt_color):
        """测试颜色检测"""
        # 设置模拟行为
        mock_cvt_color.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_in_range.return_value = np.zeros((100, 100), dtype=np.uint8)
        
        # 模拟轮廓检测结果
        contours = [
            np.array([[[10, 10]], [[50, 10]], [[50, 50]], [[10, 50]]], dtype=np.int32),
            np.array([[[60, 60]], [[80, 60]], [[80, 80]], [[60, 80]]], dtype=np.int32)
        ]
        mock_find_contours.return_value = (contours, None)
        
        # 调用方法
        boxes = self.image_processor.color_detect(
            self.test_image, 
            (0, 0, 0), 
            (180, 255, 255)
        )
        
        # 验证结果
        self.assertEqual(len(boxes), 2)
        mock_cvt_color.assert_called_once()
        mock_in_range.assert_called_once()
        mock_find_contours.assert_called_once()
        
    def test_analyze_frame(self):
        """测试分析游戏画面"""
        # 调用方法
        state = self.image_processor.analyze_frame(self.test_image)
        
        # 验证结果
        self.assertIn('timestamp', state)
        self.assertIn('frame_size', state)
        self.assertIn('dominant_colors', state)
        self.assertIn('brightness', state)
        self.assertIn('edges', state)
        self.assertEqual(state['frame_size'], (100, 100))
        self.assertIsInstance(state['brightness'], float)
        
    def test_calculate_brightness(self):
        """测试计算亮度"""
        # 创建测试图像
        white_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        black_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # 调用方法
        white_brightness = self.image_processor._calculate_brightness(white_image)
        black_brightness = self.image_processor._calculate_brightness(black_image)
        
        # 验证结果
        self.assertAlmostEqual(white_brightness, 255.0, delta=1.0)
        self.assertAlmostEqual(black_brightness, 0.0, delta=1.0)

if __name__ == '__main__':
    unittest.main() 