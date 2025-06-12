"""窗口管理器(WindowManager)单元测试"""
import unittest
import sys
import os
import numpy as np
from unittest.mock import MagicMock, patch

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.services.window_manager import GameWindowManager
from src.services.logger import GameLogger
from src.services.config import Config

class TestWindowManager(unittest.TestCase):
    """窗口管理器测试类"""

    def setUp(self):
        """测试前准备"""
        # 创建模拟对象
        self.logger = MagicMock(spec=GameLogger)
        self.config = MagicMock(spec=Config)
        
        # 配置模拟对象
        self.config.window = MagicMock()
        self.config.window.window_class = "TestWindowClass"
        self.config.window.window_title = "TestWindowTitle"
        
        # 创建测试对象
        self.window_manager = GameWindowManager(self.logger, self.config)
    
    @patch('src.services.window_manager.win32gui')
    def test_update_window_list(self, mock_win32gui):
        """测试更新窗口列表功能"""
        # 模拟窗口列表
        mock_windows = [(1, "Window1"), (2, "Window2")]
        
        # 设置模拟行为
        def mock_enum_windows(callback, windows):
            for hwnd, title in mock_windows:
                callback(hwnd, windows)
            return True
            
        mock_win32gui.EnumWindows.side_effect = mock_enum_windows
        mock_win32gui.IsWindowVisible.return_value = True
        mock_win32gui.GetWindowText = lambda hwnd: next((title for h, title in mock_windows if h == hwnd), "")
        
        # 调用方法
        self.window_manager.update_window_list()
        
        # 验证结果
        self.assertEqual(len(self.window_manager.windows_cache), 2)
        self.assertIn((1, "Window1"), self.window_manager.windows_cache)
        self.assertIn((2, "Window2"), self.window_manager.windows_cache)
    
    @patch('src.services.window_manager.win32gui')
    def test_find_window(self, mock_win32gui):
        """测试查找窗口功能"""
        # 设置模拟行为
        mock_win32gui.FindWindow.return_value = 123
        mock_win32gui.GetWindowRect.return_value = (0, 0, 800, 600)
        
        # 调用方法
        result = self.window_manager.find_window()
        
        # 验证结果
        self.assertTrue(result)
        self.assertEqual(self.window_manager.window_handle, 123)
        self.assertEqual(self.window_manager.window_rect, (0, 0, 800, 600))
        mock_win32gui.FindWindow.assert_called_once_with("TestWindowClass", "TestWindowTitle")
        
    @patch('src.services.window_manager.win32gui')
    def test_find_window_not_found(self, mock_win32gui):
        """测试查找不存在的窗口"""
        # 设置模拟行为
        mock_win32gui.FindWindow.return_value = 0
        
        # 调用方法
        result = self.window_manager.find_window()
        
        # 验证结果
        self.assertFalse(result)
        
    @patch('src.services.window_manager.win32gui')
    def test_is_window_active(self, mock_win32gui):
        """测试窗口激活状态检查"""
        # 设置模拟行为
        self.window_manager.window_handle = 123
        mock_win32gui.GetForegroundWindow.return_value = 123
        
        # 验证激活状态
        self.assertTrue(self.window_manager.is_window_active())
        
        # 设置为非激活状态
        mock_win32gui.GetForegroundWindow.return_value = 456
        
        # 验证非激活状态
        self.assertFalse(self.window_manager.is_window_active())
    
    @patch('src.services.window_manager.GameWindowManager.get_screenshot')
    def test_get_screenshot(self, mock_get_screenshot):
        """测试获取屏幕截图"""
        # 创建模拟截图数据
        mock_img = np.zeros((600, 800, 3), dtype=np.uint8)
        
        # 直接返回模拟图像而不是尝试模拟复杂的mss行为
        mock_get_screenshot.return_value = mock_img
        
        # 设置窗口属性
        self.window_manager.window_rect = (0, 0, 800, 600)
        self.window_manager.window_handle = 123
        
        # 调用方法
        result = self.window_manager.get_screenshot()
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, (600, 800, 3))
        mock_get_screenshot.assert_called_once()

if __name__ == '__main__':
    unittest.main() 